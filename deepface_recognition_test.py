from deepface import DeepFace

# 1. Gán đường dẫn ảnh của bạn vào biến
img_path = "C:\\Users\\ADMIN\\Desktop\\FaceRecognition_RealTime\\dataset\\messi\\download (10).jpg"

try:
    # 2. Phân tích ảnh
    # actions: chọn những gì bạn muốn phân tích
    objs = DeepFace.analyze(img_path = img_path,
                            actions = ['age', 'gender', 'race', 'emotion'])

    # 3. In kết quả
    # Vì 1 ảnh có thể có nhiều mặt, kết quả trả về là 1 list
    print("Tuổi dự đoán:", objs[0]['age'])
    print("Giới tính:", objs[0]['dominant_gender'])
    print("Cảm xúc:", objs[0]['dominant_emotion'])
    print("Nhóm dân tộc:", objs[0]['dominant_race'])

except Exception as e:
    print("Lỗi rồi! Có thể không tìm thấy mặt hoặc đường dẫn sai.")
    print(e)