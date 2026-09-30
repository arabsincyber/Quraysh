"""
HBS-7 — Self-Attention + FF + Backprop
=========================================

Transformer مصغّر — كامل.
Attention + Feed Forward + Backprop.
تعليمي فقط.
"""

import math
import random


# ═══════════════════════════════════════════════════════════
#  الأساسيات
# ═══════════════════════════════════════════════════════════

def softmax(x):
    m = max(x)
    exps = [math.exp(v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


def relu(x):
    return max(0.0, x)


def relu_grad(x):
    return 1.0 if x > 0 else 0.0


def matmul(A, B):
    """(n × m) × (m × p) = (n × p)"""
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def transpose(M):
    return [list(row) for row in zip(*M)]


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
#  HBS-7 — Full Transformer (مصغّر)
# ═══════════════════════════════════════════════════════════

class Habs7:

    def __init__(self, vocab_size, d_model=16, d_ff=32, seed=42):
        random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.d_ff = d_ff
        self.sqrt_d = math.sqrt(d_model)

        def rand_matrix(rows, cols):
            scale_v = math.sqrt(2.0 / (rows + cols))
            return [[random.gauss(0, scale_v) for _ in range(cols)]
                    for _ in range(rows)]

        # Embedding
        self.embed = rand_matrix(vocab_size, d_model)

        # Attention
        self.W_q = rand_matrix(d_model, d_model)
        self.W_k = rand_matrix(d_model, d_model)
        self.W_v = rand_matrix(d_model, d_model)

        # FF
        self.W1 = rand_matrix(d_model, d_ff)
        self.b1 = [0.0] * d_ff
        self.W2 = rand_matrix(d_ff, vocab_size)
        self.b2 = [0.0] * vocab_size

    # ═══════════════════════════════════════════════════════════
    #  Forward
    # ═══════════════════════════════════════════════════════════

    def forward(self, token_ids):
        seq_len = len(token_ids)
        d = self.d_model
        d_ff = self.d_ff
        V = self.vocab_size

        # 1. Embedding
        X = [self.embed[tid][:] for tid in token_ids]

        # 2. Q, K, V
        Q = matmul(X, self.W_q)
        K = matmul(X, self.W_k)
        V_mat = matmul(X, self.W_v)

        # 3. Scores
        K_T = transpose(K)
        S = matmul(Q, K_T)
        # scale
        S = [[v / self.sqrt_d for v in row] for row in S]

        # 4. Causal Mask
        for i in range(seq_len):
            for j in range(seq_len):
                if j > i:
                    S[i][j] = -1e9

        # 5. Attention Weights
        A = [softmax(row) for row in S]

        # 6. Attention Output
        O = matmul(A, V_mat)

        # 7. Average Pool
        h = [
            sum(O[i][j] for i in range(seq_len)) / seq_len
            for j in range(d)
        ]

        # 8. FF Layer 1
        h1_pre = [
            sum(h[i] * self.W1[i][j] for i in range(d)) + self.b1[j]
            for j in range(d_ff)
        ]
        h1 = [relu(v) for v in h1_pre]

        # 9. FF Layer 2
        logits = [
            sum(h1[i] * self.W2[i][j] for i in range(d_ff)) + self.b2[j]
            for j in range(V)
        ]

        # Cache
        self.cache = {
            'X': X, 'Q': Q, 'K': K, 'V': V_mat,
            'S': S, 'A': A, 'O': O,
            'h': h, 'h1_pre': h1_pre, 'h1': h1,
            'logits': logits, 'tokens': token_ids,
            'seq_len': seq_len,
        }

        return logits

    # ═══════════════════════════════════════════════════════════
    #  Backward
    # ═══════════════════════════════════════════════════════════

    def backward(self, target_id, lr=0.01):
        c = self.cache
        X = c['X']
        Q = c['Q']
        K = c['K']
        V_mat = c['V']
        S = c['S']
        A = c['A']
        O = c['O']
        h = c['h']
        h1_pre = c['h1_pre']
        h1 = c['h1']
        logits = c['logits']
        tokens = c['tokens']
        seq_len = c['seq_len']
        d = self.d_model
        d_ff = self.d_ff
        V = self.vocab_size

        # ═══ 1. Loss ═══
        probs = softmax(logits)
        loss = -math.log(probs[target_id] + 1e-9)

        # ═══ 2. dL/dLogits ═══
        d_logits = probs[:]
        d_logits[target_id] -= 1.0

        # ═══ 3. FF Layer 2 ═══
        d_W2 = [
            [h1[i] * d_logits[j] for j in range(V)]
            for i in range(d_ff)
        ]
        d_b2 = d_logits[:]

        d_h1 = [
            sum(self.W2[i][j] * d_logits[j] for j in range(V))
            for i in range(d_ff)
        ]

        # ═══ 4. ReLU ═══
        d_h1_pre = [d_h1[i] * relu_grad(h1_pre[i]) for i in range(d_ff)]

        # ═══ 5. FF Layer 1 ═══
        d_W1 = [
            [h[i] * d_h1_pre[j] for j in range(d_ff)]
            for i in range(d)
        ]
        d_b1 = d_h1_pre[:]

        d_h = [
            sum(self.W1[i][j] * d_h1_pre[j] for j in range(d_ff))
            for i in range(d)
        ]

        # ═══ 6. Average Pool ═══
        d_O = [
            [d_h[j] / seq_len for j in range(d)]
            for _ in range(seq_len)
        ]

        # ═══ 7. Attention Output ═══
        # O = A × V
        # dL/dA = dL/dO × V^T
        V_T = transpose(V_mat)
        d_A = matmul(d_O, V_T)

        # dL/dV = A^T × dL/dO
        A_T = transpose(A)
        d_V = matmul(A_T, d_O)

        # ═══ 8. Softmax ═══
        d_S = []
        for i in range(seq_len):
            row_A = A[i]
            row_dA = d_A[i]
            # dot = Σ dA × A
            dot = sum(row_dA[j] * row_A[j] for j in range(seq_len))
            # dS[i][j] = A[i][j] × (dA[i][j] - dot)
            row_dS = [row_A[j] * (row_dA[j] - dot) for j in range(seq_len)]
            d_S.append(row_dS)

        # ═══ 9. Scale ═══
        d_S_scaled = [[v / self.sqrt_d for v in row] for row in d_S]

        # ═══ 10. Scores — Q × K^T ═══
        # dL/dQ = d_S_scaled × K
        d_Q = matmul(d_S_scaled, K)

        # dL/dK = d_S_scaled^T × Q
        d_S_T = transpose(d_S_scaled)
        d_K = matmul(d_S_T, Q)

        # ═══ 11. W_q, W_k, W_v ═══
        X_T = transpose(X)
        d_W_q = matmul(X_T, d_Q)
        d_W_k = matmul(X_T, d_K)
        d_W_v = matmul(X_T, d_V)

        # ═══ 12. dL/dX ═══
        W_q_T = transpose(self.W_q)
        W_k_T = transpose(self.W_k)
        W_v_T = transpose(self.W_v)

        d_X = matmul(d_Q, W_q_T)
        d_X = [[d_X[i][j] + matmul(d_K, W_k_T)[i][j] for j in range(d)] for i in range(seq_len)]
        d_X = [[d_X[i][j] + matmul(d_V, W_v_T)[i][j] for j in range(d)] for i in range(seq_len)]

        # ═══ Update ═══

        # W2, b2
        for i in range(d_ff):
            for j in range(V):
                self.W2[i][j] -= lr * d_W2[i][j]
        for j in range(V):
            self.b2[j] -= lr * d_b2[j]

        # W1, b1
        for i in range(d):
            for j in range(d_ff):
                self.W1[i][j] -= lr * d_W1[i][j]
        for j in range(d_ff):
            self.b1[j] -= lr * d_b1[j]

        # W_q, W_k, W_v
        for i in range(d):
            for j in range(d):
                self.W_q[i][j] -= lr * d_W_q[i][j]
                self.W_k[i][j] -= lr * d_W_k[i][j]
                self.W_v[i][j] -= lr * d_W_v[i][j]

        # Embedding
        for i, tid in enumerate(tokens):
            for j in range(d):
                self.embed[tid][j] -= lr * d_X[i][j]

        return loss

    # ═══════════════════════════════════════════════════════════
    #  التوليد
    # ═══════════════════════════════════════════════════════════

    def generate(self, start, word2id, id2word, length=5, temperature=0.8):
        tokens = [word2id.get(w, word2id["<BOS>"]) for w in start.split()]

        for _ in range(length):
            logits = self.forward(tokens)

            if temperature != 1.0:
                logits = [x / temperature for x in logits]

            probs = softmax(logits)
            chosen = max(range(len(probs)), key=lambda i: probs[i])

            if id2word[chosen] == "<EOS>":
                break
            tokens.append(chosen)

        return " ".join(id2word[t] for t in tokens if id2word[t] not in ("<BOS>", "<EOS>"))


# ═══════════════════════════════════════════════════════════
#  التدريب
# ═══════════════════════════════════════════════════════════

def train(model, batch, word2id, epochs=30, lr=0.01):
    losses = []

    for epoch in range(epochs):
        random.shuffle(batch)
        epoch_loss = 0

        for input_words, target_word in batch:
            input_ids = [word2id.get(w, 0) for w in input_words]
            target_id = word2id.get(target_word, 0)

            model.forward(input_ids)
            loss = model.backward(target_id, lr)
            epoch_loss += loss

        avg = epoch_loss / len(batch)
        losses.append(avg)
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  [Epoch {epoch+1:2d}] Loss: {avg:.4f}")

    return losses


# ═══════════════════════════════════════════════════════════
#  التشغيل
# ═══════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  🧠 HBS-7 — Self-Attention + FF")
    print("═" * 60)
    print()

    lines = load_corpus("data/corpus.txt")
    print(f"📖 البيانات: {len(lines)} سطر")
    print()

    vocab, word2id, id2word = build_vocab(lines)
    print(f"📚 القاموس: {len(vocab)} كلمة")
    print()

    batch = []
    for line in lines:
        words = line.split()
        if 3 <= len(words) <= 6:
            batch.append((words[:-1], words[-1]))

    print(f"🎓 Batch: {len(batch)} عينة")
    print()

    model = Habs7(vocab_size=len(vocab), d_model=16, d_ff=32)

    print("🎓 جاري التدريب...")
    print()
    losses = train(model, batch, word2id, epochs=30, lr=0.01)

    print()
    print(f"📉 الابتدائي: {losses[0]:.4f}")
    print(f"📉 النهائي:   {losses[-1]:.4f}")
    imp = (losses[0] - losses[-1]) / losses[0] * 100
    print(f"📈 التحسين:   {imp:.1f}%")
    print()

    print("─" * 60)
    print("🎨 التوليد:")
    print("─" * 60)
    print()

    for s in ["قل", "هو", "إنا", "يوم", "الله", "الذي"]:
        result = model.generate(s, word2id, id2word, length=5, temperature=0.8)
        print(f"   [{s}] → {result}")

    print()
    print("═" * 60)
    print("  ⚠️  تعليمي فقط — احترام القرآن.")
    print("═" * 60)


if __name__ == "__main__":
    main()
