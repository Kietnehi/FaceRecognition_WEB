"""
Script tự động quản lý môi trường Anaconda cho Face Recognition Project
"""
import subprocess
import sys
import os
import json
import platform

class CondaEnvironmentManager:
    """Quản lý môi trường conda cho dự án"""
    
    def __init__(self):
        self.envs = {
            'face_recognition': {
                'packages': ['face_recognition', 'dlib', 'numpy', 'pillow', 'opencv-python'],
                'python_version': '3.9'
            },
            'deepface_recognition': {
                'packages': ['deepface==0.0.96', 'opencv-python==4.12.0.88', 'tf-keras'],
                'python_version': '3.9'
            }
        }
        self.is_windows = platform.system() == 'Windows'
    
    def _run_conda_command(self, cmd_list, **kwargs):
        """Chạy lệnh conda với cấu hình phù hợp cho từng OS"""
        if self.is_windows:
            # Trên Windows, cần shell=True để tìm conda trong PATH
            cmd_str = ' '.join(cmd_list)
            return subprocess.run(cmd_str, shell=True, **kwargs)
        else:
            return subprocess.run(cmd_list, **kwargs)
    
    def check_conda_installed(self):
        """Kiểm tra conda đã được cài đặt chưa"""
        try:
            self._run_conda_command(['conda', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_conda_envs(self):
        """Lấy danh sách các môi trường conda hiện có"""
        try:
            result = self._run_conda_command(
                ['conda', 'env', 'list', '--json'],
                capture_output=True, text=True, check=True
            )
            env_data = json.loads(result.stdout)
            env_names = [os.path.basename(path) for path in env_data['envs']]
            return env_names
        except Exception as e:
            print(f"Lỗi khi lấy danh sách môi trường: {e}")
            return []
    
    def check_env_exists(self, env_name):
        """Kiểm tra môi trường có tồn tại không"""
        envs = self.get_conda_envs()
        return env_name in envs
    
    def create_environment(self, env_name):
        """Tạo môi trường conda mới"""
        if env_name not in self.envs:
            print(f"Môi trường {env_name} không được định nghĩa!")
            return False
        
        env_config = self.envs[env_name]
        python_version = env_config['python_version']
        
        print(f"Đang tạo môi trường {env_name} với Python {python_version}...")
        
        try:
            # Tạo môi trường với Python version
            self._run_conda_command(
                ['conda', 'create', '-n', env_name, f'python={python_version}', '-y'],
                check=True
            )
            print(f"✓ Đã tạo môi trường {env_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Lỗi khi tạo môi trường {env_name}: {e}")
            return False
    
    def install_packages(self, env_name):
        """Cài đặt các package cần thiết vào môi trường"""
        if env_name not in self.envs:
            print(f"Môi trường {env_name} không được định nghĩa!")
            return False
        
        packages = self.envs[env_name]['packages']
        
        print(f"Đang cài đặt packages cho {env_name}...")
        
        try:
            # Cài đặt từng package
            for package in packages:
                print(f"  - Đang cài đặt {package}...")
                self._run_conda_command(
                    ['conda', 'run', '-n', env_name, 'pip', 'install', package],
                    check=True, capture_output=True
                )
                print(f"  ✓ Đã cài đặt {package}")
            
            print(f"✓ Hoàn thành cài đặt packages cho {env_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Lỗi khi cài đặt packages: {e}")
            return False
    
    def check_packages_installed(self, env_name):
        """Kiểm tra các package đã được cài đặt chưa"""
        if env_name not in self.envs:
            return False
        
        try:
            result = self._run_conda_command(
                ['conda', 'run', '-n', env_name, 'pip', 'list'],
                capture_output=True, text=True, check=True
            )
            installed_packages = result.stdout.lower()
            
            packages = self.envs[env_name]['packages']
            for package in packages:
                # Lấy tên package (bỏ version nếu có)
                package_name = package.split('==')[0].split('>=')[0].split('<=')[0].strip()
                if package_name.lower() not in installed_packages:
                    return False
            return True
        except Exception as e:
            print(f"Lỗi khi kiểm tra packages: {e}")
            return False
    
    def setup_environment(self, env_name):
        """Thiết lập môi trường: tạo nếu chưa có, cài packages nếu thiếu"""
        print(f"\n{'='*60}")
        print(f"Thiết lập môi trường: {env_name}")
        print(f"{'='*60}")
        
        # Kiểm tra conda
        if not self.check_conda_installed():
            print("✗ Conda chưa được cài đặt. Vui lòng cài đặt Anaconda hoặc Miniconda.")
            return False
        
        # Kiểm tra môi trường có tồn tại không
        if not self.check_env_exists(env_name):
            print(f"Môi trường {env_name} chưa tồn tại.")
            if not self.create_environment(env_name):
                return False
        else:
            print(f"✓ Môi trường {env_name} đã tồn tại")
        
        # Kiểm tra packages
        if not self.check_packages_installed(env_name):
            print(f"Packages chưa đầy đủ trong {env_name}")
            if not self.install_packages(env_name):
                return False
        else:
            print(f"✓ Tất cả packages đã được cài đặt")
        
        print(f"{'='*60}")
        print(f"✓ Môi trường {env_name} đã sẵn sàng!")
        print(f"{'='*60}\n")
        return True
    
    def setup_all_environments(self):
        """Thiết lập tất cả các môi trường"""
        print("\n" + "="*60)
        print("BẮT ĐẦU THIẾT LẬP TẤT CẢ MÔI TRƯỜNG")
        print("="*60)
        
        success = True
        for env_name in self.envs.keys():
            if not self.setup_environment(env_name):
                success = False
        
        if success:
            print("\n✓ Tất cả môi trường đã được thiết lập thành công!")
        else:
            print("\n✗ Có lỗi xảy ra khi thiết lập môi trường!")
        
        return success

def main():
    """Hàm chính"""
    manager = CondaEnvironmentManager()
    
    if len(sys.argv) > 1:
        env_name = sys.argv[1]
        if env_name in manager.envs:
            manager.setup_environment(env_name)
        else:
            print(f"Môi trường '{env_name}' không hợp lệ!")
            print(f"Các môi trường có sẵn: {', '.join(manager.envs.keys())}")
    else:
        # Thiết lập tất cả môi trường
        manager.setup_all_environments()

if __name__ == "__main__":
    main()
