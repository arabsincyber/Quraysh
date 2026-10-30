import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from quraysh.intel import wallet_scanner

def test_bitcoin_valid():
    """اختبار محفظة بيتكوين صالحة (بدون اتصال)"""
    result = wallet_scanner.scan_wallet("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
    assert result["valid"] == True
    assert result["type"] == "Bitcoin (BTC)"

def test_ethereum_valid():
    """اختبار محفظة إيثيريوم صالحة (بدون اتصال)"""
    result = wallet_scanner.scan_wallet("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    assert result["valid"] == True
    assert result["type"] == "Ethereum (ETH)"

def test_tron_valid():
    """اختبار محفظة ترون صالحة (بدون اتصال)"""
    result = wallet_scanner.scan_wallet("TXFBqBbqJommqZf7BV8NNYzePh97UmJodJ")
    assert result["valid"] == True
    assert result["type"] == "Tron (TRX)"

def test_invalid_wallet():
    """اختبار عنوان غير صالح"""
    result = wallet_scanner.scan_wallet("invalid_wallet_123")
    assert result["valid"] == False
    assert result["type"] == "غير معروف"
