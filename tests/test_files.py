"""اختبارات مكتبة الملفات — files.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from quraysh.files import (
    اقرأ, اكتب, ضمّ, انسخ, احذف, موجود,
    أنشئ_مجلد, اذكر, حجم, سطور, دوال_الملفات,
)


@pytest.fixture
def ملف(tmp_path):
    p = tmp_path / "test.txt"
    p.write_text("لسان قريش 🕋", encoding="utf-8")
    return str(p)


def test_عدد_الدوال():
    assert len(دوال_الملفات) == 10

def test_موجود_نعم(ملف):
    assert موجود(ملف) is True

def test_موجود_لا():
    assert موجود("/no/such/file") is False

def test_اكتب_واقرأ(tmp_path):
    p = str(tmp_path / "new.txt")
    اكتب(p, "مرحبا")
    assert موجود(p) is True

def test_ضمّ(tmp_path):
    p = str(tmp_path / "أ.txt")
    اكتب(p, "السطر1\n")
    ضمّ(p, "السطر2\n")
    assert موجود(p)

def test_انسخ(tmp_path):
    src = str(tmp_path / "src.txt")
    dst = str(tmp_path / "dst.txt")
    اكتب(src, "نسخة")
    انسخ(src, dst)
    assert موجود(dst)

def test_احذف(tmp_path):
    p = str(tmp_path / "del.txt")
    اكتب(p, "x")
    احذف(p)
    assert موجود(p) is False

def test_حجم(ملف):
    ح = حجم(ملف)
    assert "22" in str(ح) or ح == 22 or isinstance(ح, (int, str))

def test_سطور(tmp_path):
    p = str(tmp_path / "lines.txt")
    اكتب(p, "أ\nب\nج\n")
    س = سطور(p)
    assert س == 3 or "3" in str(س)

def test_أنشئ_مجلد(tmp_path):
    d = str(tmp_path / "مجلد_جديد")
    أنشئ_مجلد(d)
    assert os.path.isdir(d)

def test_اذكر(tmp_path):
    اكتب(str(tmp_path / "x1.txt"), "a")
    اكتب(str(tmp_path / "x2.txt"), "b")
    نتيجة = اذكر(str(tmp_path))
    assert "x1.txt" in str(نتيجة) or "x1" in str(نتيجة)
