"""
Service script cho DeepFace Analysis
Chạy trong môi trường conda deepface_recognition
"""
import sys
import os
import json
from deepface import DeepFace
import cv2

# Mapping các giá trị tiếng Anh sang tiếng Việt
EMOTION_MAP = {
    'angry': 'Tức giận',
    'disgust': 'Ghê tởm',
    'fear': 'Sợ hãi',
    'happy': 'Vui vẻ',
    'sad': 'Buồn',
    'surprise': 'Ngạc nhiên',
    'neutral': 'Bình thường'
}

GENDER_MAP = {
    'Man': 'Nam',
    'Woman': 'Nữ'
}

RACE_MAP = {
    'asian': 'Châu Á',
    'indian': 'Ấn Độ',
    'black': 'Da đen',
    'white': 'Da trắng',
    'middle eastern': 'Trung Đông',
    'latino hispanic': 'Mỹ La-tinh'
}

def analyze_face(image_path):
    """Phân tích khuôn mặt với DeepFace"""
    try:
        # Kiểm tra file tồn tại
        if not os.path.exists(image_path):
            return {
                'error': f'File không tồn tại: {image_path}'
            }
        
        # Đọc ảnh
        img = cv2.imread(image_path)
        if img is None:
            return {
                'error': 'Không thể đọc file ảnh'
            }
        
        # Phân tích với DeepFace
        analysis = DeepFace.analyze(
            img_path=image_path,
            actions=['age', 'gender', 'emotion', 'race'],
            enforce_detection=True
        )
        
        # Lấy kết quả (có thể có nhiều khuôn mặt)
        if isinstance(analysis, list):
            result = analysis[0]
        else:
            result = analysis
        
        # Lấy emotion có confidence cao nhất
        emotion_data = result.get('emotion', {})
        dominant_emotion = result.get('dominant_emotion', 'neutral')
        emotion_confidence = emotion_data.get(dominant_emotion, 0)
        
        # Lấy race có confidence cao nhất
        race_data = result.get('race', {})
        dominant_race = result.get('dominant_race', 'asian')
        race_confidence = race_data.get(dominant_race, 0)
        
        # Lấy gender
        gender_data = result.get('gender', {})
        dominant_gender = result.get('dominant_gender', 'Man')
        gender_confidence = max(gender_data.values()) if gender_data else 0
        
        # Lấy age
        age = result.get('age', 0)
        
        # Tạo output JSON
        output = {
            'age': int(age),
            'gender': GENDER_MAP.get(dominant_gender, dominant_gender),
            'gender_confidence': round(gender_confidence, 1),
            'emotion': EMOTION_MAP.get(dominant_emotion, dominant_emotion),
            'emotion_confidence': round(emotion_confidence, 1),
            'race': RACE_MAP.get(dominant_race, dominant_race),
            'race_confidence': round(race_confidence, 1)
        }
        
        return output
        
    except ValueError as e:
        # Không tìm thấy khuôn mặt
        if "Face could not be detected" in str(e):
            return {
                'error': 'Không phát hiện khuôn mặt trong ảnh!'
            }
        else:
            return {
                'error': f'Lỗi: {str(e)}'
            }
    except Exception as e:
        return {
            'error': f'Lỗi không xác định: {str(e)}'
        }

def main():
    """Hàm chính"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'error': 'Usage: python deepface_service.py <image_path>'
        }), file=sys.stderr)
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    result = analyze_face(image_path)
    
    # Output dưới dạng JSON
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
