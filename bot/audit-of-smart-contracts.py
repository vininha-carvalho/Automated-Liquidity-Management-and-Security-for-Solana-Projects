# Automatic auditing via Otterscan API
def audit_contract(token_address: str) -> dict:
    try:
        report = {
            "verified": False,
            "risks": []
        }
        
        # Code verification check
        otterscan_api = f"https://api.otterscan.io/audit/{token_address}"
        data = requests.get(otterscan_api).json()
        
        if data["verified"]:
            report["verified"] = True
        else:
            report["risks"].append("Unverified contract")
        
        # Search for vulnerabilities
        if data.get("mint_authority_centralized"):
            report["risks"].append("Centralized mint")
            
        return report
    except:
        return {"error": "Audit failed"}
