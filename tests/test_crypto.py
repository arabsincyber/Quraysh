"""اختبارات مكتبة التشفير — crypto.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from quraysh.crypto import (
    بصمة_نص, بصمة_ملف, توقيع_hmac, تحقق_hmac,
    ترميز_base64, فك_base64, مفتاح_عشوائي, مقارنة_آمنة,
    بصمة_سلسلة, تشفير_xor, فك_xor,
)


def test_بصمة_نص_ثابتة():
    assert بصمة_نص("السلام") == بصمة_نص("السلام")

def test_بصمة_نص_مختلفة():
    assert بصمة_نص("السلام") != بصمة_نص("سلام")

def test_بصمة_نص_sha256_الطول():
    assert len(بصمة_نص("قريش")) == 64

def test_بصمة_ملف(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("لسان قريش", encoding="utf-8")
    assert len(بصمة_ملف(str(f))) == 64

def test_hmac_تحقق():
    توقيع = توقيع_hmac("مرحبا", "مفتاح")
    assert تحقق_hmac("مرحبا", "مفتاح", توقيع) is True

def test_hmac_رفض():
    توقيع = توقيع_hmac("مرحبا", "مفتاح")
    assert تحقق_hmac("مرحبا", "مفتاح_خطأ", توقيع) is False

def test_base64_ذهاب_وعودة():
    نص = "لسان قريش 🕋"
    assert فك_base64(ترميز_base64(نص)) == نص

def test_base64_عربي():
    assert ترميز_base64("قريش") != "قريش"

def test_مفتاح_عشوائي_طول():
    assert len(مفتاح_عشوائي(16)) == 32  # hex = ضعف الطول
    assert مفتاح_عشوائي() != مفتاح_عشوائي()  # عشوائية

def test_مقارنة_آمنة():
    assert مقارنة_آمنة("abc", "abc") is True
    assert مقارنة_آمنة("abc", "abd") is False

def test_بصمة_سلسلة():
    assert بصمة_سلسلة("أ", "ب") == بصمة_سلسلة("أ", "ب")
    assert بصمة_سلسلة("أ", "ب") != بصمة_سلسلة("أ", "ج")

def test_xor_ذهاب_وعودة():
    نص = "لسان قريش 123"
    مفتاح = "سر"
    مشفر = تشفير_xor(نص, مفتاح)
    assert مشفر != نص
    assert فك_xor(مشفر, مفتاح) == نص

def test_xor_عربي_utf8():
    نص = "🕋"
    مفتاح = "مفتاح"
    assert فك_xor(تشفير_xor(نص, مفتاح), مفتاح) == نص
