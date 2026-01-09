"""
Service script cho Face Recognition
Chạy trong môi trường conda face_recognition
"""
import sys
import os
import face_recognition
import cv2
import numpy as np

def load_known_faces(dataset_path='dataset'):
    """Load tất cả khuôn mặt đã đăng ký từ dataset"""
    known_face_encodings = []
    known_face_names = []
    
    if not os.path.exists(dataset_path):
        return known_face_encodings, known_face_names
    
    # Duyệt qua từng thư mục người dùng
    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        
        if not os.path.isdir(person_folder):
            continue
        
        # Load tất cả ảnh của người này
        for image_file in os.listdir(person_folder):
            if not image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            image_path = os.path.join(person_folder, image_file)
            
            try:
                # Load và encode khuôn mặt
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if len(encodings) > 0:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(person_name)
            except Exception as e:
                print(f"Lỗi khi xử lý {image_path}: {e}", file=sys.stderr)
                continue
    
    return known_face_encodings, known_face_names

def recognize_face(image_path):
    """Nhận diện khuôn mặt từ ảnh"""
    try:
        # Load known faces
        known_face_encodings, known_face_names = load_known_faces()
        
        if len(known_face_encodings) == 0:
            return "Chưa có dữ liệu người dùng nào được đăng ký!"
        
        # Load ảnh cần nhận diện
        image = face_recognition.load_image_file(image_path)
        
        # Tìm tất cả khuôn mặt trong ảnh
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) == 0:
            return "Không phát hiện khuôn mặt nào trong ảnh!"
        
        results = []
        
        # Nhận diện từng khuôn mặt
        for face_encoding in face_encodings:
            # So sánh với known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            name = "Unknown"
            
            # Tính khoảng cách với từng known face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    confidence = (1 - face_distances[best_match_index]) * 100
                    results.append(f"{name} ({confidence:.1f}%)")
                else:
                    results.append("Unknown")
        
        if len(results) == 0:
            return "Không nhận diện được khuôn mặt!"
        
        return " | ".join(results)
        
    except Exception as e:
        return f"Lỗi: {str(e)}"

def main():
    """Hàm chính"""
    if len(sys.argv) < 2:
        print("Usage: python face_recognition_service.py <image_path>", file=sys.stderr)
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"File không tồn tại: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    result = recognize_face(image_path)
    print(result)

if __name__ == "__main__":
    main()
