import cv2
import os
import time

# --- CẤU HÌNH ---
FOLDER_PATH = "dataset/my_object"  # Thư mục chứa ảnh
IMG_SIZE = 300                     # Kích thước ảnh muốn cắt (300x300)
SAVE_INTERVAL = False              # True: Tự động lưu mỗi giây, False: Bấm 's' để lưu
# ----------------

# Tạo thư mục nếu chưa tồn tại
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)
    print(f"Đã tạo thư mục: {FOLDER_PATH}")

# Khởi động webcam
cap = cv2.VideoCapture(0)

# Đếm số lượng ảnh hiện có trong thư mục để đặt tên tiếp theo
count = len(os.listdir(FOLDER_PATH))
last_save_time = time.time()

print("--- HƯỚNG DẪN ---")
print("Nhấn 's' để lưu ảnh thủ công.")
print("Nhấn 'q' để thoát chương trình.")
print("-----------------")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Lật ngược ảnh cho giống gương (tùy chọn)
    frame = cv2.flip(frame, 1)
    
    # Lấy kích thước khung hình
    h, w, _ = frame.shape
    
    # Tính toán tọa độ trung tâm để vẽ khung vuông (ROI)
    # Tọa độ góc trên bên trái (x1, y1) và góc dưới bên phải (x2, y2)
    x1 = int((w - IMG_SIZE) / 2)
    y1 = int((h - IMG_SIZE) / 2)
    x2 = x1 + IMG_SIZE
    y2 = y1 + IMG_SIZE

    # Copy frame để hiển thị (không vẽ đè lên ảnh gốc dùng để lưu)
    display_frame = frame.copy()

    # Vẽ khung hình chữ nhật màu xanh lá lên màn hình hiển thị
    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Hiển thị số lượng ảnh đã chụp
    cv2.putText(display_frame, f"Da luu: {count}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Data Collector", display_frame)

    # --- XỬ LÝ LƯU ẢNH ---
    key = cv2.waitKey(1) & 0xFF
    
    save_flag = False
    
    # Cách 1: Bấm phím 's' để lưu
    if key == ord('s'):
        save_flag = True
        
    # Cách 2: Tự động lưu mỗi 1 giây (nếu bật chế độ SAVE_INTERVAL)
    if SAVE_INTERVAL:
        if time.time() - last_save_time > 1: # 1 giây
            save_flag = True
            last_save_time = time.time()

    if save_flag:
        # Cắt vùng ảnh trong khung (ROI)
        roi_img = frame[y1:y2, x1:x2]
        
        # Tạo tên file
        filename = f"{FOLDER_PATH}/img_{count}.jpg"
        
        # Lưu ảnh
        cv2.imwrite(filename, roi_img)
        print(f"Đã lưu: {filename}")
        count += 1
        
        # Hiệu ứng nháy màn hình khi chụp
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), (255, 255, 255), 10)
        cv2.imshow("Data Collector", display_frame)
        cv2.waitKey(50) # Dừng 50ms để tạo hiệu ứng

    # Thoát
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()