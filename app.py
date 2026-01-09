"""
Flask Web Application cho Face Recognition Project
Tự động quản lý 2 môi trường Anaconda riêng biệt
"""
from flask import Flask, render_template, request, jsonify, Response
import subprocess
import os
import sys
import cv2
import base64
import numpy as np
from env_manager import CondaEnvironmentManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Tạo thư mục uploads nếu chưa có
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Khởi tạo Environment Manager
env_manager = CondaEnvironmentManager()

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/api/check-environments', methods=['GET'])
def check_environments():
    """API kiểm tra trạng thái các môi trường"""
    try:
        status = {}
        for env_name in env_manager.envs.keys():
            env_exists = env_manager.check_env_exists(env_name)
            packages_ok = env_manager.check_packages_installed(env_name) if env_exists else False
            
            status[env_name] = {
                'exists': env_exists,
                'packages_installed': packages_ok,
                'ready': env_exists and packages_ok
            }
        
        return jsonify({
            'success': True,
            'environments': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/setup-environment/<env_name>', methods=['POST'])
def setup_environment(env_name):
    """API thiết lập môi trường"""
    try:
        if env_name not in env_manager.envs:
            return jsonify({
                'success': False,
                'error': f'Môi trường {env_name} không hợp lệ'
            }), 400
        
        success = env_manager.setup_environment(env_name)
        
        return jsonify({
            'success': success,
            'message': f'Môi trường {env_name} đã được thiết lập' if success else 'Có lỗi xảy ra'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/face-recognition/register', methods=['POST'])
def register_face():
    """API đăng ký khuôn mặt mới"""
    try:
        # Kiểm tra môi trường
        if not env_manager.check_env_exists('face_recognition'):
            return jsonify({
                'success': False,
                'error': 'Môi trường face_recognition chưa được thiết lập'
            }), 400
        
        data = request.json
        name = data.get('name')
        image_data = data.get('image')
        
        if not name or not image_data:
            return jsonify({
                'success': False,
                'error': 'Thiếu thông tin tên hoặc ảnh'
            }), 400
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Tạo thư mục cho người dùng
        user_folder = os.path.join('dataset', name)
        os.makedirs(user_folder, exist_ok=True)
        
        # Đếm số ảnh hiện có
        count = len(os.listdir(user_folder))
        
        # Lưu ảnh
        filename = os.path.join(user_folder, f'img_{count}.jpg')
        cv2.imwrite(filename, image)
        
        return jsonify({
            'success': True,
            'message': f'Đã lưu ảnh {count + 1} cho {name}',
            'count': count + 1
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/face-recognition/recognize', methods=['POST'])
def recognize_face():
    """API nhận diện khuôn mặt"""
    try:
        # Kiểm tra môi trường
        if not env_manager.check_env_exists('face_recognition'):
            return jsonify({
                'success': False,
                'error': 'Môi trường face_recognition chưa được thiết lập'
            }), 400
        
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'Không có dữ liệu ảnh'
            }), 400
        
        # Lưu ảnh tạm
        temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_recognize.jpg')
        image_bytes = base64.b64decode(image_data.split(',')[1])
        with open(temp_image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Chạy script nhận diện trong môi trường face_recognition
        result = subprocess.run(
            'conda run -n face_recognition python face_recognition_service.py ' + temp_image_path,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True  # Thêm shell=True cho Windows
        )
        
        # Xóa file tạm
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        if result.returncode == 0:
            # Parse kết quả
            output = result.stdout.strip()
            return jsonify({
                'success': True,
                'result': output
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/deepface/analyze', methods=['POST'])
def analyze_face():
    """API phân tích khuôn mặt với DeepFace"""
    try:
        # Kiểm tra môi trường
        if not env_manager.check_env_exists('deepface_recognition'):
            return jsonify({
                'success': False,
                'error': 'Môi trường deepface_recognition chưa được thiết lập'
            }), 400
        
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'Không có dữ liệu ảnh'
            }), 400
        
        # Lưu ảnh tạm
        temp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_analyze.jpg')
        image_bytes = base64.b64decode(image_data.split(',')[1])
        with open(temp_image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Chạy script phân tích trong môi trường deepface_recognition
        result = subprocess.run(
            'conda run -n deepface_recognition python deepface_service.py ' + temp_image_path,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True  # Thêm shell=True cho Windows
        )
        
        # Xóa file tạm
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        if result.returncode == 0:
            # Parse kết quả JSON
            import json
            output = json.loads(result.stdout.strip())
            return jsonify({
                'success': True,
                'result': output
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-registered-users', methods=['GET'])
def get_registered_users():
    """API lấy danh sách người dùng đã đăng ký"""
    try:
        dataset_path = 'dataset'
        if not os.path.exists(dataset_path):
            return jsonify({
                'success': True,
                'users': []
            })
        
        users = []
        for user_folder in os.listdir(dataset_path):
            folder_path = os.path.join(dataset_path, user_folder)
            if os.path.isdir(folder_path):
                image_count = len([f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                users.append({
                    'name': user_folder,
                    'image_count': image_count
                })
        
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("KHỞI ĐỘNG FACE RECOGNITION WEB APPLICATION")
    print("="*60)
    print("Đang kiểm tra các môi trường...")
    
    # Kiểm tra trạng thái môi trường
    for env_name in env_manager.envs.keys():
        exists = env_manager.check_env_exists(env_name)
        if exists:
            packages_ok = env_manager.check_packages_installed(env_name)
            status = "✓ SẴN SÀNG" if packages_ok else "⚠ THIẾU PACKAGES"
        else:
            status = "✗ CHƯA CÀI"
        print(f"  {env_name}: {status}")
    
    print("\nServer đang chạy tại: http://localhost:5000")
    print("Nhấn Ctrl+C để dừng server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
