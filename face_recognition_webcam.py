import face_recognition
import cv2
import os
import numpy as np

# ======================
# Dataset path
# ======================
DATASET_DIR = r"C:\Users\ADMIN\Desktop\FaceRecognition_RealTime\dataset"

known_face_encodings = []
known_face_names = []

print("📂 Loading dataset...")

# ======================
# Load dataset
# ======================
for person_name in os.listdir(DATASET_DIR):
    person_path = os.path.join(DATASET_DIR, person_name)

    if not os.path.isdir(person_path):
        continue

    encodings = []

    for img_name in os.listdir(person_path):
        if img_name.lower().endswith((".jpg", ".png", ".jpeg")):
            img_path = os.path.join(person_path, img_name)

            image = face_recognition.load_image_file(img_path)
            face_encs = face_recognition.face_encodings(image)

            if len(face_encs) > 0:
                encodings.append(face_encs[0])
            else:
                print(f"⚠️ No face in {img_path}")

    if len(encodings) > 0:
        mean_encoding = np.mean(encodings, axis=0)
        known_face_encodings.append(mean_encoding)
        known_face_names.append(person_name)
        print(f"✅ Loaded {person_name} ({len(encodings)} images)")
    else:
        print(f"❌ No valid images for {person_name}")

# ======================
# Open webcam
# ======================
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("❌ Cannot open webcam")
    exit()

print("🎥 Webcam started (press 'q' to quit)")

# ======================
# Realtime recognition
# ======================
while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Resize for speed
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(
        rgb_small_frame, face_locations
    )

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(
            known_face_encodings, face_encoding, tolerance=0.5
        )
        name = "Unknown"

        face_distances = face_recognition.face_distance(
            known_face_encodings, face_encoding
        )

        if len(face_distances) > 0:
            best_match = np.argmin(face_distances)
            if matches[best_match]:
                name = known_face_names[best_match]

        # Scale back
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw box
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Draw label
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom),
                      (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.imshow("Face Recognition - Dataset", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ======================
# Release
# ======================
video_capture.release()
cv2.destroyAllWindows()
