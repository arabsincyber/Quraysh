"""اختبارات مكتبة FORTRAN — fortran.py"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from quraysh.fortran import (
    جيب, جيب_تمام, ظل, ظل_تمام,
    جيب_عكسي, ظل_عكسي,
    لوغاريتم, لوغاريتم_طبيعي, أس,
    جذر_ن, قوة_ن,
    مساحة_مثلث, مساحة_دائرة, محيط_دائرة,
    مساحة_مستطيل, مساحة_مربع,
    حجم_كرة, حجم_مكعب,
    متوسط, وسيط, مجموع, أكبر, أصغر,
    دوال_FORTRAN,
)


def test_عدد_الدوال():
    assert len(دوال_FORTRAN) == 27

def test_جيب():
    assert جيب(0) == 0.0

def test_جيب_تمام():
    assert جيب_تمام(0) == 1.0

def test_ظل():
    assert abs(ظل(0)) < 1e-9

def test_جيب_عكسي():
    assert abs(جيب_عكسي(1) - math.pi / 2) < 1e-9

def test_ظل_عكسي():
    assert abs(ظل_عكسي(1) - math.pi / 4) < 1e-9

def test_لوغاريتم():
    assert لوغاريتم(100) == 2.0

def test_لوغاريتم_طبيعي():
    assert abs(لوغاريتم_طبيعي(math.e) - 1.0) < 1e-9

def test_أس():
    assert abs(أس(1) - math.e) < 1e-9

def test_جذر_ن():
    assert جذر_ن(16) == 4.0

def test_جذر_ن_ثلاثي():
    assert abs(جذر_ن(27, 3) - 3.0) < 1e-9

def test_قوة_ن():
    assert قوة_ن(2, 10) == 1024

def test_مساحة_مثلث():
    assert مساحة_مثلث(10, 6) == 30.0

def test_مساحة_دائرة():
    assert abs(مساحة_دائرة(1) - math.pi) < 1e-9

def test_محيط_دائرة():
    assert abs(محيط_دائرة(1) - 2 * math.pi) < 1e-9

def test_مساحة_مستطيل():
    assert مساحة_مستطيل(5, 4) == 20

def test_مساحة_مربع():
    assert مساحة_مربع(5) == 25

def test_حجم_كرة():
    assert abs(حجم_كرة(1) - (4/3) * math.pi) < 1e-9

def test_حجم_مكعب():
    assert حجم_مكعب(3) == 27

def test_متوسط():
    assert متوسط(10, 20, 30, 40) == 25.0

def test_وسيط_زوجي():
    assert وسيط(10, 20, 30, 40) == 25.0

def test_وسيط_فردي():
    assert وسيط(1, 2, 3) == 2

def test_مجموع():
    assert مجموع(1, 2, 3, 4, 5) == 15

def test_أكبر():
    assert أكبر(5, 10, 3, 8) == 10

def test_أصغر():
    assert أصغر(5, 10, 3, 8) == 3
