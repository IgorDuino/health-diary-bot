from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
import base64
from dtb.settings import SECRET_KEY


def get_key(password: str) -> bytes:
    return SHA256.new(password.encode()).digest()


def encrypt_data(data: str) -> str:
    key = get_key(SECRET_KEY)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = cipher.iv
    return base64.b64encode(iv + ct_bytes).decode("utf-8")


def decrypt_data(data: str) -> str:
    key = get_key(SECRET_KEY)
    data = base64.b64decode(data)
    iv = data[: AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(data[AES.block_size :]), AES.block_size)
    return pt.decode("utf-8")
