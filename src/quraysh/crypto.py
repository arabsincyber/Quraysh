"""crypto.py — دوال التشفير للسان قريش"""
import hashlib
import hmac
import base64
import secrets

def بصمة_نص(نص: str, خوارزمية: str = "sha256") -> str:
    return hashlib.new(خوارزمية, نص.encode("utf-8")).hexdigest()

def بصمة_ملف(مسار: str, خوارزمية: str = "sha256") -> str:
    h = hashlib.new(خوارزمية)
    with open(مسار, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def توقيع_hmac(نص: str, مفتاح: str) -> str:
    return hmac.new(مفتاح.encode(), نص.encode(), hashlib.sha256).hexdigest()

def تحقق_hmac(نص: str, مفتاح: str, توقيع: str) -> bool:
    return hmac.compare_digest(توقيع_hmac(نص, مفتاح), توقيع)

def ترميز_base64(نص: str) -> str:
    return base64.b64encode(نص.encode("utf-8")).decode("ascii")

def فك_base64(نص: str) -> str:
    return base64.b64decode(نص.encode("ascii")).decode("utf-8")

def مفتاح_عشوائي(طول: int = 32) -> str:
    return secrets.token_hex(طول)

def مقارنة_آمنة(أ: str, ب: str) -> bool:
    return hmac.compare_digest(أ, ب)

def بصمة_سلسلة(*عناصر: str) -> str:
    h = hashlib.sha256()
    for ع in عناصر:
        h.update(ع.encode("utf-8"))
    return h.hexdigest()



def تشفير_xor(نص: str, مفتاح: str) -> str:
    b = نص.encode("utf-8")
    k = مفتاح.encode("utf-8")
    return base64.b64encode(bytes(x ^ k[i % len(k)] for i, x in enumerate(b))).decode("ascii")

def فك_xor(نص: str, مفتاح: str) -> str:
    b = base64.b64decode(نص.encode("ascii"))
    k = مفتاح.encode("utf-8")
    return bytes(x ^ k[i % len(k)] for i, x in enumerate(b)).decode("utf-8")

دوال_التشفير = {
    "بصمة_نص": بصمة_نص,
    "بصمة_ملف": بصمة_ملف,
    "توقيع_hmac": توقيع_hmac,
    "تحقق_hmac": تحقق_hmac,
    "ترميز_base64": ترميز_base64,
    "فك_base64": فك_base64,
    "مفتاح_عشوائي": مفتاح_عشوائي,
    "مقارنة_آمنة": مقارنة_آمنة,
    "بصمة_سلسلة": بصمة_سلسلة,
    "تشفير_xor": تشفير_xor,
    "فك_xor": فك_xor,
}
