import pygame
import random
import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import joblib
import os

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gesture Controlled Snake Game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

cell_size = 20
snake_pos = [width // 2, height // 2]
snake_body = [[width // 2, height // 2],
              [width // 2 - cell_size, height // 2],
              [width // 2 - 2*cell_size, height // 2]]
food_pos = [random.randrange(1, (width // cell_size - 2)) * cell_size + cell_size,
            random.randrange(1, (height // cell_size - 2)) * cell_size + cell_size]
food_spawn = True

direction = 'RIGHT'
change_to = direction

score = 0

paused = False

model_path = r"C:\Users\91812\Downloads\gesture_model.h5"
model = tf.keras.models.load_model(model_path)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    cnt = 0
    thresh = (hand_landmarks.landmark[0].y * 100 - hand_landmarks.landmark[9].y * 100) / 2

    if (hand_landmarks.landmark[5].y * 100 - hand_landmarks.landmark[8].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[9].y * 100 - hand_landmarks.landmark[12].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[13].y * 100 - hand_landmarks.landmark[16].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[17].y * 100 - hand_landmarks.landmark[20].y * 100) > thresh:
        cnt += 1
    if (hand_landmarks.landmark[5].x * 100 - hand_landmarks.landmark[4].x * 100) > 6:
        cnt += 1

    return cnt

def get_gesture():
    ret, frame = cap.read()
    if not ret:
        return None

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        finger_count = count_fingers(hand_landmarks)

        if finger_count == 1:
            return 'UP'
        elif finger_count == 2:
            return 'RIGHT'
        elif finger_count == 3:
            return 'DOWN'
        elif finger_count == 4:
            return 'LEFT'
        elif finger_count == 5:
            return 'PAUSE'

    return None

def game_over():
    my_font = pygame.font.SysFont('times new roman', 50)
    game_over_surface = my_font.render('Your Score is : ' + str(score), True, RED)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (width / 2, height / 4)
    screen.fill(BLACK)
    screen.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    cap.release()
    quit()

def draw_instructions():
    font = pygame.font.SysFont('arial', 20)
    instructions = [
        "Controls:",
        "1 Finger: Move UP",
        "2 Fingers: Move RIGHT",
        "3 Fingers: Move DOWN",
        "4 Fingers: Move LEFT",
        "5 Fingers: PAUSE/RESUME"
    ]
    for i, instruction in enumerate(instructions):
        text = font.render(instruction, True, WHITE)
        screen.blit(text, (10, height - 140 + i * 20))

def show_score():
    score_font = pygame.font.SysFont('arial', 20)
    score_surface = score_font.render('Score : ' + str(score), True, WHITE)
    score_rect = score_surface.get_rect()
    score_rect.topleft = (10, 10)
    screen.blit(score_surface, score_rect)

def show_pause_screen():
    pause_font = pygame.font.SysFont('arial', 50)
    pause_surface = pause_font.render('PAUSED', True, WHITE)
    pause_rect = pause_surface.get_rect()
    pause_rect.center = (width // 2, height // 2)
    screen.blit(pause_surface, pause_rect)

def draw_boundaries():
    pygame.draw.rect(screen, RED, pygame.Rect(0, 0, width, cell_size))  # Top
    pygame.draw.rect(screen, RED, pygame.Rect(0, height - cell_size, width, cell_size))  # Bottom
    pygame.draw.rect(screen, RED, pygame.Rect(0, 0, cell_size, height))  # Left
    pygame.draw.rect(screen, RED, pygame.Rect(width - cell_size, 0, cell_size, height))  # Right

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            quit()

    gesture = get_gesture()
    if gesture == 'PAUSE':
        paused = not paused
    elif not paused and gesture:
        change_to = gesture

    if not paused:
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        if direction == 'UP':
            snake_pos[1] -= cell_size
        if direction == 'DOWN':
            snake_pos[1] += cell_size
        if direction == 'LEFT':
            snake_pos[0] -= cell_size
        if direction == 'RIGHT':
            snake_pos[0] += cell_size

        if (snake_pos[0] < cell_size or snake_pos[0] >= width - cell_size or
            snake_pos[1] < cell_size or snake_pos[1] >= height - cell_size):
            game_over()

        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [random.randrange(1, (width // cell_size - 2)) * cell_size + cell_size,
                        random.randrange(1, (height // cell_size - 2)) * cell_size + cell_size]
        food_spawn = True

        screen.fill(BLACK)
        for pos in snake_body:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], cell_size, cell_size))

        pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], cell_size, cell_size))

        draw_boundaries()

        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over()

        draw_instructions()
        show_score()
    else:
        show_pause_screen()

    pygame.display.update()
    pygame.time.Clock().tick(3)