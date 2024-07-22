import cv2
import mediapipe as mp
import pyautogui
import time
from keras import models
import sys

def run_test():
    try:
        new_model = models.load_model(r"C:\Users\91812\Downloads\gesture_model.h5")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit()

    mute_state = False

    def record_action(action):
        with open('output.txt', 'a') as output_file:
            output_file.write(action + "\n")

    def count_fingers(lst):
        cnt = 0

        thresh = (lst.landmark[0].y * 100 - lst.landmark[9].y * 100) / 2

        if (lst.landmark[5].y * 100 - lst.landmark[8].y * 100) > thresh:
            cnt += 1

        if (lst.landmark[9].y * 100 - lst.landmark[12].y * 100) > thresh:
            cnt += 1

        if (lst.landmark[13].y * 100 - lst.landmark[16].y * 100) > thresh:
            cnt += 1

        if (lst.landmark[17].y * 100 - lst.landmark[20].y * 100) > thresh:
            cnt += 1

        if (lst.landmark[5].x * 100 - lst.landmark[4].x * 100) > 6:
            cnt += 1

        return cnt

    cap = cv2.VideoCapture(0)

    drawing = mp.solutions.drawing_utils
    hands = mp.solutions.hands.Hands(max_num_hands=1)
    hand_obj = hands

    start_init = False
    prev = -1

    try:
        while True:
            _, frm = cap.read()
            frm = cv2.flip(frm, 1)

            res = hand_obj.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

            if res.multi_hand_landmarks:
                hand_keyPoints = res.multi_hand_landmarks[0]
                cnt = count_fingers(hand_keyPoints)

                if not (prev == cnt):
                    if not start_init:
                        start_time = time.time()
                        start_init = True
                    elif (time.time() - start_time) > 0.1:
                        if cnt == 1:
                            pyautogui.press("right")
                            record_action("forward")
                        elif cnt == 2:
                            pyautogui.press("left")
                            record_action("backward")
                        elif cnt == 3:
                            pyautogui.press("up")
                            record_action("volume up")
                        elif cnt == 4:
                            pyautogui.press("down")
                            record_action("volume down")
                        elif cnt == 5:
                            pyautogui.press("space")
                            record_action("play/pause")

                        prev = cnt
                        start_init = False

                drawing.draw_landmarks(frm, hand_keyPoints, mp.solutions.hands.HAND_CONNECTIONS)

            cv2.imshow("Camera", frm)

            if cv2.waitKey(1) == 27:
                break
            if cv2.waitKey(1) == ord('q'):
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
