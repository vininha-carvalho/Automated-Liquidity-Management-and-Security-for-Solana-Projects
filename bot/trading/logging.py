# Recording all activities in encrypted CSV
import csv
from Crypto.Cipher import AES

def log_trade(action: str, amount: float, tx_hash: str):
    key = b'super-secret-key-32'  # Generated from Ledger
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    
    data = f"{action},{amount},{tx_hash}"
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    
    with open("trades.enc", "ab") as f:
        f.write(nonce + tag + ciphertext)
