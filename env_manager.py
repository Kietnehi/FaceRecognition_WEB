"""
Script tự động quản lý môi trường Anaconda cho Face Recognition Project
(Phiên bản: Smart Install + Fix AttributeError cho app.py)
"""
import subprocess
import sys
import os
import json
import platform
# Mapping package: tên trong config → tên thực tế trong pip freeze
PACKAGE_NAME_MAPPING = {
    # Face Recognition
    'face_recognition': 'face-recognition',
    'pillow': 'Pillow',
    'opencv-python': 'opencv-python',
    'dlib': 'dlib',
    'numpy': 'numpy',

    # DeepFace
    'deepface': 'deepface',
    'tf-keras': 'tf_keras',  # map tên script → pip freeze thực tế
    'tensorflow': 'tensorflow',
}
class CondaEnvironmentManager:
    """Quản lý môi trường conda: Chỉ cài đặt những gói còn thiếu"""
    
    def __init__(self):
        self.envs = {
            'face_recognition': {
                # Dlib cài qua conda-forge để tránh lỗi build, các gói khác qua pip
                'conda_packages': ['dlib', 'pip'], 
                'pip_packages': ['face_recognition', 'pillow', 'opencv-python'],
                'python_version': '3.9'
            },
            'deepface_recognition': {
                'conda_packages': ['pip'],
                'pip_packages': ['deepface', 'opencv-python', 'tf-keras'],
                'python_version': '3.9'
            }
        }
        self.is_windows = platform.system() == 'Windows'
    
    def _run_conda(self, cmd_list, check=True, capture_output=False):
        """Hàm helper chạy lệnh hệ thống"""
        try:
            # Trên Windows cần nối chuỗi lệnh nếu dùng shell=True
            cmd_str = ' '.join(cmd_list) if self.is_windows else None
            
            kwargs = {
                'shell': self.is_windows,
                'text': True,
                'encoding': 'utf-8', # Fix lỗi ký tự lạ trên Windows
                'check': check
            }
            
            if capture_output:
                kwargs['capture_output'] = True

            if self.is_windows:
                return subprocess.run(cmd_str, **kwargs)
            else:
                return subprocess.run(cmd_list, **kwargs)
                
        except subprocess.CalledProcessError as e:
            if check:
                raise e
            return e

    def get_installed_packages(self, env_name):
        """Lấy danh sách các package đã cài (dùng pip list --json)"""
        installed = set()
        try:
            result = self._run_conda(
                ['conda', 'run', '-n', env_name, 'pip', 'list', '--format=json'],
                capture_output=True, check=True
            )
            data = json.loads(result.stdout)
            for pkg in data:
                installed.add(pkg['name'].lower())
            return installed
        except Exception:
            # Nếu lệnh lỗi (do chưa có pip hoặc env hỏng), trả về rỗng để script tự cài lại
            return set()

    def check_env_exists(self, env_name):
        """Kiểm tra môi trường tồn tại"""
        try:
            res = self._run_conda(['conda', 'env', 'list', '--json'], capture_output=True)
            envs = json.loads(res.stdout)['envs']
            env_names = [os.path.basename(e) for e in envs]
            return env_name in env_names
        except:
            return False

    def create_env(self, env_name):
        """Tạo môi trường mới"""
        config = self.envs[env_name]
        ver = config['python_version']
        print(f"➜ Đang tạo môi trường '{env_name}' (Python {ver} & pip)...")
        # Luôn cài pip ngay khi tạo
        self._run_conda(['conda', 'create', '-n', env_name, f'python={ver}', 'pip', '-y'])

    def install_missing_packages(self, env_name, missing_conda, missing_pip):
        """Cài đặt bổ sung các gói còn thiếu"""
        
        # 1. Cài Conda packages (Ưu tiên)
        if missing_conda:
            print(f"➜ Đang cài qua Conda (kênh conda-forge): {', '.join(missing_conda)}")
            # Dùng channel conda-forge để cài dlib tốt nhất
            cmd = ['conda', 'install', '-n', env_name, '-c', 'conda-forge'] + missing_conda + ['-y']
            self._run_conda(cmd)

        # 2. Cài Pip packages
        if missing_pip:
            print(f"➜ Đang cài qua Pip: {', '.join(missing_pip)}")
            for pkg in missing_pip:
                print(f"   - Installing {pkg}...")
                self._run_conda(['conda', 'run', '-n', env_name, 'pip', 'install', pkg])

    def setup_environment(self, env_name):
        """Quy trình chính: Check Env -> Check Packages -> Install Missing"""
        print(f"\n{'='*60}")
        print(f"KIỂM TRA MÔI TRƯỜNG: {env_name}")
        print(f"{'='*60}")
        
        # 1. Check/Create Environment
        if not self.check_env_exists(env_name):
            print(f"✗ Môi trường chưa tồn tại.")
            self.create_env(env_name)
        else:
            print(f"✓ Môi trường '{env_name}' đã tồn tại.")

        # 2. Get Installed Packages
        installed = self.get_installed_packages(env_name)
        
        config = self.envs[env_name]
        
        # 3. Tính toán các gói thiếu (Diff)
        # Lọc tên gói conda (vd: dlib=19 -> dlib)
        missing_conda = [p for p in config.get('conda_packages', []) 
                         if p.split('=')[0].lower() not in installed]
        
        # Lọc tên gói pip (vd: deepface==0.0.96 -> deepface)
        missing_pip = [
            p for p in config.get('pip_packages', [])
            if PACKAGE_NAME_MAPPING.get(p, p).lower() not in installed
        ]

        # 4. Xử lý
        if not missing_conda and not missing_pip:
            print(f"✓ TẤT CẢ THƯ VIỆN ĐÃ ĐẦY ĐỦ.")
        else:
            print(f"⚠ Phát hiện thư viện thiếu. Đang tự động bổ sung...")
            try:
                self.install_missing_packages(env_name, missing_conda, missing_pip)
                print("✓ Cài đặt bổ sung hoàn tất.")
            except Exception as e:
                print(f"✗ Lỗi khi cài đặt: {e}")
                return False

        print(f"{'='*60}\n")
        return True

    # === HÀM QUAN TRỌNG CHO APP.PY ===
    def check_packages_installed(self, env_name):
        """
        Hàm này được app.py gọi để KIỂM TRA packages đã cài đủ chưa.
        CHỈ kiểm tra, KHÔNG tự động cài đặt.
        Trả về True nếu tất cả packages đã đầy đủ.
        """
        try:
            # Kiểm tra env có tồn tại không
            if not self.check_env_exists(env_name):
                return False
            
            # Lấy danh sách packages đã cài
            installed = self.get_installed_packages(env_name)
            if not installed:  # Nếu không lấy được danh sách -> môi trường có vấn đề
                return False
            
            config = self.envs[env_name]
            
            # Kiểm tra conda packages
            missing_conda = [p for p in config.get('conda_packages', []) 
                             if p.split('=')[0].lower() not in installed]
            
            # Kiểm tra pip packages
            missing_pip = [
                p for p in config.get('pip_packages', [])
                if PACKAGE_NAME_MAPPING.get(p.split('=')[0], p.split('=')[0]).lower() not in installed
            ]
            
            # Trả về True nếu KHÔNG còn gói nào thiếu
            return len(missing_conda) == 0 and len(missing_pip) == 0
            
        except Exception as e:
            print(f"Lỗi khi kiểm tra packages {env_name}: {e}")
            return False

    def setup_all_environments(self):
        for env_name in self.envs.keys():
            self.setup_environment(env_name)

def main():
    manager = CondaEnvironmentManager()
    
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        if env_name in manager.envs:
            manager.setup_environment(env_name)
        else:
            print(f"Môi trường '{env_name}' không hợp lệ!")
            print(f"Danh sách: {', '.join(manager.envs.keys())}")
    else:
        # Chạy thiết lập tất cả
        manager.setup_all_environments()

if __name__ == "__main__":
    main()