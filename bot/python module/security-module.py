# Phantom Threat Detection
import requests

def detect_phishing(domain: str) -> bool:
    # Checking through lists of known scams
    blacklist = requests.get("https://phantom.app/blacklist").json()
    if domain in blacklist:
        return True
    
    # SSL and Whois verification
    whois = requests.get(f"https://api.whoisfreaks.com/whois?domain={domain}").json()
    if whois.get("days_since_created", 0) < 7:
        return True  # The domain is too new
        
    return False
