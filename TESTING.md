# Hướng Dẫn Test Sau Khi Sửa Lỗi

## 🧪 Test Plan

### Test 1: Kiểm Tra Environment Manager

#### Mục tiêu
Đảm bảo `check_packages_installed()` chỉ kiểm tra, không tự động cài đặt

#### Các bước test:
1. Mở terminal
2. Chạy:
   ```bash
   python env_manager.py face_recognition
   ```
3. **Kết quả mong đợi**:
   - Nếu môi trường chưa có: Tạo mới và cài packages
   - Nếu đã có nhưng thiếu packages: Cài bổ sung
   - Nếu đã đủ: Hiển thị "✓ TẤT CẢ THƯ VIỆN ĐÃ ĐẦY ĐỦ"

4. Kiểm tra qua API:
   ```bash
   python app.py
   # Mở browser: http://localhost:5000
   # Xem phần "Trạng thái môi trường"
   # Click nút "Thiết lập" chỉ khi cần
   ```

✅ **Pass**: Environment check không trigger auto-install


### Test 2: Face Registration và Cache Invalidation

#### Mục tiêu
Đảm bảo user mới được nhận diện ngay lập tức

#### Các bước test:
1. Mở web interface: `http://localhost:5000`
2. Tab "Nhận Diện Khuôn Mặt"
3. Đăng ký user mới:
   - Nhập tên: `test_user`
   - Bật camera
   - Chụp 5-10 ảnh
4. **KHÔNG restart server**
5. Chuyển sang phần "Nhận diện"
6. Bật camera và test nhận diện

✅ **Pass**: User mới được nhận diện ngay lập tức (không cần restart)
❌ **Fail**: Phải restart server mới nhận diện được


### Test 3: DeepFace Base64 Processing

#### Mục tiêu
Đảm bảo DeepFace nhận và xử lý được ảnh base64

#### Các bước test:
1. Mở web: `http://localhost:5000`
2. Chuyển tab "Phân Tích DeepFace"
3. **Cách 1 - Upload file**:
   - Click vào khung upload
   - Chọn ảnh khuôn mặt rõ nét
   - Click "Phân Tích"

4. **Cách 2 - Paste từ clipboard**:
   - Copy một ảnh (Ctrl+C từ file explorer)
   - Click vào tab DeepFace
   - Paste (Ctrl+V)
   - Click "Phân Tích"

5. **Kết quả mong đợi**:
   - Hiển thị: Giới tính, Tuổi, Cảm xúc, Dân tộc
   - Không có lỗi "Thiếu đường dẫn ảnh"
   - Không có lỗi base64

✅ **Pass**: Phân tích thành công với cả 2 cách
❌ **Fail**: Lỗi parse base64 hoặc không tìm thấy file


### Test 4: DeepFace Timeout

#### Mục tiêu
DeepFace không bị timeout trên lần chạy đầu

#### Các bước test:
1. **Lần đầu chạy sau khi cài môi trường**:
   ```bash
   # Nếu chưa activate môi trường
   conda activate deepface_recognition
   python deepface_web.py
   # Bấm Ctrl+C sau 2-3 giây
   ```

2. Quay lại web interface
3. Upload ảnh và phân tích
4. Đợi kết quả (có thể mất 10-20s lần đầu để load model)

✅ **Pass**: DeepFace trả về kết quả (dù mất thời gian)
❌ **Fail**: Timeout error sau 10s


### Test 5: Realtime Recognition

#### Mục tiêu
Realtime recognition không bị duplicate loop

#### Các bước test:
1. Mở tab "Nhận Diện Khuôn Mặt"
2. Click "Bật Camera & Nhận Diện" (chỉ click 1 lần)
3. Mở Developer Console (F12)
4. Xem Network tab
5. Quan sát request `/api/face-recognition/recognize`

✅ **Pass**: Request gửi đều đặn mỗi 1.5s, chỉ có 1 interval
❌ **Fail**: Multiple requests cùng lúc hoặc không đều


### Test 6: Error Handling

#### Mục tiêu
Error messages rõ ràng và hữu ích

#### Test cases:

**6.1. Môi trường chưa thiết lập**
1. Xóa môi trường: `conda env remove -n face_recognition`
2. Restart server
3. Thử nhận diện khuôn mặt

✅ **Pass**: Hiển thị "Môi trường face_recognition chưa được thiết lập"


**6.2. Không có khuôn mặt trong ảnh**
1. Upload ảnh phong cảnh (không có người)
2. DeepFace phân tích

✅ **Pass**: "Không tìm thấy khuôn mặt trong ảnh. Vui lòng sử dụng ảnh rõ nét hơn."


**6.3. Chưa có user trong dataset**
1. Xóa hết folder trong `dataset/`
2. Thử nhận diện

✅ **Pass**: "Không có dữ liệu trong dataset"


### Test 7: Performance

#### Mục tiêu
Đảm bảo hiệu suất tốt

#### Metrics:
- Face Recognition realtime: < 2s/frame
- DeepFace analysis: < 30s (lần đầu), < 5s (các lần sau)
- Memory leak: Không tăng memory khi chạy lâu

#### Cách test:
1. Bật realtime recognition
2. Để chạy 5 phút
3. Kiểm tra Task Manager:
   - CPU usage ổn định
   - Memory không tăng liên tục

✅ **Pass**: Performance ổn định
❌ **Fail**: Memory leak hoặc CPU spike


## 📊 Test Results Template

Sử dụng bảng này để ghi kết quả test:

| Test ID | Tên Test | Status | Ghi chú |
|---------|----------|--------|---------|
| Test 1 | Environment Manager | ⬜ | |
| Test 2 | Face Registration Cache | ⬜ | |
| Test 3 | DeepFace Base64 | ⬜ | |
| Test 4 | DeepFace Timeout | ⬜ | |
| Test 5 | Realtime Recognition | ⬜ | |
| Test 6.1 | Error - No Env | ⬜ | |
| Test 6.2 | Error - No Face | ⬜ | |
| Test 6.3 | Error - No Dataset | ⬜ | |
| Test 7 | Performance | ⬜ | |

Legend:
- ✅ Pass
- ❌ Fail
- ⬜ Not tested yet
- ⚠️ Pass with issues


## 🔍 Debug Commands

Nếu có lỗi, sử dụng các lệnh sau:

```bash
# 1. Kiểm tra môi trường conda
conda env list

# 2. Kiểm tra packages trong môi trường
conda activate face_recognition
pip list

# 3. Test face_recognition script riêng
conda activate face_recognition
python face_recognition_web.py "data:image/jpeg;base64,<BASE64_STRING>"

# 4. Test deepface script riêng  
conda activate deepface_recognition
python deepface_web.py "data:image/jpeg;base64,<BASE64_STRING>"

# 5. Clear cache thủ công (nếu cần)
# Trong Python REPL:
python
>>> from app import _dataset_cache
>>> _dataset_cache.clear()
```


## 📝 Checklist Trước Khi Deploy

- [ ] Tất cả tests đã pass
- [ ] Không có console errors
- [ ] Environment được thiết lập đầy đủ
- [ ] Dataset có ít nhất 1 user để test
- [ ] README.md đã được cập nhật
- [ ] CHANGELOG.md đã ghi nhận thay đổi

---

**Nếu tất cả tests pass → Code đã sẵn sàng production!** 🎉
