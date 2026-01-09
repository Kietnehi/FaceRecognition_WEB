"""
DeepFace Service - Chạy trong môi trường deepface_recognition của Anaconda
Load models trước để đảm bảo real-time processing
Port: 5002
"""
from flask import Flask, request, jsonify
from deepface import DeepFace
import base64
import io
import os
import time
import tempfile
from PIL import Image
import numpy as np

app = Flask(__name__)

# Global variable để track model loading status
_model_status = {
    'loaded': False,
    'timestamp': 0,
    'models': ['age', 'gender', 'race', 'emotion']
}

def convert_to_serializable(obj):
    """
    Chuyển đổi numpy types thành Python native types để có thể serialize JSON
    """
    if isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def preload_models():
    """Pre-load DeepFace models khi khởi động service"""
    global _model_status
    
    if _model_status['loaded']:
        print("✅ Models đã được load trước đó")
        return True
    
    print("\n🔄 Đang pre-load DeepFace models...")
    print("⏳ Quá trình này có thể mất 30-60 giây...")
    start_time = time.time()
    
    try:
        # Tạo một ảnh dummy để force load tất cả models
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        dummy_img[100:150, 100:150] = [255, 255, 255]  # white square để có "face"
        
        # Lưu tạm
        temp_path = os.path.join(tempfile.gettempdir(), 'deepface_warmup.jpg')
        Image.fromarray(dummy_img).save(temp_path)
        
        # Chạy analyze để load models
        try:
            DeepFace.analyze(
                img_path=temp_path,
                actions=['age', 'gender', 'race', 'emotion'],
                enforce_detection=False,
                silent=True
            )
            print("✅ Models loaded successfully!")
        except Exception as e:
            # Ngay cả khi có lỗi detection, models vẫn được load
            print(f"⚠️ Warmup warning (expected): {str(e)[:100]}")
            print("✅ Models đã được load (ignore warning trên)")
        
        # Xóa file tạm
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        _model_status['loaded'] = True
        _model_status['timestamp'] = time.time()
        
        elapsed = time.time() - start_time
        print(f"✅ Pre-loading hoàn tất trong {elapsed:.2f}s")
        print("🚀 Service sẵn sàng xử lý real-time!\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi pre-load models: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'deepface',
        'models_loaded': _model_status['loaded'],
        'supported_actions': _model_status['models'],
        'timestamp': _model_status['timestamp']
    })

@app.route('/analyze', methods=['POST'])
def analyze_face():
    """API phân tích khuôn mặt từ base64 image"""
    temp_file = None
    
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'Không có dữ liệu ảnh'
            }), 400
        
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image_pil = Image.open(io.BytesIO(image_bytes))
        
        # Convert RGBA sang RGB nếu cần (để tránh lỗi khi lưu JPEG)
        if image_pil.mode in ('RGBA', 'LA', 'P'):
            # Tạo background trắng
            rgb_image = Image.new('RGB', image_pil.size, (255, 255, 255))
            if image_pil.mode == 'P':
                image_pil = image_pil.convert('RGBA')
            rgb_image.paste(image_pil, mask=image_pil.split()[-1] if image_pil.mode in ('RGBA', 'LA') else None)
            image_pil = rgb_image
        elif image_pil.mode != 'RGB':
            image_pil = image_pil.convert('RGB')
        
        # Lưu tạm để DeepFace có thể đọc
        temp_file = os.path.join(tempfile.gettempdir(), f'deepface_analyze_{int(time.time()*1000)}.jpg')
        image_pil.save(temp_file, 'JPEG')
        
        # Phân tích ảnh
        start_time = time.time()
        objs = DeepFace.analyze(
            img_path=temp_file,
            actions=['age', 'gender', 'race', 'emotion'],
            enforce_detection=True,
            silent=True
        )
        processing_time = time.time() - start_time
        
        # Xóa file tạm
        if os.path.exists(temp_file):
            os.remove(temp_file)
            temp_file = None
        
        if len(objs) == 0:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy khuôn mặt trong ảnh'
            })
        
        # Lấy kết quả khuôn mặt đầu tiên
        obj = objs[0]
        
        # Convert tất cả dữ liệu thành Python native types trước
        result = {
            'success': True,
            'age': int(obj.get('age', 0)),
            'gender': str(obj.get('dominant_gender', 'N/A')),
            'gender_confidence': float(round(float(obj.get('gender', {}).get(obj.get('dominant_gender', ''), 0)), 2)),
            'emotion': str(obj.get('dominant_emotion', 'N/A')),
            'emotion_confidence': float(round(float(obj.get('emotion', {}).get(obj.get('dominant_emotion', ''), 0)), 2)),
            'race': str(obj.get('dominant_race', 'N/A')),
            'race_confidence': float(round(float(obj.get('race', {}).get(obj.get('dominant_race', ''), 0)), 2)),
            'all_emotions': convert_to_serializable(obj.get('emotion', {})),
            'all_races': convert_to_serializable(obj.get('race', {})),
            'total_faces': int(len(objs)),
            'processing_time': float(round(processing_time, 3))
        }
        
        # Convert toàn bộ result để đảm bảo an toàn
        result = convert_to_serializable(result)
        
        return jsonify(result)
        
    except Exception as e:
        # Cleanup temp file nếu có lỗi
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        
        error_msg = str(e)
        
        # Xử lý lỗi phổ biến
        if "Face could not be detected" in error_msg or "no face" in error_msg.lower():
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy khuôn mặt trong ảnh. Vui lòng sử dụng ảnh rõ nét hơn.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': f'Lỗi phân tích: {error_msg}'
            }), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 DEEPFACE SERVICE - Starting...")
    print("="*70)
    print("📦 Environment: deepface_recognition (Anaconda)")
    print("🌐 Port: 5002")
    print("="*70 + "\n")
    
    # Pre-load models khi khởi động
    print("🧠 Pre-loading DeepFace AI models...")
    success = preload_models()
    
    if success:
        print("\n" + "="*70)
        print("✅ DeepFace Service is READY!")
        print("🌐 Listening on: http://localhost:5002")
        print("⚡ Real-time processing enabled (models pre-loaded)")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("⚠️ Service starting with warnings...")
        print("Models sẽ được load khi có request đầu tiên")
        print("="*70 + "\n")
    
    # Chạy service
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
