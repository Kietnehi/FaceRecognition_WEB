import cv2
from deepface import DeepFace

# Mở webcam (0 là webcam mặc định)
cap = cv2.VideoCapture(0)
text = "Waiting for analysis..."

# Giảm lag (phân tích không phải frame nào cũng chạy)
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # Chỉ phân tích mỗi 20 frame để đỡ lag
    if frame_count % 20 == 0:
        try:
            result = DeepFace.analyze(
                frame,
                actions=['age', 'gender', 'emotion', 'race'],
                enforce_detection=False
            )

            age = result[0]['age']
            gender = result[0]['dominant_gender']
            emotion = result[0]['dominant_emotion']
            race = result[0]['dominant_race']

            text = f"Age: {age}, Gender: {gender}, Emotion: {emotion}, Race: {race}"

        except Exception as e:
            text = "No face detected"

    # Thông tin
    line1 = f"Age: {age} | Gender: {gender}"
    line2 = f"Emotion: {emotion} | Race: {race}"

    # Vị trí
    x, y = 20, 30
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2

    # Tính kích thước chữ
    (w1, h1), _ = cv2.getTextSize(line1, font, font_scale, thickness)
    (w2, h2), _ = cv2.getTextSize(line2, font, font_scale, thickness)

    # Vẽ nền đen
    cv2.rectangle(
        frame,
        (x - 10, y - h1 - 10),
        (x + max(w1, w2) + 10, y + h2 + 20),
        (0, 0, 0),
        -1
    )

    # Vẽ chữ
    cv2.putText(frame, line1, (x, y),
                font, font_scale, (0, 255, 0), thickness)

    cv2.putText(frame, line2, (x, y + 30),
                font, font_scale, (0, 255, 0), thickness)

    cv2.imshow("DeepFace Realtime", frame)

    # Nhấn q để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
