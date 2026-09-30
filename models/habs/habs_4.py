"""
HBS-4 — Self-Attention + Backprop
====================================

Transformer مصغّر — مع Self-Attention.
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
    """(n × m) × (m × p) = (n × p)"""
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def transpose(M):
    return [list(row) for row in zip(*M)]


def add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def matmul_scalar(M, s):
    return [[x * s for x in row] for row in M]


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
#  HBS-4 — Self-Attention + Backprop
# ═══════════════════════════════════════════════════════════

class Habs4:

    def __init__(self, vocab_size, d_model=16, seed=42):
        random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model

        def rand_matrix(rows, cols):
            scale_v = math.sqrt(2.0 / (rows + cols))
            return [[random.gauss(0, scale_v) for _ in range(cols)]
                    for _ in range(rows)]

        # Embedding
        self.embedding = rand_matrix(vocab_size, d_model)

        # Attention Weights
        self.W_q = rand_matrix(d_model, d_model)
        self.W_k = rand_matrix(d_model, d_model)
        self.W_v = rand_matrix(d_model, d_model)

        # Output
        self.W_out = rand_matrix(d_model, vocab_size)

    # ═══════════════════════════════════════════════════════════
    #  Forward
    # ═══════════════════════════════════════════════════════════

    def forward(self, token_ids):
        seq_len = len(token_ids)

        # 1. Embedding
        X = [self.embedding[tid][:] for tid in token_ids]

        # 2. Q, K, V
        Q = matmul(X, self.W_q)
        K = matmul(X, self.W_k)
        V = matmul(X, self.W_v)

        # 3. Attention Scores
        K_T = transpose(K)
        S = matmul(Q, K_T)
        scale_v = math.sqrt(self.d_model)
        S = matmul_scalar(S, 1.0 / scale_v)

        # 4. Attention Weights
        A = [softmax(row) for row in S]

        # 5. Attention Output
        O = matmul(A, V)

        # 6. Average Pool
        h_pool = [
            sum(O[i][j] for i in range(seq_len)) / seq_len
            for j in range(self.d_model)
        ]

        # 7. Output
        logits = [
            sum(h_pool[i] * self.W_out[i][j] for i in range(self.d_model))
            for j in range(self.vocab_size)
        ]

        # حفظ للـ backward
        self.cache = {
            'X': X, 'Q': Q, 'K': K, 'V': V,
            'S': S, 'A': A, 'O': O,
            'h_pool': h_pool, 'logits': logits,
            'token_ids': token_ids,
        }

        return logits

    # ═══════════════════════════════════════════════════════════
    #  Backward
    # ═══════════════════════════════════════════════════════════

    def backward(self, target_id, lr=0.01):
        c = self.cache
        X, Q, K, V = c['X'], c['Q'], c['K'], c['V']
        S, A, O = c['S'], c['A'], c['O']
        h_pool, logits = c['h_pool'], c['logits']
        token_ids = c['token_ids']
        seq_len = len(token_ids)
        d = self.d_model

        # 1. Loss
        probs = softmax(logits)
        loss = -math.log(probs[target_id] + 1e-9)

        # 2. dL/dLogits
        d_logits = probs[:]
        d_logits[target_id] -= 1.0

        # 3. dL/dW_out
        d_W_out = [
            [h_pool[i] * d_logits[j] for j in range(self.vocab_size)]
            for i in range(d)
        ]

        # 4. dL/dh_pool
        d_h_pool = [
            sum(self.W_out[i][j] * d_logits[j] for j in range(self.vocab_size))
            for i in range(d)
        ]

        # 5. dL/dO (لكل موضع)
        d_O = [
            [d_h_pool[j] / seq_len for j in range(d)]
            for _ in range(seq_len)
        ]

        # 6. dL/dA = dL/dO × V^T
        V_T = transpose(V)
        d_A = matmul(d_O, V_T)

        # 7. dL/dV = A^T × dL/dO
        A_T = transpose(A)
        d_V = matmul(A_T, d_O)

        # 8. dL/dS — عبر Softmax
        d_S = []
        for i in range(seq_len):
            row_A = A[i]
            row_dA = d_A[i]
            # sum(dL/dA × A)
            dot = sum(row_dA[j] * row_A[j] for j in range(seq_len))
            row_dS = [row_A[j] * (row_dA[j] - dot) for j in range(seq_len)]
            d_S.append(row_dS)

        # 9. dL/dQ, dL/dK (عبر S = Q × K^T / √d)
        scale_v = 1.0 / math.sqrt(d)
        K_T = transpose(K)
        d_Q = matmul(d_S, K)
        d_Q = matmul_scalar(d_Q, scale_v)

        d_S_T = transpose(d_S)
        d_K = matmul(d_S_T, Q)
        d_K = matmul_scalar(d_K, scale_v)

        # 10. dL/dW_q, dL/dW_k, dL/dW_v
        X_T = transpose(X)
        d_W_q = matmul(X_T, d_Q)
        d_W_k = matmul(X_T, d_K)
        d_W_v = matmul(X_T, d_V)

        # 11. dL/dX
        d_X = matmul(d_Q, transpose(self.W_q))
        d_X = add(d_X, matmul(d_K, transpose(self.W_k)))
        d_X = add(d_X, matmul(d_V, transpose(self.W_v)))

        # ═══ التعديل ═══

        # W_out
        for i in range(d):
            for j in range(self.vocab_size):
                self.W_out[i][j] -= lr * d_W_out[i][j]

        # W_q, W_k, W_v
        for i in range(d):
            for j in range(d):
                self.W_q[i][j] -= lr * d_W_q[i][j]
                self.W_k[i][j] -= lr * d_W_k[i][j]
                self.W_v[i][j] -= lr * d_W_v[i][j]

        # Embedding
        for i, tid in enumerate(token_ids):
            for j in range(d):
                self.embedding[tid][j] -= lr * d_X[i][j]

        return loss

    # ═══════════════════════════════════════════════════════════
    #  التوليد
    # ═══════════════════════════════════════════════════════════

    def generate(self, start, word2id, id2word, length=5):
        tokens = [word2id.get(w, word2id["<BOS>"]) for w in start.split()]

        for _ in range(length):
            logits = self.forward(tokens)
            probs = softmax(logits)
            chosen = max(range(len(probs)), key=lambda i: probs[i])
            if id2word[chosen] == "<EOS>":
                break
            tokens.append(chosen)

        return " ".join(id2word[t] for t in tokens if id2word[t] not in ("<BOS>", "<EOS>"))


# ═══════════════════════════════════════════════════════════
#  التدريب
# ═══════════════════════════════════════════════════════════

def train(model, batch, word2id, epochs=10, lr=0.001):
    losses = []

    for epoch in range(epochs):
        epoch_loss = 0
        count = 0

        for input_words, target_word in batch:
            input_ids = [word2id.get(w, 0) for w in input_words]
            target_id = word2id.get(target_word, 0)

            # Forward
            model.forward(input_ids)

            # Backward
            loss = model.backward(target_id, lr)

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
    print("  🧠 HBS-4 — Self-Attention + Backprop")
    print("═" * 60)
    print()

    # البيانات
    lines = load_corpus("data/corpus.txt")
    print(f"📖 البيانات: {len(lines)} سطر")
    print()

    # القاموس
    vocab, word2id, id2word = build_vocab(lines)
    print(f"📚 القاموس: {len(vocab)} كلمة")
    print()

    # Batch
    batch = []
    for line in lines[:80]:
        words = line.split()
        if 2 <= len(words) <= 6:
            batch.append((words[:-1], words[-1]))

    print(f"🎓 Batch: {len(batch)} عينة")
    print()

    # النموذج
    model = Habs4(vocab_size=len(vocab), d_model=16)

    # التدريب
    print("🎓 جاري التدريب...")
    print()
    losses = train(model, batch, word2id, epochs=10, lr=0.001)

    print()
    print(f"📉 الابتدائي: {losses[0]:.4f}")
    print(f"📉 النهائي: {losses[-1]:.4f}")
    imp = (losses[0] - losses[-1]) / losses[0] * 100
    print(f"📈 التحسين: {imp:.1f}%")
    print()

    # التوليد
    print("─" * 60)
    print("🎨 التوليد:")
    print("─" * 60)
    print()

    for s in ["قل", "هو", "إنا", "يوم"]:
        result = model.generate(s, word2id, id2word, length=5)
        print(f"   [{s}] → {result}")

    print()
    print("═" * 60)
    print("  ⚠️  تعليمي فقط — احترام القرآن.")
    print("═" * 60)


if __name__ == "__main__":
    main()
