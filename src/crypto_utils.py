import os
import shutil
import base64
import tarfile
import tempfile
import uuid
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

PROFILE_DIR = os.path.expanduser("~/.mychrome_data")
ENC_PROFILE_FILE = os.path.join(PROFILE_DIR, "profile.enc")
AUTH_FILE = os.path.join(PROFILE_DIR, "auth.key")
SALT_FILE = os.path.join(PROFILE_DIR, "session.salt")

_temp_unencrypted_dir = None

def get_machine_id():
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode('utf-8')).hexdigest()[:16]

def get_or_create_salt():
    if not os.path.exists(SALT_FILE):
        new_salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(new_salt)
        return new_salt
    with open(SALT_FILE, "rb") as f:
        return f.read()

def derive_fernet_key(password: str, salt: bytes) -> bytes:
    machine_id = get_machine_id()
    combined_salt = salt + machine_id.encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=combined_salt,
        iterations=100_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    return key

def hash_password(password: str, salt: bytes) -> str:
    key = derive_fernet_key(password, salt)
    return hashlib.sha256(key).hexdigest()

def check_auth_integrity():
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR, exist_ok=True)
        return "SETUP"
    
    if os.path.exists(AUTH_FILE) and os.path.exists(SALT_FILE):
        return "LOGIN"
    elif os.path.exists(AUTH_FILE) or os.path.exists(SALT_FILE) or os.path.exists(ENC_PROFILE_FILE):
        return "CORRUPTED"
    else:
        return "SETUP"

def decrypt_and_mount_profile(password: str) -> str:
    global _temp_unencrypted_dir
    salt = get_or_create_salt()
    key = derive_fernet_key(password, salt)
    fernet = Fernet(key)
    
    _temp_unencrypted_dir = tempfile.mkdtemp(prefix="mychrome_runtime_")
    profile_target = os.path.join(_temp_unencrypted_dir, "browser_profile")
    os.makedirs(profile_target, exist_ok=True)
    
    if os.path.exists(ENC_PROFILE_FILE):
        with open(ENC_PROFILE_FILE, "rb") as f:
            encrypted_data = f.read()
        
        decrypted_tar_bytes = fernet.decrypt(encrypted_data)
        
        tar_path = os.path.join(_temp_unencrypted_dir, "temp_profile.tar")
        with open(tar_path, "wb") as f:
            f.write(decrypted_tar_bytes)
            
        with tarfile.open(tar_path, "r") as tar:
            tar.extractall(path=profile_target)
            
        os.remove(tar_path)
        
    return profile_target

def encrypt_and_unmount_profile(password: str):
    global _temp_unencrypted_dir
    if not _temp_unencrypted_dir or not os.path.exists(_temp_unencrypted_dir):
        return
        
    profile_target = os.path.join(_temp_unencrypted_dir, "browser_profile")
    if os.path.exists(profile_target):
        salt = get_or_create_salt()
        key = derive_fernet_key(password, salt)
        fernet = Fernet(key)
        
        tar_path = os.path.join(_temp_unencrypted_dir, "temp_profile.tar")
        with tarfile.open(tar_path, "w") as tar:
            for item in os.listdir(profile_target):
                item_path = os.path.join(profile_target, item)
                tar.add(item_path, arcname=item)
                
        with open(tar_path, "rb") as f:
            tar_bytes = f.read()
            
        encrypted_bytes = fernet.encrypt(tar_bytes)
        
        with open(ENC_PROFILE_FILE, "wb") as f:
            f.write(encrypted_bytes)
            
    shutil.rmtree(_temp_unencrypted_dir, ignore_errors=True)
    _temp_unencrypted_dir = None

def get_runtime_profile_dir():
    global _temp_unencrypted_dir
    if _temp_unencrypted_dir:
        return os.path.join(_temp_unencrypted_dir, "browser_profile")
    return os.path.expanduser("~/.mychrome_data/browser_profile")
