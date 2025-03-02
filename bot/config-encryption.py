# AES-256 encryption for API keys
from Crypto.Cipher import AES
import base64

def encrypt_config(data: str, key: str) -> str:
    cipher = AES.new(key.encode(), AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt_config(encrypted: str, key: str) -> str:
    data = base64.b64decode(encrypted)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(key.encode(), AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
