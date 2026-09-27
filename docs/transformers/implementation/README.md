# 🔧 تنفيذ Transformers

> **تنفيذ عملي لمفاهيم Transformers — خطوة بخطوة.**

---

## 📚 المحتويات

| # | الملف | الوصف |
|---|-------|--------|
| 1 | 01_softmax.py | تحويل Logits لاحتمالات |
| 2 | 02_sampling.py | Greedy, Top-K, Top-P |
| 3 | 03_attention.py | آلية الانتباه (Q, K, V) |
| 4 | 04_transformer.py | Transformer كامل |

---

## 🚀 التشغيل

افتح Terminal ونفّذ:

    python3 01_softmax.py
    python3 02_sampling.py
    python3 03_attention.py
    python3 04_transformer.py

---

## 🎯 ما ستتعلمه

### 1️⃣ Softmax
- كيف يحوّل النموذج الأرقام لاحتمالات
- دور Temperature في التحكم بالإبداع

### 2️⃣ Sampling
- Greedy — دقيق لكن ممل
- Top-K — متوازن
- Top-P — مرن
- Random — مبدع

### 3️⃣ Attention
- Q, K, V
- Softmax على الأوزان
- Mask — إخفاء المستقبل

### 4️⃣ Transformer
- Embedding + Positional Encoding
- Multi-Head Attention
- Feed Forward
- Layer Norm
- المخرجات النهائية

---

## ⚠️ ملاحظة مهمة

هذا النموذج تعليمي:
- المعمارية صحيحة
- الأوزان عشوائية (بدون تدريب)
- النتائج مو حقيقية

لكن:
- نفس معمارية النماذج الحديثة
- نفس المبادئ
- نفس الحسابات

الفرق:
- الحجم: مليارات الأوزان مقابل مئات
- التدريب: بيانات ضخمة مقابل لا شي

---

## 📖 للتوسّع

- راجع: ../README.md — المفاهيم النظرية
- جرب: عدّل الأرقام، شوف النتائج
- افهم: كل سطر — ليش موجود

---

💙 صُنع بـ 💙 في العالم العربي
