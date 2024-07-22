import V
import numpy as np
import pyautogui
import time
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller

pyautogui.FAILSAFE = False


class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text


class VirtualKeyboardAndGestureControl:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        self.detector = HandDetector(detectionCon=0.8, maxHands=2)

        self.keys = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]
        ]

        self.buttonList = self.init_buttons()

        self.finalText = ""
        self.keyboard = Controller()

        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothing = 2
        self.prev_x, self.prev_y = 0, 0

    def init_buttons(self):
        return [Button([100 * j + 50, 100 * i + 50], key) for i, row in enumerate(self.keys) for j, key in
                enumerate(row)]

    def draw_all(self, img):
        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return img

    def draw_text_box(self, img):
        cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, self.finalText, (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    def handle_keyboard(self, img, hand):
        for button in self.buttonList:
            x, y = button.pos
            w, h = button.size
            if x < hand[8][0] < x + w and y < hand[8][1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                distance_info = self.detector.findDistance(hand[8][:2], hand[12][:2])
                if distance_info:
                    l = distance_info[0]
                    if l < 30:
                        self.keyboard.press(button.text)
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        self.finalText += button.text
                        time.sleep(0.15)
        return img

    def handle_cursor(self, hand):
        fingers = self.detector.fingersUp(hand)
        finger_count = sum(fingers)

        index_finger = hand['lmList'][8]
        x, y = index_finger[0], index_finger[1]

        x = int(self.prev_x + (x - self.prev_x) / self.smoothing)
        y = int(self.prev_y + (y - self.prev_y) / self.smoothing)

        self.prev_x, self.prev_y = x, y

        screen_x = int(np.interp(x, [0, self.cap.get(3)], [0, self.screen_width]))
        screen_y = int(np.interp(y, [0, self.cap.get(4)], [0, self.screen_height]))

        if finger_count == 1:
            pyautogui.moveTo(screen_x, screen_y)
        elif finger_count == 2:
            pyautogui.click()
            time.sleep(0.2)
        elif finger_count == 3:
            pyautogui.rightClick()
            time.sleep(0.2)
        elif finger_count == 4:
            pyautogui.doubleClick()
            time.sleep(0.2)
        elif finger_count == 5:
            pyautogui.scroll(20 if y < self.cap.get(4) / 2 else -20)

    def run(self):
        while True:
            success, img = self.cap.read()
            if not success:
                print("Failed to capture image")
                break

            img = cv2.flip(img, 1)

            hands, img = self.detector.findHands(img)
            img = self.draw_all(img)
            self.draw_text_box(img)

            if len(hands) == 2:
                left_hand = hands[0] if hands[0]['type'] == 'Left' else hands[1]
                right_hand = hands[1] if hands[1]['type'] == 'Right' else hands[0]

                img = self.handle_keyboard(img, left_hand['lmList'])
                self.handle_cursor(right_hand)
            elif len(hands) == 1:
                if hands[0]['type'] == 'Left':
                    img = self.handle_keyboard(img, hands[0]['lmList'])
                else:
                    self.handle_cursor(hands[0])

            cv2.putText(img, "Left: Keyboard, Right: Cursor & Gestures", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2)
            cv2.imshow("Virtual Keyboard and Gesture Control", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    keyboard_and_gesture = VirtualKeyboardAndGestureControl()
    keyboard_and_gesture.run()