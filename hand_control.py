import cv2
import mediapipe as mp
import socket
import time

# ESP32 Wi-Fi details
ESP32_IP = "10.194.208.1"  # Change to your ESP32 IP
ESP32_PORT = 1234           # Must match your ESP32 TCP server port

# Connect to ESP32 via TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((ESP32_IP, ESP32_PORT))
    print("[Connected] to ESP32")
except Exception as e:
    print(f"Failed to connect to ESP32: {e}")
    exit()

time.sleep(1)

# MediaPipe hands setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    """Count raised fingers using MediaPipe landmarks."""
    tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
    fingers = 0

    # Check fingers (except thumb)
    for tip_id in tips:
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            fingers += 1

    # Thumb (x position check)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers += 1

    return fingers

# Map finger count to motor commands
command_map = {
    1: "F",  # Forward
    2: "B",  # Backward
    3: "L",  # Left
    4: "R",  # Right
    5: "S"   # Stop
}

last_command = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    finger_count = 0
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            finger_count = count_fingers(hand_landmarks)

    # Display finger count
    cv2.putText(frame, f"Fingers: {finger_count}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Send command to ESP32 over Wi-Fi
    if finger_count in command_map:
        command = command_map[finger_count]
        if command != last_command:  # Avoid repeated sending
            try:
                client_socket.send(command.encode())
                last_command = command
                print(f"Sent: {command}")
            except Exception as e:
                print(f"Socket error: {e}")
                break

    cv2.imshow("MediaPipe Hands Wi-Fi Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

# Clean up
client_socket.close()
cap.release()
cv2.destroyAllWindows()
