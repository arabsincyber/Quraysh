"""
Crypto — مكتبة التشفير
========================

تشفير وتوقيع للغة "لسان قريش".
مبنية على pycryptodome + hashlib.

الفلسفة:
  "الوضوح = أمان"
  - كل عملية تُعلن نفسها
  - التشفير بـ AES-256 (CBC)
  - التوقيع بـ HMAC-SHA256
"""

import os
import hmac
import hashlib
import base64
from pathlib import Path

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Random import get_random_bytes
    PYDOME_OK = True
except ImportError:
    PYDOME_OK = False


# ═══════════════════════════════════════════════════════════
#  Hash — البصمة
# ═══════════════════════════════════════════════════════════

def بصمة(نص):
    """بصمة SHA256 لنص"""
    if isinstance(نص, str):
        نص = نص.encode("utf-8")
    return hashlib.sha256(نص).hexdigest()


def بصمة_ملف(مسار):
    """بصمة SHA256 لملف"""
    try:
        h = hashlib.sha256()
        with open(مسار, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"❌ خطأ: {e}"


def قارن_بصمة(مسار, بصمة_متوقعة):
    """يتحقق من بصمة ملف"""
    try:
        return بصمة_ملف(مسار) == بصمة_متوقعة
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  المفتاح
# ═══════════════════════════════════════════════════════════

def مفتاح_جديد(حجم=32):
    """يولّد مفتاح عشوائي (32 بايت = AES-256)"""
    return base64.b64encode(get_random_bytes(حجم)).decode("utf-8")


def مفتاح_من_نص(نص):
    """يحوّل نص لمفتاح AES-256"""
    key = hashlib.sha256(نص.encode("utf-8")).digest()
    return base64.b64encode(key).decode("utf-8")


def حفظ_مفتاح(مفتاح, مسار):
    """يحفظ المفتاح في ملف"""
    try:
        Path(مسار).write_text(مفتاح, encoding="utf-8")
        return f"✅ تم حفظ المفتاح: {مسار}"
    except Exception as e:
        return f"❌ خطأ: {e}"


def اقرأ_مفتاح(مسار):
    """يقرأ مفتاح من ملف"""
    try:
        return Path(مسار).read_text(encoding="utf-8").strip()
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  التشفير — AES-256-CBC
# ═══════════════════════════════════════════════════════════

def شفر(نص, مفتاح):
    """يشفّر نص بـ AES-256-CBC"""
    if not PYDOME_OK:
        return "❌ pycryptodome غير مثبتة"
    try:
        key = base64.b64decode(مفتاح)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = نص.encode("utf-8") if isinstance(نص, str) else نص
        encrypted = cipher.encrypt(pad(data, AES.block_size))
        # ندمج IV + المشفر، ثم base64
        result = base64.b64encode(iv + encrypted).decode("utf-8")
        return result
    except Exception as e:
        return f"❌ خطأ: {e}"


def فك(مشفر, مفتاح):
    """يفك تشفير نص"""
    if not PYDOME_OK:
        return "❌ pycryptodome غير مثبتة"
    try:
        key = base64.b64decode(مفتاح)
        raw = base64.b64decode(مشفر)
        iv = raw[:16]
        encrypted = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return decrypted.decode("utf-8")
    except Exception as e:
        return f"❌ خطأ: {e}"


def شفر_ملف(مسار, مفتاح, مسار_ناتج=None):
    """يشفّر ملف كامل"""
    try:
        data = Path(مسار).read_bytes()
        key = base64.b64decode(مفتاح)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data, AES.block_size))
        out = مسار_ناتج or (مسار + ".enc")
        Path(out).write_bytes(iv + encrypted)
        return f"✅ تم التشفير: {out}"
    except Exception as e:
        return f"❌ خطأ: {e}"


def فك_ملف(مسار, مفتاح, مسار_ناتج=None):
    """يفك تشفير ملف"""
    try:
        raw = Path(مسار).read_bytes()
        key = base64.b64decode(مفتاح)
        iv = raw[:16]
        encrypted = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        out = مسار_ناتج or مسار.replace(".enc", "")
        Path(out).write_bytes(decrypted)
        return f"✅ تم فك التشفير: {out}"
    except Exception as e:
        return f"❌ خطأ: {e}"


# ═══════════════════════════════════════════════════════════
#  التوقيع — HMAC-SHA256
# ═══════════════════════════════════════════════════════════

def وقع(رسالة, مفتاح):
    """يوقّع رسالة بـ HMAC-SHA256"""
    if isinstance(رسالة, str):
        رسالة = رسالة.encode("utf-8")
    if isinstance(مفتاح, str):
        مفتاح = مفتاح.encode("utf-8")
    return hmac.new(مفتاح, رسالة, hashlib.sha256).hexdigest()


def تحقق_توقيع(رسالة, توقيع, مفتاح):
    """يتحقق من توقيع"""
    متوقع = وقع(رسالة, مفتاح)
    return hmac.compare_digest(متوقع, توقيع)


# ═══════════════════════════════════════════════════════════
#  الاختبار
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    from pathlib import Path
    HOME = Path.home()

    print("=" * 60)
    print("  🔐 Crypto — مكتبة التشفير")
    print("=" * 60)
    print()

    # 1. بصمة
    print("1️⃣ بصمة SHA256:")
    print(f"   {بصمة('السلام عليكم')}")
    print()

    # 2. مفتاح جديد
    print("2️⃣ توليد مفتاح:")
    key = مفتاح_جديد()
    print(f"   {key[:32]}...")
    print()

    # 3. مفتاح من نص
    print("3️⃣ مفتاح من نص:")
    key2 = مفتاح_من_نص("كلمة سر قوية")
    print(f"   {key2[:32]}...")
    print()

    # 4. تشفير نص
    print("4️⃣ تشفير نص:")
    النص = "هذه رسالة سرية من لسان قريش"
    مشفر = شفر(النص, key)
    print(f"   الأصل: {النص}")
    print(f"   المشفر: {مشفر[:50]}...")
    print()

    # 5. فك التشفير
    print("5️⃣ فك التشفير:")
    مفكوك = فك(مشفر, key)
    print(f"   {مفكوك}")
    print(f"   ✅ مطابق؟ {مفكوك == النص}")
    print()

    # 6. توقيع
    print("6️⃣ توقيع HMAC:")
    توقيع = وقع("رسالة مهمة", "مفتاح سري")
    print(f"   {توقيع}")
    print()

    # 7. تحقق
    print("7️⃣ تحقق من التوقيع:")
    صحيح = تحقق_توقيع("رسالة مهمة", توقيع, "مفتاح سري")
    خطأ = تحقق_توقيع("رسالة معدلة", توقيع, "مفتاح سري")
    print(f"   الصحيح: {صحيح}")
    print(f"   المعدّل: {خطأ}")
    print()

    # 8. بصمة ملف
    test_file = str(HOME / "crypto_test.txt")
    Path(test_file).write_text("محتوى اختبار", encoding="utf-8")
    print("8️⃣ بصمة ملف:")
    print(f"   {بصمة_ملف(test_file)}")
    print()

    # 9. تشفير ملف
    print("9️⃣ تشفير ملف:")
    print(f"   {شفر_ملف(test_file, key)}")
    print()

    # 10. فك ملف
    print("🔟 فك تشفير ملف:")
    print(f"   {فك_ملف(test_file + '.enc', key, test_file + '.dec')}")
    print()

    # تنظيف
    for f in [test_file, test_file + ".enc", test_file + ".dec"]:
        try:
            Path(f).unlink()
        except:
            pass

    print("=" * 60)
