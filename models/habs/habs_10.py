"""
HBS-10 — Backprop حقيقي (Bigram Neural)
=========================================

نموذج يثبت أن Backprop يشتغل:
- Loss ينخفض تدريجياً
- النص يتحسن
- بدون PyTorch

بعدها نوسّع لـ Transformer.
"""

import math
import random
import json
from pathlib import Path
from collections import Counter


# ═══════════════════════════════════════════════════════════
#  تحميل البيانات
# ═══════════════════════════════════════════════════════════

def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        نص = f.read()
    تشكيل = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670"
    كلمات = []
    for ك in نص.split():
        مجرّد = "".join(c for c in ك if c not in تشكيل)
        if مجرّد:
            كلمات.append(مجرّد)
    return كلمات


def build_vocab(كلمات, max_vocab=500):
    عدّاد = Counter(كلمات)
    الأكثر = عدّاد.most_common(max_vocab - 2)
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for ك, _ in الأكثر:
        vocab[ك] = len(vocab)
    return vocab


def encode(كلمات, vocab):
    return [vocab.get(ك, vocab["<UNK>"]) for ك in كلمات]


# ═══════════════════════════════════════════════════════════
#  Softmax
# ═══════════════════════════════════════════════════════════

def softmax(x):
    m = max(x)
    exps = [math.exp(v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


# ═══════════════════════════════════════════════════════════
#  Bigram Neural — Backprop
# ═══════════════════════════════════════════════════════════

class BigramNeural:
    """Bigram + Backprop"""

    def __init__(self, vocab_size, d_model=16):
        self.vocab_size = vocab_size
        self.d_model = d_model
        حد = 1.0 / math.sqrt(d_model)

        self.embedding = [[random.uniform(-حد, حد) for _ in range(d_model)]
                          for _ in range(vocab_size)]
        self.W_out = [[random.uniform(-حد, حد) for _ in range(d_model)]
                      for _ in range(vocab_size)]

    def forward(self, input_id):
        emb = self.embedding[input_id]
        logits = [sum(emb[j] * self.W_out[i][j] for j in range(self.d_model))
                  for i in range(self.vocab_size)]
        cache = {"input_id": input_id, "emb": emb, "logits": logits}
        return logits, cache

    def backward(self, cache, target_id, lr=0.01):
        input_id = cache["input_id"]
        emb = cache["emb"]
        logits = cache["logits"]

        probs = softmax(logits)
        grad_logits = list(probs)
        grad_logits[target_id] -= 1.0

        # Gradient of embedding
        grad_emb = [0.0] * self.d_model
        for i in range(self.vocab_size):
            gl = grad_logits[i]
            if abs(gl) < 1e-9:
                continue
            row = self.W_out[i]
            for j in range(self.d_model):
                grad_emb[j] += gl * row[j]

        # Update W_out
        for i in range(self.vocab_size):
            gl = grad_logits[i]
            if abs(gl) < 1e-9:
                continue
            row = self.W_out[i]
            for j in range(self.d_model):
                row[j] -= lr * gl * emb[j]

        # Update embedding
        emb_row = self.embedding[input_id]
        for j in range(self.d_model):
            emb_row[j] -= lr * grad_emb[j]

        loss = -math.log(probs[target_id] + 1e-9)
        return loss

    def generate(self, seed_ids, length=10, temperature=0.8):
        seq = list(seed_ids)
        for _ in range(length):
            input_id = seq[-1] % self.vocab_size
            logits, _ = self.forward(input_id)
            if temperature != 1.0:
                logits = [v / temperature for v in logits]
            probs = softmax(logits)
            r = random.random()
            cum = 0
            next_id = 0
            for i, p in enumerate(probs):
                cum += p
                if cum >= r:
                    next_id = i
                    break
            seq.append(next_id)
        return seq

    def حفظ(self, مسار):
        data = {
            "vocab_size": self.vocab_size,
            "d_model": self.d_model,
            "embedding": self.embedding,
            "W_out": self.W_out,
        }
        with open(مسار, "w", encoding="utf-8") as f:
            json.dump(data, f)


# ═══════════════════════════════════════════════════════════
#  التدريب
# ═══════════════════════════════════════════════════════════

def train(نموذج, ids, epochs=3, lr=0.5):
    print(f"🏋️  Backprop حقيقي — {epochs} epochs, lr={lr}")
    for epoch in range(epochs):
        epoch_loss = 0
        epoch_count = 0

        indexed = list(range(len(ids) - 1))
        random.shuffle(indexed)

        for i in indexed:
            input_id = ids[i]
            target_id = ids[i + 1]
            logits, cache = نموذج.forward(input_id)
            loss = نموذج.backward(cache, target_id, lr=lr)
            epoch_loss += loss
            epoch_count += 1

        avg = epoch_loss / max(epoch_count, 1)
        print(f"  Epoch {epoch+1}/{epochs} — loss: {avg:.4f}, lr: {lr:.4f}")
        lr *= 0.85

    return avg


# ═══════════════════════════════════════════════════════════
#  التجربة
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧠 HBS-10 — Backprop حقيقي (Bigram Neural)")
    print("=" * 50)

    مسارات = [
        "/data/data/com.termux/files/home/lugha/quraysh-v2/models/corpus/quran/quran.txt",
        "../../corpus/quran/quran.txt",
    ]

    نص_مسار = None
    for م in مسارات:
        if Path(م).exists():
            نص_مسار = م
            break

    if not نص_مسار:
        print("⚠️ القرآن غير موجود")
        exit(1)

    كلمات = load_corpus(نص_مسار)
    print(f"📖 كلمات: {len(كلمات):,}")

    vocab = build_vocab(كلمات, max_vocab=500)
    print(f"📚 vocab: {len(vocab)}")

    ids = encode(كلمات[:3000], vocab)
    print(f"🔢 IDs: {len(ids):,}")

    # حفظ vocab
    with open("habs_10_vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)
    print("💾 vocab محفوظ")

    نموذج = BigramNeural(vocab_size=len(vocab), d_model=16)
    print(f"🏗️  d_model=16, vocab={len(vocab)}")
    print()

    final_loss = train(نموذج, ids, epochs=3, lr=0.5)

    print()
    print(f"✅ loss النهائي: {final_loss:.4f}")

    # توليد
    seed = ids[:2]
    generated = نموذج.generate(seed, length=10, temperature=0.7)
    id_to_word = {v: k for k, v in vocab.items()}
    نص = " ".join(id_to_word.get(i, "?") for i in generated)
    print(f"📝 نص مولّد: {نص}")

    نموذج.حفظ("habs_10_trained.json")
    print("💾 حُفظ: habs_10_trained.json")
