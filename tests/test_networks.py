"""اختبارات مكتبة الشبكات — networks.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from quraysh.networks import (
    استعلم_dns, افتح_منفذ, ip_الحالي, بينغ, دوال_الشبكة,
)


def test_عدد_الدوال():
    assert len(دوال_الشبكة) == 8

def test_dns_google():
    نتيجة = استعلم_dns("google.com")
    assert isinstance(نتيجة, dict)
    assert "ip" in نتيجة
    assert نتيجة["domain"] == "google.com"

def test_dns_نطاق_خطأ():
    نتيجة = استعلم_dns("هذا.نطاق.غير.موجود.xyz")
    assert isinstance(نتيجة, str)  # رسالة خطأ

def test_tcp_google_443():
    نتيجة = افتح_منفذ("google.com", 443)
    assert "مفتوح" in نتيجة

def test_tcp_منفذ_مغلق():
    نتيجة = افتح_منفذ("google.com", 99999, timeout=1)
    assert "مغلق" in نتيجة or "خطأ" in نتيجة

def test_ip_الحالي():
    نتيجة = ip_الحالي()
    assert "IP:" in نتيجة or "خطأ" in نتيجة

def test_bing_يعمل():
    نتيجة = بينغ("8.8.8.8", count=1)
    assert "8.8.8.8" in نتيجة or "خطأ" in نتيجة

def test_دوال_الشبكة_كلها_callable():
    for اسم, دالة in دوال_الشبكة.items():
        assert callable(دالة), f"{اسم} ليس قابل للاستدعاء"
