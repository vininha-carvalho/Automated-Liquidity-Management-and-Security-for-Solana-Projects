import os
import yaml
from typing import Dict, Any
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_path = Path(os.environ.get('CQ_CONFIG', '~/.cryptoquantum/config.yml'))
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Loading config with structure check"""
        try:
            with open(self.config_path.expanduser(), 'r') as f:
                config = yaml.safe_load(f)
                
            # Валидация обязательных полей
            assert 'exchanges' in config, "Missing 'exchanges' section"
            assert 'risk_management' in config, "Missing 'risk_management'"
            
            return config
        except FileNotFoundError:
            raise RuntimeError("Config file not found. Run 'cqpro init' first")

    def get_exchange_creds(self, exchange: str) -> Dict[str, str]:
        """Securely obtain API keys"""
        return {
            'api_key': os.environ.get(f"{exchange}_API_KEY"),  # Рекомендуемо использовать env vars
            'api_secret': os.environ.get(f"{exchange}_API_SECRET")
        }

# example config file: ~/.cryptoquantum/config.yml
"""
exchanges:
  binance:
    enabled: true
    trade_fee: 0.1%
    type: spot
  uniswap_v3:
    enabled: true
    pools: [USDC/ETH, BTC/ETH]

risk_management:
  max_risk_per_trade: 2%
  stop_loss:
    mode: dynamic
    sensitivity: medium

ai_settings:
  prediction_model: lstm_v3
  retrain_interval: 24h

security:
  tpm_enabled: true
  tor_proxy: socks5://localhost:9050
"""
