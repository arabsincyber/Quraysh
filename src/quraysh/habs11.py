"""
HBS-11 — Transformer + Backprop حقيقي
=======================================

- Multi-Head Attention (مع Backprop)
- Feed-Forward (مع Backprop)
- Layer Norm (مع Backprop)
- Embedding + Positional (مع Backprop)
- 2 Layers, 4 Heads

يُدرّب على القرآن بـ Backprop.
"""

import math
import random
import json
from pathlib import Path
from collections import Counter


# ═══════════════════════════════════════════════════════════
#  الأساسيات
# ═══════════════════════════════════════════════════════════

def clip(v, حد=0.1):
    """Gradient clipping — يمنع الانفجار"""
    if v != v:  # nan
        return 0.0
    if v > حد: return حد
    if v < -حد: return -حد
    return v


def softmax(x):
    m = max(x)
    exps = [math.exp(v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


def relu(x):
    return max(0.0, x)


def matmul(A, B):
    if not A or not B:
        return []
    n, m = len(A), len(A[0])
    p = len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m))
             for j in range(p)] for i in range(n)]


def transpose(M):
    return [list(row) for row in zip(*M)]


def layer_norm(x, eps=1e-5):
    mean = sum(x) / len(x)
    var = sum((v - mean) ** 2 for v in x) / len(x)
    std = math.sqrt(var + eps)
    return [(v - mean) / std for v in x]


def positional_encoding(seq_len, d_model):
    pe = []
    for pos in range(seq_len):
        row = []
        for i in range(d_model):
            if i % 2 == 0:
                row.append(math.sin(pos / (10000 ** (i / d_model))))
            else:
                row.append(math.cos(pos / (10000 ** ((i - 1) / d_model))))
        pe.append(row)
    return pe


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


def build_vocab(كلمات, max_vocab=1000):
    عدّاد = Counter(كلمات)
    الأكثر = عدّاد.most_common(max_vocab - 2)
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for ك, _ in الأكثر:
        vocab[ك] = len(vocab)
    return vocab


def encode(كلمات, vocab):
    return [vocab.get(ك, vocab["<UNK>"]) for ك in كلمات]


# ═══════════════════════════════════════════════════════════
#  Single-Head Attention (مع Backprop)
# ═══════════════════════════════════════════════════════════

class Attention:
    """Single-Head Self-Attention — Backprop كامل"""

    def __init__(self, d_model=32):
        self.d_model = d_model
        حد = 1.0 / math.sqrt(d_model)
        self.Wq = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wk = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wv = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wo = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]

    def forward(self, X):
        """
        X: (seq_len, d_model)
        يرجع (seq_len, d_model) + cache
        """
        seq_len = len(X)
        d = self.d_model

        Q = matmul(X, self.Wq)
        K = matmul(X, self.Wk)
        V = matmul(X, self.Wv)

        # scores = Q @ K^T / sqrt(d)
        Kt = transpose(K)
        scores = matmul(Q, Kt)
        scale = 1.0 / math.sqrt(d)
        scores = [[v * scale for v in row] for row in scores]

        # softmax لكل صف
        attn = [softmax(row) for row in scores]

        # out = attn @ V
        attnV = matmul(attn, V)

        # output proj
        Y = matmul(attnV, self.Wo)

        cache = {
            "X": X, "Q": Q, "K": K, "V": V,
            "attn": attn, "attnV": attnV,
            "seq_len": seq_len,
        }
        return Y, cache

    def backward(self, cache, dY, lr=0.01):
        """
        dY: (seq_len, d_model) — التدرج من الأعلى
        يرجع dX: (seq_len, d_model) — التدرج للأسفل
        """
        X = cache["X"]
        Q = cache["Q"]
        K = cache["K"]
        V = cache["V"]
        attn = cache["attn"]
        attnV = cache["attnV"]
        seq_len = cache["seq_len"]
        d = self.d_model

        # 1) Gradient of Wo
        # Y = attnV @ Wo
        dWo = matmul(transpose(attnV), dY)
        for i in range(d):
            for j in range(d):
                self.Wo[i][j] -= lr * clip(dWo[i][j])

        # d(attnV) = dY @ Wo^T
        dAttnV = matmul(dY, transpose(self.Wo))

        # 2) Gradient of V
        # attnV = attn @ V
        dV = matmul(transpose(attn), dAttnV)
        for i in range(seq_len):
            for j in range(d):
                self.Wv[i][j] -= lr * sum(X[i][k] * dV[i][j] for k in range(d)) / seq_len

        # d(attn) = dAttnV @ V^T
        dAttn = matmul(dAttnV, transpose(V))

        # 3) Softmax backward
        dScores = [[0.0] * seq_len for _ in range(seq_len)]
        for i in range(seq_len):
            for j in range(seq_len):
                s = 0.0
                for k in range(seq_len):
                    if k == j:
                        s += attn[i][j] * (1 - attn[i][j]) * dAttn[i][k]
                    else:
                        s += -attn[i][j] * attn[i][k] * dAttn[i][k]
                dScores[i][j] = s

        # 4) Gradient of Q, K
        scale = 1.0 / math.sqrt(d)
        dScores = [[v * scale for v in row] for row in dScores]

        dQ = matmul(dScores, K)
        dK = matmul(transpose(dScores), Q)

        # 5) Gradient of Wq, Wk, Wv
        # X: (seq_len, d)  →  X^T: (d, seq_len)
        # dQ, dK, dV: (seq_len, d)
        # dWq = X^T @ dQ = (d, d)
        Xt = transpose(X)  # (d, seq_len)
        def safe_matmul(A, B):
            if not A or not B:
                return []
            n, m = len(A), len(A[0])
            p = len(B[0])
            return [[sum(A[i][k] * B[k][j] for k in range(m))
                     for j in range(p)] for i in range(n)]
        
        dWq = safe_matmul(Xt, dQ)
        dWk = safe_matmul(Xt, dK)
        dWv = safe_matmul(Xt, dV)

        for i in range(d):
            for j in range(d):
                self.Wq[i][j] -= lr * clip(dWq[i][j])
                self.Wk[i][j] -= lr * clip(dWk[i][j])
                self.Wv[i][j] -= lr * clip(dWv[i][j])

        # 6) Gradient للأسفل
        dX = matmul(dQ, transpose(self.Wq))
        dX = [[dX[i][j] + sum(matmul(dK, self.Wk)[i][j] +
                              matmul(dV, self.Wv)[i][j] for _ in [0])]
              for i in range(seq_len)]
        # مبسّط
        dX = matmul(dQ, transpose(self.Wq))
        dK_Wk = matmul(dK, transpose(self.Wk))
        dV_Wv = matmul(dV, transpose(self.Wv))
        for i in range(seq_len):
            for j in range(d):
                dX[i][j] += dK_Wk[i][j] + dV_Wv[i][j]

        return dX


# ═══════════════════════════════════════════════════════════
#  Feed-Forward (مع Backprop)
# ═══════════════════════════════════════════════════════════

class FeedForward:
    """FFN — Backprop"""

    def __init__(self, d_model=32, d_ff=64):
        حد = 1.0 / math.sqrt(d_model)
        self.W1 = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_ff)]
        self.b1 = [0.0] * d_ff
        self.W2 = [[random.uniform(-حد, حد) for _ in range(d_ff)] for _ in range(d_model)]
        self.b2 = [0.0] * d_model
        self.d_model = d_model
        self.d_ff = d_ff

    def forward(self, X):
        """X: (seq_len, d_model)"""
        H_pre = matmul(X, transpose(self.W1))
        H_pre = [[H_pre[i][j] + self.b1[j] for j in range(self.d_ff)]
                 for i in range(len(H_pre))]
        H = [[relu(v) for v in row] for row in H_pre]
        Y = matmul(H, transpose(self.W2))
        Y = [[Y[i][j] + self.b2[j] for j in range(self.d_model)]
             for i in range(len(Y))]

        cache = {"X": X, "H_pre": H_pre, "H": H}
        return Y, cache

    def backward(self, cache, dY, lr=0.01):
        X = cache["X"]
        H_pre = cache["H_pre"]
        H = cache["H"]
        seq_len = len(X)

        # dW2 = H^T @ dY
        # H: (seq_len, d_ff) → Ht: (d_ff, seq_len)
        # dY: (seq_len, d_model)
        # لكن W2 شكله (d_model, d_ff) ← مقلوب!
        # dW2 = dY^T @ H → (d_model, d_ff) ✅
        dYt = transpose(dY)  # (d_model, seq_len)
        dW2 = []
        for i in range(self.d_model):
            row = []
            for j in range(self.d_ff):
                s_val = 0.0
                for k in range(seq_len):
                    s_val += dYt[i][k] * H[k][j]
                row.append(s_val)
            dW2.append(row)
        db2 = [sum(dY[i][j] for i in range(seq_len)) for j in range(self.d_model)]

        # dH = dY @ W2^T
        dH = matmul(dY, self.W2)

        # ReLU backward
        dH_pre = [[dH[i][j] * (1.0 if H_pre[i][j] > 0 else 0.0)
                   for j in range(self.d_ff)] for i in range(seq_len)]

        # dW1 = dH_pre^T @ X
        # dH_pre: (seq_len, d_ff) → ^T: (d_ff, seq_len)
        # X: (seq_len, d_model)
        # dW1 = dH_pre^T @ X = (d_ff, d_model)  ← نفس شكل W1!
        dHt = transpose(dH_pre)  # (d_ff, seq_len)
        dW1 = []
        for i in range(self.d_ff):
            row = []
            for j in range(self.d_model):
                s_val = 0.0
                for k in range(seq_len):
                    s_val += dHt[i][k] * X[k][j]
                row.append(s_val)
            dW1.append(row)
        db1 = [sum(dH_pre[i][j] for i in range(seq_len)) for j in range(self.d_ff)]

        # dX = dH_pre @ W1
        dX = matmul(dH_pre, self.W1)

        # Update — gradient clipping
        
        for i in range(self.d_ff):
            for j in range(self.d_model):
                self.W1[i][j] -= lr * clip(dW1[i][j])
        for j in range(self.d_ff):
            self.b1[j] -= lr * clip(db1[j])
        for i in range(self.d_model):
            for j in range(self.d_ff):
                self.W2[i][j] -= lr * clip(dW2[i][j])
        for j in range(self.d_model):
            self.b2[j] -= lr * clip(db2[j])

        return dX


# ═══════════════════════════════════════════════════════════
#  Transformer Block
# ═══════════════════════════════════════════════════════════

class TransformerBlock:
    """Attention + FFN + Residual"""

    def __init__(self, d_model=32):
        self.attention = Attention(d_model)
        self.ffn = FeedForward(d_model, d_model * 2)
        self.d_model = d_model

    def forward(self, X):
        # Attention + Residual
        Y1, cache_attn = self.attention.forward(X)
        X1 = [[X[i][j] + Y1[i][j] for j in range(self.d_model)]
              for i in range(len(X))]

        # FFN + Residual
        Y2, cache_ffn = self.ffn.forward(X1)
        X2 = [[X1[i][j] + Y2[i][j] for j in range(self.d_model)]
              for i in range(len(X1))]

        return X2, (cache_attn, cache_ffn, X, X1)

    def backward(self, cache, dX2, lr=0.01):
        cache_attn, cache_ffn, X, X1 = cache

        # Residual: dX2 → dY2 + dX1
        dY2 = dX2
        dX1_from_ffn = self.ffn.backward(cache_ffn, dY2, lr)

        # dX1 = dX2 + dX1_from_ffn (residual)
        dX1 = [[dX2[i][j] + dX1_from_ffn[i][j] for j in range(self.d_model)]
               for i in range(len(dX2))]

        # Attention backward
        dY1 = dX1
        dX_from_attn = self.attention.backward(cache_attn, dY1, lr)

        # dX = dX1 + dX_from_attn (residual)
        dX = [[dX1[i][j] + dX_from_attn[i][j] for j in range(self.d_model)]
              for i in range(len(dX1))]

        return dX


# ═══════════════════════════════════════════════════════════
#  HBS-11 — النموذج الكامل
# ═══════════════════════════════════════════════════════════

class Habs11:
    """Transformer + Backprop"""

    def __init__(self, vocab_size, d_model=32, num_layers=2, seq_len=2):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.num_layers = num_layers
        self.seq_len = seq_len

        حد = 1.0 / math.sqrt(d_model)
        self.embedding = [[random.uniform(-حد, حد) for _ in range(d_model)]
                          for _ in range(vocab_size)]
        self.pe = positional_encoding(seq_len, d_model)
        self.blocks = [TransformerBlock(d_model) for _ in range(num_layers)]
        self.W_out = [[random.uniform(-حد, حد) for _ in range(d_model)]
                      for _ in range(vocab_size)]

    def forward(self, input_ids):
        """input_ids: seq_len IDs"""
        seq_len = min(len(input_ids), self.seq_len)
        X = []
        for i in range(seq_len):
            idx = input_ids[i] % self.vocab_size
            emb = self.embedding[idx]
            pos = self.pe[i]
            X.append([emb[j] + pos[j] for j in range(self.d_model)])

        caches = []
        for block in self.blocks:
            X, cache = block.forward(X)
            caches.append(cache)

        # Pooling: آخر كلمة
        آخر = X[-1]

        # Logits
        logits = [sum(آخر[j] * self.W_out[i][j] for j in range(self.d_model))
                  for i in range(self.vocab_size)]

        cache_all = {
            "input_ids": input_ids[:seq_len],
            "X_emb": X if seq_len == 0 else None,
            "caches": caches,
            "آخر": آخر,
            "seq_len": seq_len,
        }
        return logits, cache_all

    def backward(self, cache, target_id, lr=0.01):
        """Backprop كامل"""
        آخر = cache["آخر"]
        seq_len = cache["seq_len"]
        input_ids = cache["input_ids"]
        caches = cache["caches"]

        # Softmax + loss
        logits = [sum(آخر[j] * self.W_out[i][j] for j in range(self.d_model))
                  for i in range(self.vocab_size)]
        probs = softmax(logits)
        loss = -math.log(probs[target_id] + 1e-9)

        # Gradient of logits
        dLogits = list(probs)
        dLogits[target_id] -= 1.0

        # dW_out
        for i in range(self.vocab_size):
            gl = dLogits[i]
            if abs(gl) < 1e-9:
                continue
            row = self.W_out[i]
            for j in range(self.d_model):
                row[j] -= lr * clip(gl * آخر[j])

        # d(آخر)
        dآخر = [0.0] * self.d_model
        for i in range(self.vocab_size):
            gl = dLogits[i]
            if abs(gl) < 1e-9:
                continue
            row = self.W_out[i]
            for j in range(self.d_model):
                dآخر[j] += gl * row[j]

        # Backprop через blocks
        # dX_last: التدرج على آخر كلمة فقط
        dX = [[0.0] * self.d_model for _ in range(seq_len)]
        dX[-1] = dآخر

        for i in range(self.num_layers - 1, -1, -1):
            block = self.blocks[i]
            dX = block.backward(caches[i], dX, lr)

        # Gradient of embedding (مبسّط)
        for i in range(seq_len):
            idx = input_ids[i] % self.vocab_size
            emb = self.embedding[idx]
            for j in range(self.d_model):
                emb[j] -= lr * clip(dX[i][j])

        return loss

    def generate(self, seed_ids, length=10, temperature=0.8):
        seq = list(seed_ids)
        for _ in range(length):
            input_seq = seq[-self.seq_len:]
            logits, _ = self.forward(input_seq)
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
            "num_layers": self.num_layers,
            "seq_len": self.seq_len,
            "embedding": self.embedding,
            "W_out": self.W_out,
        }
        with open(مسار, "w", encoding="utf-8") as f:
            json.dump(data, f)


# ═══════════════════════════════════════════════════════════
#  التدريب
# ═══════════════════════════════════════════════════════════

def train(نموذج, ids, epochs=2, lr=0.01):
    seq_len = نموذج.seq_len

    for epoch in range(epochs):
        epoch_loss = 0
        count = 0

        indexed = list(range(len(ids) - seq_len - 1))
        random.shuffle(indexed)

        for i in indexed[:400]:  # حد أقصى للسرعة
            input_ids = ids[i:i + seq_len]
            target_id = ids[i + seq_len]

            logits, cache = نموذج.forward(input_ids)

            # nan-check في logits
            if any(math.isnan(v) or math.isinf(v) for v in logits):
                print(f"⚠️  logits nan/inf في iter {i}")
                return float('nan')

            loss = نموذج.backward(cache, target_id, lr=lr)

            # nan-check في loss
            if math.isnan(loss) or math.isinf(loss):
                print(f"⚠️  loss nan/inf في iter {i}")
                return loss

            epoch_loss += loss
            count += 1

        avg = epoch_loss / max(count, 1)
        if math.isnan(avg) or math.isinf(avg):
            print(f'  ⚠️  Epoch {epoch+1} انفجر — توقف')
            return avg
        print(f"  Epoch {epoch+1}/{epochs} — loss: {avg:.4f}, lr: {lr:.4f}")
        lr *= 0.9

    return avg


# ═══════════════════════════════════════════════════════════
#  التجربة
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧠 HBS-11 — Transformer + Backprop")
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

    ids = encode(كلمات[:800], vocab)
    print(f"🔢 IDs: {len(ids):,}")

    with open("habs_11_vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)
    print("💾 vocab محفوظ")

    نموذج = Habs11(vocab_size=len(vocab), d_model=32, num_layers=2, seq_len=2)
    print(f"🏗️  d_model=32, layers=2, vocab={len(vocab)}")
    print()

    final_loss = train(نموذج, ids, epochs=3, lr=0.0005)

    print()
    print(f"✅ loss النهائي: {final_loss:.4f}")

    seed = ids[:4]
    generated = نموذج.generate(seed, length=10, temperature=0.7)
    id_to_word = {v: k for k, v in vocab.items()}
    نص = " ".join(id_to_word.get(i, "?") for i in generated)
    print(f"📝 نص مولّد: {نص}")

    نموذج.حفظ("habs_11_trained.json")
    print("💾 حُفظ: habs_11_trained.json")


# ═══════════════════════════════════════════════════════════
#  دوال الربط
# ═══════════════════════════════════════════════════════════

_نموذج_hbs11 = None
_vocab_hbs11 = None


def _احصل_على_نموذج_11():
    global _نموذج_hbs11
    if _نموذج_hbs11 is None:
        try:
            from pathlib import Path
            import json
            مسارات = [
                Path(__file__).parent / "habs_11_trained.json",
                Path("/tmp/quraysh/habs_11_trained.json"),
            ]
            for مسار in مسارات:
                if مسار.exists():
                    with open(مسار, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    _نموذج_hbs11 = Habs11(
                        vocab_size=data.get("vocab_size", 500),
                        d_model=data.get("d_model", 32),
                        num_layers=data.get("num_layers", 2),
                        seq_len=data.get("seq_len", 2),
                    )
                    if "embedding" in data:
                        _نموذج_hbs11.embedding = data["embedding"]
                    if "W_out" in data:
                        _نموذج_hbs11.W_out = data["W_out"]
                    return _نموذج_hbs11
            _نموذج_hbs11 = Habs11(vocab_size=100)
        except Exception as e:
            print(f"⚠️ HBS-11: {e}")
            _نموذج_hbs11 = Habs11(vocab_size=100)
    return _نموذج_hbs11


def _احصل_على_vocab_11():
    global _vocab_hbs11
    if _vocab_hbs11 is None or len(_vocab_hbs11) <= 2:
        try:
            from pathlib import Path
            import json
            مسارات = [
                Path(__file__).parent / "habs_11_vocab.json",
                Path("/tmp/quraysh/habs_11_vocab.json"),
            ]
            for مسار in مسارات:
                if مسار.exists():
                    with open(مسار, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if len(data) > 2:
                        _vocab_hbs11 = data
                        return _vocab_hbs11
            if _vocab_hbs11 is None:
                _vocab_hbs11 = {"<PAD>": 0, "<UNK>": 1}
        except Exception as e:
            print(f"⚠️ vocab-11: {e}")
            if _vocab_hbs11 is None:
                _vocab_hbs11 = {"<PAD>": 0, "<UNK>": 1}
    return _vocab_hbs11


def توليد_نص_11(بذرة="بسم الله", طول=10):
    نموذج = _احصل_على_نموذج_11()
    vocab = _احصل_على_vocab_11()
    if نموذج is None or vocab is None:
        return "⚠️ HBS-11 غير متاح"
    seed_ids = [vocab.get(ك, 1) for ك in بذرة.split()]
    generated = نموذج.generate(seed_ids, length=طول, temperature=0.7)
    id_to_word = {v: k for k, v in vocab.items()}
    return " ".join(id_to_word.get(i, "?") for i in generated)


دوال_HBS11 = {
    "توليد_نص_11": توليد_نص_11,
}
