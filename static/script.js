// Global variables
let registerStream = null;
let recognizeStream = null;
let deepfaceImageData = null; // Store uploaded/pasted image

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    checkEnvironments();
    loadRegisteredUsers();
    setupDeepfaceUpload(); // Setup upload và paste cho DeepFace
});

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    if (tabName === 'face-recognition') {
        document.getElementById('face-recognition-tab').classList.add('active');
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
    } else if (tabName === 'deepface') {
        document.getElementById('deepface-tab').classList.add('active');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
    }
}

// Environment Management
async function checkEnvironments() {
    try {
        const response = await fetch('/api/check-environments');
        const data = await response.json();
        
        if (data.success) {
            updateEnvironmentStatus('face_recognition', data.environments.face_recognition);
            updateEnvironmentStatus('deepface_recognition', data.environments.deepface_recognition);
        }
    } catch (error) {
        console.error('Error checking environments:', error);
    }
}

function updateEnvironmentStatus(envName, status) {
    const cardId = envName === 'face_recognition' ? 'env-face-recognition' : 'env-deepface';
    const card = document.getElementById(cardId);
    const dot = card.querySelector('.status-dot');
    const text = card.querySelector('.status-text');
    const btn = card.querySelector('.btn-setup');
    
    if (status.ready) {
        dot.className = 'status-dot ready';
        text.textContent = '✓ Sẵn sàng';
        btn.disabled = true;
        btn.textContent = 'Đã thiết lập';
    } else if (status.exists && !status.packages_installed) {
        dot.className = 'status-dot warning';
        text.textContent = '⚠ Thiếu packages';
        btn.disabled = false;
    } else {
        dot.className = 'status-dot not-ready';
        text.textContent = '✗ Chưa cài đặt';
        btn.disabled = false;
    }
}

async function setupEnvironment(envName) {
    showLoading('Đang thiết lập môi trường ' + envName + '...');
    
    try {
        const response = await fetch('/api/setup-environment/' + envName, {
            method: 'POST'
        });
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            alert('✓ Môi trường đã được thiết lập thành công!');
            checkEnvironments();
        } else {
            alert('✗ Lỗi: ' + data.error);
        }
    } catch (error) {
        hideLoading();
        alert('✗ Lỗi khi thiết lập môi trường: ' + error.message);
    }
}

// Loading Overlay
function showLoading(text) {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    loadingText.textContent = text || 'Đang xử lý...';
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('active');
}

// Face Registration Functions
async function startRegisterCamera() {
    try {
        registerStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        document.getElementById('register-video').srcObject = registerStream;
    } catch (error) {
        alert('Không thể truy cập camera: ' + error.message);
    }
}

function stopRegisterCamera() {
    if (registerStream) {
        registerStream.getTracks().forEach(track => track.stop());
        document.getElementById('register-video').srcObject = null;
        registerStream = null;
    }
}

async function captureRegister() {
    const name = document.getElementById('user-name').value.trim();
    
    if (!name) {
        alert('Vui lòng nhập tên người dùng!');
        return;
    }
    
    if (!registerStream) {
        alert('Vui lòng bật camera trước!');
        return;
    }
    
    const video = document.getElementById('register-video');
    const canvas = document.getElementById('register-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    showLoading('Đang lưu ảnh...');
    
    try {
        const response = await fetch('/api/face-recognition/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                image: imageData
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        const statusDiv = document.getElementById('register-status');
        
        if (data.success) {
            statusDiv.className = 'status-message success';
            statusDiv.textContent = '✓ ' + data.message;
            loadRegisteredUsers();
        } else {
            statusDiv.className = 'status-message error';
            statusDiv.textContent = '✗ ' + data.error;
        }
        
        setTimeout(() => {
            statusDiv.className = 'status-message';
            statusDiv.textContent = '';
        }, 5000);
        
    } catch (error) {
        hideLoading();
        alert('Lỗi: ' + error.message);
    }
}

async function loadRegisteredUsers() {
    try {
        const response = await fetch('/api/get-registered-users');
        const data = await response.json();
        
        if (data.success) {
            const userList = document.getElementById('user-list');
            userList.innerHTML = '';
            
            if (data.users.length === 0) {
                userList.innerHTML = '<li>Chưa có người dùng nào</li>';
            } else {
                data.users.forEach(user => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <span>${user.name}</span>
                        <span style="color: #667eea; font-weight: bold;">${user.image_count} ảnh</span>
                    `;
                    userList.appendChild(li);
                });
            }
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Face Recognition Functions
async function startRecognizeCamera() {
    try {
        recognizeStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        document.getElementById('recognize-video').srcObject = recognizeStream;
    } catch (error) {
        alert('Không thể truy cập camera: ' + error.message);
    }
}

function stopRecognizeCamera() {
    if (recognizeStream) {
        recognizeStream.getTracks().forEach(track => track.stop());
        document.getElementById('recognize-video').srcObject = null;
        recognizeStream = null;
    }
}

async function recognizeFace() {
    if (!recognizeStream) {
        alert('Vui lòng bật camera trước!');
        return;
    }
    
    const video = document.getElementById('recognize-video');
    const canvas = document.getElementById('recognize-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg');
    
    showLoading('Đang nhận diện khuôn mặt...');
    
    try {
        const response = await fetch('/api/face-recognition/recognize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        const resultDiv = document.getElementById('recognize-result');
        
        if (data.success) {
            resultDiv.innerHTML = `
                <h3>Kết quả nhận diện:</h3>
                <p style="font-size: 1.5em; color: #28a745; font-weight: bold;">
                    ${data.result}
                </p>
            `;
        } else {
            resultDiv.innerHTML = `
                <h3>Lỗi:</h3>
                <p style="color: #dc3545;">${data.error}</p>
            `;
        }
        
    } catch (error) {
        hideLoading();
        alert('Lỗi: ' + error.message);
    }
}

// DeepFace Functions - Upload & Paste
function setupDeepfaceUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('image-upload');
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleImageFile(file);
        }
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImageFile(file);
        } else {
            alert('Vui lòng chỉ kéo thả file ảnh!');
        }
    });
    
    // Paste from clipboard (Ctrl+V)
    document.addEventListener('paste', (e) => {
        // Chỉ xử lý khi đang ở tab DeepFace
        const deepfaceTab = document.getElementById('deepface-tab');
        if (!deepfaceTab.classList.contains('active')) {
            return;
        }
        
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                handleImageFile(blob);
                e.preventDefault();
                break;
            }
        }
    });
}

function handleImageFile(file) {
    const reader = new FileReader();
    
    reader.onload = (e) => {
        deepfaceImageData = e.target.result;
        
        // Show preview
        const previewContainer = document.getElementById('image-preview-container');
        const previewImage = document.getElementById('image-preview');
        const uploadArea = document.getElementById('upload-area');
        
        previewImage.src = deepfaceImageData;
        previewContainer.style.display = 'block';
        uploadArea.style.display = 'none';
    };
    
    reader.readAsDataURL(file);
}

function clearImage() {
    deepfaceImageData = null;
    
    const previewContainer = document.getElementById('image-preview-container');
    const uploadArea = document.getElementById('upload-area');
    const resultDiv = document.getElementById('deepface-result');
    
    previewContainer.style.display = 'none';
    uploadArea.style.display = 'block';
    resultDiv.innerHTML = '';
    
    // Reset file input
    document.getElementById('image-upload').value = '';
}

async function analyzeFaceFromImage() {
    if (!deepfaceImageData) {
        alert('Vui lòng tải lên hoặc paste ảnh trước!');
        return;
    }
    
    showLoading('Đang phân tích khuôn mặt...');
    
    try {
        const response = await fetch('/api/deepface/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: deepfaceImageData
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        const resultDiv = document.getElementById('deepface-result');
        
        if (data.success) {
            const result = data.result;
            resultDiv.innerHTML = `
                <h3>Kết quả phân tích:</h3>
                <div class="analysis-grid">
                    <div class="analysis-item">
                        <h4>👤 Giới tính</h4>
                        <div class="value">${result.gender}</div>
                        <div class="confidence">${result.gender_confidence}%</div>
                    </div>
                    <div class="analysis-item">
                        <h4>🎂 Tuổi</h4>
                        <div class="value">${result.age} tuổi</div>
                    </div>
                    <div class="analysis-item">
                        <h4>😊 Cảm xúc</h4>
                        <div class="value">${result.emotion}</div>
                        <div class="confidence">${result.emotion_confidence}%</div>
                    </div>
                    <div class="analysis-item">
                        <h4>🌍 Dân tộc</h4>
                        <div class="value">${result.race}</div>
                        <div class="confidence">${result.race_confidence}%</div>
                    </div>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <h3>Lỗi:</h3>
                <p style="color: #dc3545;">${data.error}</p>
            `;
        }
        
    } catch (error) {
        hideLoading();
        alert('Lỗi: ' + error.message);
    }
}
