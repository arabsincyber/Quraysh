import re
import requests

def scan_wallet(address: str) -> dict:
    result = {
        "address": address,
        "type": "غير معروف",
        "valid": False,
        "network": "غير معروف",
        "balance": "غير متاح",
        "warnings": []
    }

    # 1. Bitcoin (BTC)
    if re.match(r'^(1|3)[a-zA-HJ-NP-Z0-9]{25,34}$', address) or re.match(r'^bc1[a-zA-HJ-NP-Z0-9]{39,59}$', address):
        result["type"] = "Bitcoin (BTC)"
        result["valid"] = True
        result["network"] = "Bitcoin Mainnet"
        try:
            res = requests.get(f"https://blockchain.info/q/addressbalance/{address}", timeout=10)
            if res.status_code == 200:
                satoshis = int(res.text)
                btc = satoshis / 100000000
                result["balance"] = f"{btc:.8f} BTC"
        except: pass

    # 2. Ethereum (ETH) & Binance Coin (BNB)
    elif re.match(r'^0x[a-fA-F0-9]{40}$', address):
        result["type"] = "Ethereum (ETH) / Binance (BNB)"
        result["valid"] = True
        result["network"] = "EVM Mainnet (ETH/BNB)"
        result["balance"] = "غير متاح (يحتاج مفتاح API)"

    # 3. Tron (TRX)
    elif re.match(r'^T[a-zA-HJ-NP-Z0-9]{33}$', address):
        result["type"] = "Tron (TRX)"
        result["valid"] = True
        result["network"] = "Tron Mainnet"
        result["balance"] = "غير متاح (يحتاج مفتاح API)"

    # 4. Ripple (XRP)
    elif re.match(r'^r[1-9A-HJ-NP-Za-km-z]{24,34}$', address):
        result["type"] = "Ripple (XRP)"
        result["valid"] = True
        result["network"] = "XRP Ledger"

    # 5. Dogecoin (DOGE)
    elif re.match(r'^D[5-9A-HJ-NP-U][1-9A-HJ-NP-Za-km-z]{32}$', address):
        result["type"] = "Dogecoin (DOGE)"
        result["valid"] = True
        result["network"] = "Dogecoin Mainnet"

    # 6. Litecoin (LTC)
    elif re.match(r'^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$', address):
        result["type"] = "Litecoin (LTC)"
        result["valid"] = True
        result["network"] = "Litecoin Mainnet"

    # 7. Solana (SOL)
    elif re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address) and not address.startswith('0x') and not address.startswith('T'):
        result["type"] = "Solana (SOL) أو عملة أخرى (Base58)"
        result["valid"] = True
        result["network"] = "Solana Mainnet (محتمل)"

    else:
        result["warnings"].append("العنوان غير صالح أو غير معروف.")
        
    return result
