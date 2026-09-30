"""
HBS-3 — Backprop يدوي
=======================

Transformer مصغّر — مع Backpropagation حقيقي.
تعليمي فقط — احترام القرآن.
"""

import math
import random
from pathlib import Path


# ═══════════════════════════════════════════════════════════
#  الأساسيات
# ═══════════════════════════════════════════════════════════

def softmax(x):
    m = max(x)
    exps = [math.exp(v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


def matmul(A, B):
    cols_B = len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(cols_B)] for i in range(len(A))]


def transpose(M):
    return [list(row) for row in zip(*M)]


def add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def scale_matrix(M, f):
    return [[x * f for x in row] for row in M]


# ═══════════════════════════════════════════════════════════
#  البيانات
# ═══════════════════════════════════════════════════════════

def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def build_vocab(lines):
    words = set()
    for line in lines:
        for w in line.split():
            words.add(w)
    words.add("<BOS>")
    words.add("<EOS>")
    vocab = sorted(words)
    return vocab, {w: i for i, w in enumerate(vocab)}, {i: w for i, w in enumerate(vocab)}


# ═══════════════════════════════════════════════════════════
#  النموذج — بدون Attention (مبسّط للـ Backprop)
# ═══════════════════════════════════════════════════════════

class SimpleHabs3:
    """
    نموذج مبسّط:
    - Embedding
    - Average Pooling
    - Output Projection
    - Backprop على كل شي
    """

    def __init__(self, vocab_size, d_model=16, seed=42):
        random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model

        # Embedding
        scale_e = math.sqrt(2.0 / (vocab_size + d_model))
        self.embedding = [
            [random.gauss(0, scale_e) for _ in range(d_model)]
            for _ in range(vocab_size)
        ]

        # Output Projection
        scale_o = math.sqrt(2.0 / (d_model + vocab_size))
        self.W_out = [
            [random.gauss(0, scale_o) for _ in range(vocab_size)]
            for _ in range(d_model)
        ]

    # ═══════════════════════════════════════════════════════════
    #  Forward
    # ═══════════════════════════════════════════════════════════

    def forward(self, token_ids):
        """
        Forward Pass.

        Returns:
            H (seq_len × d_model) — Embedding
            h_pool (d_model,) — متوسط Embedding
            logits (vocab_size,) — التوقعات
        """
        # 1. Embedding
        H = [self.embedding[tid][:] for tid in token_ids]

        # 2. Average Pooling
        seq_len = len(H)
        h_pool = [
            sum(H[i][j] for i in range(seq_len)) / seq_len
            for j in range(self.d_model)
        ]

        # 3. Output Projection
        # logits = h_pool × W_out
        logits = [
            sum(h_pool[i] * self.W_out[i][j] for i in range(self.d_model))
            for j in range(self.vocab_size)
        ]

        return H, h_pool, logits

    # ═══════════════════════════════════════════════════════════
    #  Backprop
    # ═══════════════════════════════════════════════════════════

    def backward(self, token_ids, target_id, H, h_pool, logits, lr=0.01):
        """
        Backpropagation.

        Args:
            token_ids: قائمة الأرقام
            target_id: الرقم الصحيح
            H: Embedding
            h_pool: متوسط
            logits: التوقعات
            lr: معدل التعلم

        Returns:
            loss: قيمة الخطأ
        """
        # ═══ 1. حساب Loss ═══
        probs = softmax(logits)
        loss = -math.log(probs[target_id] + 1e-9)

        # ═══ 2. Gradient للـ Logits ═══
        # dL/dLogits = softmax(logits) - one_hot(target)
        d_logits = probs[:]
        d_logits[target_id] -= 1.0

        # ═══ 3. Gradient للـ W_out ═══
        # dL/dW_out = h_pool^T × d_logits
        # h_pool: (d_model,)
        # d_logits: (vocab_size,)
        # dL/dW_out: (d_model × vocab_size)
        d_W_out = [
            [h_pool[i] * d_logits[j] for j in range(self.vocab_size)]
            for i in range(self.d_model)
        ]

        # ═══ 4. Gradient للـ h_pool ═══
        # dL/dh_pool = W_out × d_logits
        # W_out: (d_model × vocab_size)
        # d_logits: (vocab_size,)
        # d_h_pool: (d_model,)
        d_h_pool = [
            sum(self.W_out[i][j] * d_logits[j] for j in range(self.vocab_size))
            for i in range(self.d_model)
        ]

        # ═══ 5. Gradient للـ Embedding ═══
        # d_h_pool/d_H[i][j] = 1 / seq_len
        # dL/dH[i][j] = d_h_pool[j] / seq_len
        seq_len = len(H)
        d_H = [
            [d_h_pool[j] / seq_len for j in range(self.d_model)]
            for _ in range(seq_len)
        ]

        # ═══ 6. التعديل ═══

        # 6.1: تعديل W_out
        for i in range(self.d_model):
            for j in range(self.vocab_size):
                self.W_out[i][j] -= lr * d_W_out[i][j]

        # 6.2: تعديل Embedding
        for i, tid in enumerate(token_ids):
            for j in range(self.d_model):
                self.embedding[tid][j] -= lr * d_H[i][j]

        return loss

    # ═══════════════════════════════════════════════════════════
    #  التوليد
    # ═══════════════════════════════════════════════════════════

    def generate(self, start, vocab, word2id, id2word, length=5):
        """يولّد جملة"""
        tokens = [word2id.get(w, word2id["<BOS>"]) for w in start.split()]

        for _ in range(length):
            _, _, logits = self.forward(tokens)
            probs = softmax(logits)

            # أعلى احتمال
            chosen = max(range(len(probs)), key=lambda i: probs[i])

            if id2word[chosen] == "<EOS>":
                break

            tokens.append(chosen)

        return " ".join(id2word[t] for t in tokens if id2word[t] not in ("<BOS>", "<EOS>"))


# ═══════════════════════════════════════════════════════════
#  التدريب
# ═══════════════════════════════════════════════════════════

def train(model, batch, word2id, epochs=10, lr=0.01):
    """يتدرب"""
    losses = []

    for epoch in range(epochs):
        epoch_loss = 0
        count = 0

        for input_words, target_word in batch:
            input_ids = [word2id.get(w, 0) for w in input_words]
            target_id = word2id.get(target_word, 0)

            # Forward
            H, h_pool, logits = model.forward(input_ids)

            # Backward
            loss = model.backward(input_ids, target_id, H, h_pool, logits, lr)

            epoch_loss += loss
            count += 1

        avg_loss = epoch_loss / count if count > 0 else 0
        losses.append(avg_loss)

        print(f"  [Epoch {epoch+1}] Loss: {avg_loss:.4f}")

    return losses


# ═══════════════════════════════════════════════════════════
#  التشغيل
# ═══════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  🧠 HBS-3 — Backprop يدوي")
    print("═" * 60)
    print()

    # البيانات
    path = "data/corpus.txt"
    lines = load_corpus(path)
    print(f"📖 البيانات: {len(lines)} سطر")
    print()

    # القاموس
    vocab, word2id, id2word = build_vocab(lines)
    print(f"📚 القاموس: {len(vocab)} كلمة")
    print()

    # Batch — بسيط (جمل قصيرة)
    batch = []
    for line in lines[:50]:
        words = line.split()
        if 2 <= len(words) <= 6:
            batch.append((words[:-1], words[-1]))

    print(f"🎓 Batch: {len(batch)} عينة")
    print()

    # النموذج
    model = SimpleHabs3(vocab_size=len(vocab), d_model=16)

    # التدريب
    print("🎓 جاري التدريب...")
    print()
    losses = train(model, batch, word2id, epochs=10, lr=0.01)

    print()
    print(f"📉 Loss الابتدائي: {losses[0]:.4f}")
    print(f"📉 Loss النهائي: {losses[-1]:.4f}")
    improvement = (losses[0] - losses[-1]) / losses[0] * 100
    print(f"📈 التحسين: {improvement:.1f}%")
    print()

    # التوليد
    print("─" * 60)
    print("🎨 التوليد:")
    print("─" * 60)
    print()

    starts = ["قل", "هو", "إنا", "يوم"]
    for s in starts:
        result = model.generate(s, vocab, word2id, id2word, length=5)
        print(f"   [{s}] → {result}")

    print()
    print("═" * 60)
    print("  ⚠️  تعليمي فقط — احترام القرآن.")
    print("═" * 60)


if __name__ == "__main__":
    main()
