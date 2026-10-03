"""اختبارات الواجهة التفاعلية — repl.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from quraysh.repl import _اعرض_مساعدة, _تعامل_مع_أمر, main, run_file
from quraysh.tutor import مساعد_لسان_قريش


@pytest.fixture
def مساعد():
    return مساعد_لسان_قريش()


@pytest.fixture
def سجل():
    return []


# ═══ أوامر المساعد ═══

def test_مساعدة_يطبع(capsys):
    _اعرض_مساعدة()
    captured = capsys.readouterr()
    assert "المساعد الذكي" in captured.out
    assert ".اشرح" in captured.out
    assert ".اقترح" in captured.out
    assert ".راجع" in captured.out

def test_تعامل_مع_مساعدة(مساعد, سجل):
    نتيجة = _تعامل_مع_أمر(".مساعدة", مساعد, سجل)
    assert نتيجة is True

def test_تعامل_مع_اشرح(مساعد, سجل, capsys):
    نتيجة = _تعامل_مع_أمر(".اشرح بصمة_نص", مساعد, سجل)
    captured = capsys.readouterr()
    assert نتيجة is True
    assert "SHA-256" in captured.out

def test_تعامل_مع_اشرح_خطأ_إملائي(مساعد, سجل, capsys):
    نتيجة = _تعامل_مع_أمر(".اشرح بصمه_نص", مساعد, سجل)
    captured = capsys.readouterr()
    assert نتيجة is True
    assert "هل قصدت" in captured.out or "بصمة_نص" in captured.out

def test_تعامل_مع_اقترح(مساعد, سجل, capsys):
    نتيجة = _تعامل_مع_أمر(".اقترح تشفير", مساعد, سجل)
    captured = capsys.readouterr()
    assert نتيجة is True
    assert "بصمة_نص" in captured.out

def test_تعامل_مع_راجع_بدون_سجل(مساعد, سجل, capsys):
    نتيجة = _تعامل_مع_أمر(".راجع", مساعد, سجل)
    captured = capsys.readouterr()
    assert نتيجة is True
    assert "لا يوجد كود" in captured.out

def test_تعامل_مع_راجع_مع_سجل(مساعد, capsys):
    سجل = ['(بصمه_نص "قريش")']
    نتيجة = _تعامل_مع_أمر(".راجع", مساعد, سجل)
    captured = capsys.readouterr()
    assert نتيجة is True
    assert "تقرير المساعد" in captured.out

def test_تعامل_مع_غير_أمر(مساعد, سجل):
    نتيجة = _تعامل_مع_أمر("(بصمة_نص \"قريش\")", مساعد, سجل)
    assert نتيجة is False

def test_اشرح_بدون_وسيط(مساعد, سجل, capsys):
    نتيجة = _تعامل_مع_أمر(".اشرح", مساعد, سجل)
    captured = capsys.readouterr()
    assert نتيجة is True
    assert "استخدم" in captured.out

def test_اقترح_بدون_وسيط(مساعد, سجل, capsys):
    نتيجة = _تعامل_مع_أمر(".اقترح", مساعد, سجل)
    captured = capsys.readouterr()
    assert نتيجة is True
    assert "استخدم" in captured.out

def test_أمر_غير_معروف_يرجع_False(مساعد, سجل):
    نتيجة = _تعامل_مع_أمر(".xyz", مساعد, سجل)
    assert نتيجة is False


# ═══ التكامل الكامل ═══

def test_repl_main_يخرج_بخروج(monkeypatch):
    """اختبار أن main() يخرج عند 'خروج'"""
    الإدخالات = iter(["خروج"])
    monkeypatch.setattr("builtins.input", lambda _: next(الإدخالات))

    main()  # يجب أن يخرج بدون خطأ


def test_repl_main_يعرض_نتيجة(monkeypatch, capsys):
    """اختبار أن main() يقيّم كوداً ويطبع النتيجة"""
    الإدخالات = iter(['(+ 2 3)', 'خروج'])
    monkeypatch.setattr("builtins.input", lambda _: next(الإدخالات))

    main()
    captured = capsys.readouterr()
    assert "5" in captured.out
