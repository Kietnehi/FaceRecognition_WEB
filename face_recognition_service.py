"""
Face Recognition Service - Chạy trong môi trường face_recognition của Anaconda
Load models trước để đảm bảo real-time processing
Port: 5001
"""
from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import base64
import io
import os
import time
from PIL import Image

app = Flask(__name__)

# Global variables để cache dataset
_dataset_cache = {
    'encodings': [],
    'names': [],
    'timestamp': 0,
    'loaded': False
}

def load_face_dataset():
    """Load và cache dataset - chỉ load 1 lần khi khởi động"""
    global _dataset_cache
    
    # Nếu đã load rồi và chưa quá 5 phút, dùng cache
    if _dataset_cache['loaded'] and (time.time() - _dataset_cache['timestamp'] < 300):
        return _dataset_cache['encodings'], _dataset_cache['names']
    
    print("🔄 Đang load face recognition dataset...")
    start_time = time.time()
    
    dataset_dir = 'dataset'
    known_face_encodings = []
    known_face_names = []
    
    if not os.path.exists(dataset_dir):
        print("⚠️ Dataset folder không tồn tại")
        return [], []
    
    person_count = 0
    total_images = 0
    
    for person_name in os.listdir(dataset_dir):
        person_path = os.path.join(dataset_dir, person_name)
        if not os.path.isdir(person_path):
            continue
        
        person_count += 1
        encodings = []
        
        for img_name in os.listdir(person_path):
            if img_name.lower().endswith(('.jpg', '.png', '.jpeg')):
                img_path = os.path.join(person_path, img_name)
                try:
                    image = face_recognition.load_image_file(img_path)
                    face_encs = face_recognition.face_encodings(image)
                    if len(face_encs) > 0:
                        encodings.append(face_encs[0])
                        total_images += 1
                except Exception as e:
                    print(f"⚠️ Lỗi khi load {img_path}: {str(e)}")
                    continue
        
        if encodings:
            # Tính encoding trung bình cho mỗi người
            mean_encoding = np.mean(encodings, axis=0)
            known_face_encodings.append(mean_encoding)
            known_face_names.append(person_name)
    
    # Update cache
    _dataset_cache['encodings'] = known_face_encodings
    _dataset_cache['names'] = known_face_names
    _dataset_cache['timestamp'] = time.time()
    _dataset_cache['loaded'] = True
    
    elapsed = time.time() - start_time
    print(f"✅ Dataset loaded: {person_count} người, {total_images} ảnh trong {elapsed:.2f}s")
    
    return known_face_encodings, known_face_names

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'face_recognition',
        'dataset_loaded': _dataset_cache['loaded'],
        'persons_count': len(_dataset_cache['names']),
        'timestamp': _dataset_cache['timestamp']
    })

@app.route('/reload-dataset', methods=['POST'])
def reload_dataset():
    """Reload dataset - gọi khi có người dùng mới được đăng ký"""
    global _dataset_cache
    _dataset_cache['loaded'] = False
    _dataset_cache['timestamp'] = 0
    
    encodings, names = load_face_dataset()
    
    return jsonify({
        'success': True,
        'message': f'Dataset đã được reload: {len(names)} người',
        'persons_count': len(names)
    })

@app.route('/recognize', methods=['POST'])
def recognize_face():
    """API nhận diện khuôn mặt từ base64 image"""
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'Không có dữ liệu ảnh'
            }), 400
        
        # Load dataset (từ cache nếu đã load)
        known_encodings, known_names = load_face_dataset()
        
        if not known_encodings:
            return jsonify({
                'success': False,
                'error': 'Không có dữ liệu trong dataset. Vui lòng đăng ký khuôn mặt trước.'
            }), 400
        
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image_pil = Image.open(io.BytesIO(image_bytes))
        image_rgb = np.array(image_pil.convert('RGB'))
        
        # Detect và encode faces
        start_time = time.time()
        face_locations = face_recognition.face_locations(image_rgb)
        face_encodings = face_recognition.face_encodings(image_rgb, face_locations)
        processing_time = time.time() - start_time
        
        if not face_encodings:
            return jsonify({
                'success': True,
                'faces': [],
                'total_faces': 0,
                'processing_time': round(processing_time, 3),
                'message': 'Không tìm thấy khuôn mặt'
            })
        
        # Nhận diện từng khuôn mặt
        results = []
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            confidence = 0
            
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    confidence = round((1 - face_distances[best_match_index]) * 100, 2)
            
            results.append({
                'name': name,
                'confidence': confidence,
                'location': {
                    'top': int(face_location[0]),
                    'right': int(face_location[1]),
                    'bottom': int(face_location[2]),
                    'left': int(face_location[3])
                }
            })
        
        return jsonify({
            'success': True,
            'faces': results,
            'total_faces': len(results),
            'processing_time': round(processing_time, 3)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi nhận diện: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 FACE RECOGNITION SERVICE - Starting...")
    print("="*70)
    print("📦 Environment: face_recognition (Anaconda)")
    print("🌐 Port: 5001")
    print("="*70 + "\n")
    
    # Pre-load dataset khi khởi động
    print("📊 Pre-loading dataset...")
    encodings, names = load_face_dataset()
    if len(names) > 0:
        print(f"✅ Dataset ready: {len(names)} người đã đăng ký")
    else:
        print("⚠️ Dataset trống - chưa có người dùng nào được đăng ký")
    
    print("\n" + "="*70)
    print("✅ Face Recognition Service is READY!")
    print("🌐 Listening on: http://localhost:5001")
    print("="*70 + "\n")
    
    # Chạy service
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
