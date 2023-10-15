import cv2
import mediapipe as mp
import time
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import mouse
import math

# Initialize the camera capture
cap = cv2.VideoCapture(0)

# Initialize MediaPipe hands module
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Initialize audio devices for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Initialize previous and current time for frame rate calculation
pTime = 0
cTime = 0

def rescale_frame(frame, scale):
    # Rescale the frame to the desired dimensions
    width = 1920
    height = 1000
    dimensions = (width, height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)

while True:
    # Initialize finger variable
    finger = 0

    # Read a frame from the camera
    success, imgs = cap.read()

    # Rescale the frame
    img = rescale_frame(imgs, 2)

    # Convert the frame to RGB format
    imgRBG = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process hand landmarks
    results = hands.process(imgRBG)
    
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                if id == 8:
                    h, w, c = img.shape
                    icx, icy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (icx, icy), 15, (255, 0, 0), cv2.FILLED)
                if id == 4:
                    h, w, c = img.shape
                    tcx, tcy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (tcx, tcy), 15, (0, 255, 0), cv2.FILLED)
            
            kx = icx - tcx
            ky = icy - tcy
            squared_x = kx ** 2
            squared_y = ky ** 2
            hypotenuse = int(math.sqrt(squared_x + squared_y))
            print(hypotenuse)

            if hypotenuse >= 100:
                position = mouse.get_position()
                x = position[0]
                y = position[1]
                mouse.move(icx, tcy)
            elif hypotenuse < 100:
                position = mouse.get_position()
                x = position[0]
                y = position[1]
                mouse.drag(x, y, icx, tcy)
            
            # Draw hand landmarks and connections
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # Calculate and display the frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"fps {str(int(fps))}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    # Display the processed frame
    cv2.imshow("image", img)

    # Exit the loop with 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()