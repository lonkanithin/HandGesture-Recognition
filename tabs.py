import cv2
from cvzone.HandTrackingModule import HandDetector
import pygetwindow as gw
from keras import models
import sys


def run_tabs():
    # Load the model
    try:
        new_model = models.load_model("C:\\Users\91812\Downloads\gesture_model.h5")
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit()

    # Parameters
    width = 720
    gestureThreshold = 150

    # Camera Setup
    cap = cv2.VideoCapture(0)
    cap.set(3, width)

    # Hand Detector
    detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

    # List to keep track of minimized windows
    minimized_windows = []

    # Open the output file for writing
    output_file = open('output.txt', 'w')

    while True:
        # Get image frame
        success, img = cap.read()
        if not success:
            print("Failed to capture image")
            continue

        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Find the hand and its landmarks
        try:
            hands, img = detectorHand.findHands(imgRGB)
        except Exception as e:
            print(f"Error processing image: {e}")
            continue

        if hands:  # If hand is detected
            hand = hands[0]
            cx, cy = hand["center"]
            lmList = hand["lmList"]  # List of 21 Landmark points
            fingers = detectorHand.fingersUp(hand)  # List of which fingers are up

            if cy <= gestureThreshold:  # If hand is at the height of the face
                # If index finger and thumb are up (pinch gesture), minimize the active window
                if fingers == [1, 0, 0, 0, 1]:
                    active_window = gw.getActiveWindow()
                    if active_window is not None and active_window not in minimized_windows:
                        active_window.minimize()
                        minimized_windows.append(active_window)
                        output_file.write("0\n")  # Write 0 to indicate minimize

                # If all fingers are up (open palm), close the active window
                elif fingers == [0, 1, 0, 0, 1]:
                    active_window = gw.getActiveWindow()
                    if active_window is not None:
                        active_window.close()
                        output_file.write("1\n")  # Write 1 to indicate close

                # If index and middle fingers are up (V sign), restore down the last minimized window
                elif fingers == [1, 1, 0, 0, 0]:
                    if minimized_windows:
                        last_minimized = minimized_windows.pop()
                        last_minimized.restore()
                        output_file.write("2\n")  # Write 2 to indicate restore

                # If thumb and index finger are up (OK sign), maximize the active window
                elif fingers == [1, 1, 0, 0, 1]:
                    active_window = gw. getActiveWindow()
                    if active_window is  not None:
                        active_window.maximize()
                        output_file.write("3\n")  # Write 3 to indicate maximize

        cv2.imshow("Camera", img)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    # Release the camera and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

    # Close the output file
    output_file.close()
     
