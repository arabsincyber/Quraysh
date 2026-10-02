"""اختبارات مكتبة BASIC — basic.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from quraysh.basic import (
    كرر_من_إلى, كرر_خطوة, طول_نص, جزء_نص,
    يسار, يمين, رمز, حرف, عشوائي,
    تقريب_عدد, صحيح, مطلق_عدد, إشارة, دوال_BASIC,
)


def test_عدد_الدوال():
    assert len(دوال_BASIC) == 17

def test_كرر_من_إلى():
    assert كرر_من_إلى(1, 5) == [1, 2, 3, 4, 5]

def test_كرر_خطوة():
    # الدالة تشمل النهاية
    assert كرر_خطوة(0, 10, 2) == [0, 2, 4, 6, 8, 10]

def test_طول_نص():
    assert طول_نص("السلام") == 6

def test_طول_نص_فارغ():
    assert طول_نص("") == 0

def test_جزء_نص():
    assert جزء_نص("السلام عليكم", 0, 6) == "السلام"

def test_يسار():
    assert يسار("السلام", 3) == "الس"

def test_يمين():
    assert يمين("السلام", 3) == "لام"

def test_رمز():
    assert رمز("أ") == ord("أ")

def test_حرف():
    assert حرف(ord("أ")) == "أ"

def test_عشوائي_مدى():
    for _ in range(10):
        x = عشوائي(0, 100)
        assert 0 <= x <= 100

def test_تقريب_عدد():
    assert تقريب_عدد(3.7) == 4

def test_تقريب_خانات():
    assert تقريب_عدد(3.14159, 2) == 3.14

def test_صحيح():
    assert صحيح(3.9) == 3

def test_مطلق_عدد_سالب():
    assert مطلق_عدد(-5) == 5

def test_مطلق_عدد_موجب():
    assert مطلق_عدد(5) == 5

def test_إشارة_سالب():
    assert إشارة(-5) == -1

def test_إشارة_موجب():
    assert إشارة(5) == 1

def test_إشارة_صفر():
    assert إشارة(0) == 0
