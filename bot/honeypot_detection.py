# Token verification on honeypot via Birdeye API + contract analysis
import requests
from solana.rpc.api import Client

def is_honeypot(token_address: str) -> bool:
    try:
        # 1. Checking via Birdeye
        birdeye_api = f"https://api.birdeye.so/token/{token_address}?chain=solana"
        response = requests.get(birdeye_api).json()
        if response.get("isHoneypot"):
            return True

        # 2. Contract analysis
        client = Client("https://api.mainnet-beta.solana.com")
        acc_info = client.get_account_info(token_address)
        owner = acc_info["result"]["owner"]
        
        # Blacklist of suspicious programs
        scam_programs = {"HONEYPOT_PROGRAM_ID", "FAKE_MINT_PROGRAM"}
        return owner in scam_programs

    except Exception as e:
        # Fail-safe: error block
        return True 
