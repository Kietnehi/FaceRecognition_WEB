# 🎭 Face Recognition & Analysis System

Hệ thống nhận diện và phân tích khuôn mặt sử dụng Face Recognition và DeepFace với giao diện web hiện đại.


<p align="center">
  <img src="./image/flask.png" width="200" alt="Flask"/>
  <img src="./image/python.png" width="200" alt="Python"/>
  <img src="./image/anaconda.jpg" width="200" alt="Anaconda"/>
  <img src="./image/Opencv.png" width="200" alt="OpenCV"/>
</p>

## 🎬 GIF

![GIF](output.gif)

*Minh họa hệ thống nhận diện và phân tích khuôn mặt real-time*

## 📋 Mô tả dự án

Đây là một hệ thống web hoàn chỉnh cho phép:

### 1. **Face Recognition** 👤
- Đăng ký khuôn mặt người dùng mới
- Nhận diện và xác định danh tính người dùng từ camera
- Quản lý database người dùng đã đăng ký

### 2. **DeepFace Analysis** 🔍
- Dự đoán tuổi (Age)
- Phân tích giới tính (Gender)
- Nhận diện cảm xúc (Emotion)
- Xác định nhóm dân tộc (Race)

## 🏗️ Kiến trúc hệ thống

Hệ thống sử dụng 2 môi trường Anaconda riêng biệt:

```
├── face_recognition/          # Môi trường cho nhận diện khuôn mặt
│   ├── face_recognition
│   ├── dlib
│   ├── numpy
│   ├── pillow
│   └── opencv-python
│
└── deepface_recognition/      # Môi trường cho phân tích DeepFace
    ├── deepface==0.0.96
    ├── opencv-python==4.12.0.88
    └── tf-keras
```

## 📁 Cấu trúc thư mục

```
FaceRecognition_RealTime/
├── app.py                          # Flask web application chính
├── env_manager.py                  # Script quản lý môi trường Anaconda
├── face_recognition_service.py     # Service nhận diện khuôn mặt
├── deepface_service.py             # Service phân tích DeepFace
├── collect_data.py                 # Tool thu thập dữ liệu (standalone)
├── requirements.txt                # Danh sách thư viện
├── README.md                       # File này
│
├── templates/                      # HTML templates
│   └── index.html                  # Giao diện chính
│
├── static/                         # Static files (CSS, JS)
│   ├── style.css                   # Stylesheet
│   └── script.js                   # JavaScript logic
│
├── dataset/                        # Dữ liệu khuôn mặt đã đăng ký
│   ├── user1/
│   ├── user2/
│   └── ...
│
└── uploads/                        # Thư mục tạm cho file upload
```

## 🚀 Cài đặt và chạy

### Bước 1: Cài đặt Anaconda/Miniconda

Đảm bảo bạn đã cài đặt [Anaconda](https://www.anaconda.com/download) hoặc [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

### Bước 2: Clone hoặc tải project

```bash
git clone <repository-url>
cd FaceRecognition_RealTime
```

### Bước 3: Thiết lập môi trường tự động

Hệ thống có thể tự động thiết lập môi trường khi chạy lần đầu.

#### Cách 1: Thiết lập tất cả môi trường trước

```bash
python env_manager.py
```

#### Cách 2: Thiết lập từng môi trường

```bash
# Thiết lập môi trường Face Recognition
python env_manager.py face_recognition

# Thiết lập môi trường DeepFace
python env_manager.py deepface_recognition
```

### Bước 4: Cài đặt Flask (môi trường base)

```bash
pip install flask
```

### Bước 5: Chạy web application

```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

## 🎮 Hướng dẫn sử dụng

### 1. Kiểm tra môi trường

Khi truy cập trang web, phần "Trạng thái môi trường" sẽ hiển thị:
- ✓ **Sẵn sàng**: Môi trường đã được thiết lập đầy đủ
- ⚠ **Thiếu packages**: Môi trường tồn tại nhưng thiếu thư viện
- ✗ **Chưa cài đặt**: Môi trường chưa được tạo

Nhấn nút **"Thiết lập"** để tự động cài đặt môi trường thiếu.

### 2. Đăng ký khuôn mặt (Face Registration)

1. Chuyển sang tab **"👤 Nhận Diện Khuôn Mặt"**
2. Nhập tên người dùng trong ô "Tên người dùng"
3. Nhấn **"📷 Bật Camera"**
4. Điều chỉnh vị trí khuôn mặt trong khung hình
5. Nhấn **"✓ Chụp & Lưu"** nhiều lần để lưu nhiều ảnh (khuyến nghị: 5-10 ảnh)
6. Nhấn **"✕ Tắt Camera"** khi hoàn tất

> **Mẹo**: Chụp nhiều góc độ khác nhau (trái, phải, trên, dưới) để tăng độ chính xác nhận diện.

### 3. Nhận diện khuôn mặt (Face Recognition)

1. Trong tab **"👤 Nhận Diện Khuôn Mặt"**, phần bên phải
2. Nhấn **"📷 Bật Camera"**
3. Nhấn **"🔍 Nhận Diện"** để nhận diện khuôn mặt trong khung hình
4. Kết quả sẽ hiển thị tên và độ chính xác (%)

### 4. Phân tích DeepFace

1. Chuyển sang tab **"🔍 Phân Tích DeepFace"**
2. Nhấn **"📷 Bật Camera"**
3. Nhấn **"🔬 Phân Tích"**
4. Hệ thống sẽ hiển thị:
   - **Giới tính**: Nam/Nữ với độ tin cậy
   - **Tuổi**: Độ tuổi dự đoán
   - **Cảm xúc**: Vui vẻ, buồn, tức giận, v.v.
   - **Dân tộc**: Châu Á, Da trắng, Da đen, v.v.

## � Hình ảnh minh họa

<div align="center">
  <img src="image/face_recognition.png" alt="Giao diện chính" width="800"/>
  <p><i>Giao diện web của hệ thống Face Recognition</i></p>
</div>

<div align="center">
  <img src="image/deepface_recognition.png" alt="Phân tích DeepFace" width="800"/>
  <p><i>Phân tích khuôn mặt với DeepFace</i></p>
</div>

## �🔧 Tool thu thập dữ liệu độc lập

File `collect_data.py` là tool độc lập để thu thập dữ liệu nhanh hơn:

```bash
# Chỉnh sửa cấu hình trong file:
FOLDER_PATH = "dataset/ten_nguoi_dung"
IMG_SIZE = 300
SAVE_INTERVAL = False  # True = tự động lưu, False = bấm 's' để lưu

# Chạy:
python collect_data.py
```

**Phím tắt:**
- `s`: Chụp và lưu ảnh
- `q`: Thoát

## 🛠️ Troubleshooting

### Lỗi: "Conda chưa được cài đặt"

**Giải pháp**: Cài đặt [Anaconda](https://www.anaconda.com/download) hoặc [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

### Lỗi: "Không thể truy cập camera"

**Giải pháp**:
- Kiểm tra camera đã được kích hoạt
- Cho phép trình duyệt truy cập camera
- Đảm bảo không có ứng dụng khác đang sử dụng camera

### Lỗi: "Face could not be detected"

**Giải pháp**:
- Đảm bảo khuôn mặt nằm trong khung hình
- Ánh sáng đủ sáng
- Khuôn mặt nhìn thẳng vào camera

### Lỗi cài đặt dlib (Windows)

**Giải pháp**:
```bash
# Cài đặt Visual C++ Build Tools trước
# Hoặc tải dlib wheel từ: https://github.com/jloh02/dlib/releases

conda install -c conda-forge dlib
```

### Lỗi TensorFlow/GPU

**Giải pháp**: DeepFace có thể chạy trên CPU. Nếu muốn dùng GPU:
```bash
conda install tensorflow-gpu
```

## 📊 Yêu cầu hệ thống

- **OS**: Windows, macOS, Linux
- **Python**: 3.8 - 3.10
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB+)
- **Camera**: Webcam hoặc camera tích hợp
- **Trình duyệt**: Chrome, Firefox, Edge (phiên bản mới)

## 🔐 Bảo mật

- Dữ liệu khuôn mặt được lưu local trong thư mục `dataset/`
- Không có dữ liệu được gửi ra ngoài
- Ảnh tạm trong `uploads/` tự động xóa sau khi xử lý

## 📝 Ghi chú

- Hệ thống hoạt động offline hoàn toàn
- Dữ liệu được lưu trữ local
- Có thể tùy chỉnh model trong DeepFace nếu cần
- Hỗ trợ nhiều khuôn mặt trong một khung hình

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo Pull Request hoặc Issue.

## 📄 License

MIT License

## 👨‍💻 Tác giả

Dự án Face Recognition & Analysis System

## 🔗 Tài liệu tham khảo

- [Face Recognition Library](https://github.com/ageitgey/face_recognition)
- [DeepFace](https://github.com/serengil/deepface)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenCV Python](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

---

**Lưu ý**: Dự án này chỉ dùng cho mục đích học tập và nghiên cứu. Không sử dụng cho mục đích xâm phạm quyền riêng tư.
