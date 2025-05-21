import json
import os
from flask import current_app

def update_app_name(new_name):
    """
    Fungsi untuk mengupdate nama aplikasi di config.json
    Return: Tuple (status, message)
    """
    config_path = os.path.join(current_app.static_folder, 'config.json')
    
    try:
        # Baca config saat ini
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validasi input
        if not isinstance(new_name, str) or len(new_name.strip()) == 0:
            return False, "Nama harus berupa string tidak kosong"
        
        # Update config
        config['app_name'] = new_name.strip()
        
        # Simpan perubahan
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            
        return True, f"Nama aplikasi berhasil diubah menjadi: {new_name}"
    
    except FileNotFoundError:
        return False, "File config.json tidak ditemukan"
    except json.JSONDecodeError:
        return False, "Format config.json tidak valid"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_current_app_name():
    """
    Fungsi untuk mendapatkan nama aplikasi saat ini
    Return: Tuple (status, nama_app/error_message)
    """
    config_path = os.path.join(current_app.static_folder, 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return True, config.get('app_name', '__name__')
    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == '__main__':
    # Untuk testing standalone (tanpa Flask)
    import sys
    if len(sys.argv) > 1:
        result, message = update_app_name(sys.argv[1])
        print(message)
    else:
        print("Usage: python update_name.py <new_app_name>")