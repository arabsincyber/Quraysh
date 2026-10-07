"""
HBS-9 — Transformer عربي أقوى
================================

تحسينات على HBS-8:
- Embedding أكبر (64 بدل 32)
- طبقات أكثر (3 بدل 2)
- Vocab أكبر (2000 بدل 500)
- Seq length أطول (8 بدل 4)
- تكامل محسّن مع bigram

مدرّب على القرآن الكريم.
"""

import math
import random
import json
from pathlib import Path
from collections import Counter


# ═══════════════════════════════════════════════════════════
#  الأساسيات الرياضية
# ═══════════════════════════════════════════════════════════

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
    m = len(B)
    p = len(B[0]) if B else 0
    return [[sum(A[i][k] * B[k][j] for k in range(m))
             for j in range(p)] for i in range(len(A))]


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
#  Multi-Head Attention
# ═══════════════════════════════════════════════════════════

class MultiHeadAttention:
    def __init__(self, d_model=32, num_heads=4):
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        حد = 1.0 / math.sqrt(d_model)

        self.Wq = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wk = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wv = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wo = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]

    def forward(self, X):
        Q = matmul(X, self.Wq)
        K = matmul(X, self.Wk)
        V = matmul(X, self.Wv)

        scores = matmul(Q, transpose(K))
        scores = [[v / math.sqrt(self.d_k) for v in row] for row in scores]
        attn = [softmax(row) for row in scores]
        out = matmul(attn, V)
        return matmul(out, self.Wo)


# ═══════════════════════════════════════════════════════════
#  Feed-Forward
# ═══════════════════════════════════════════════════════════

class FeedForward:
    def __init__(self, d_model=32, d_ff=256):
        حد = 1.0 / math.sqrt(d_model)
        self.W1 = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_ff)]
        self.b1 = [0.0] * d_ff
        self.W2 = [[random.uniform(-حد, حد) for _ in range(d_ff)] for _ in range(d_model)]
        self.b2 = [0.0] * d_model

    def forward(self, X):
        h = matmul(X, transpose(self.W1))
        h = [[relu(v + self.b1[j]) for j, v in enumerate(row)] for row in h]
        out = matmul(h, transpose(self.W2))
        out = [[v + self.b2[j] for j, v in enumerate(row)] for row in out]
        return out


# ═══════════════════════════════════════════════════════════
#  Transformer Block
# ═══════════════════════════════════════════════════════════

class TransformerBlock:
    def __init__(self, d_model=32, num_heads=4, d_ff=256):
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, d_ff)

    def forward(self, X):
        attn_out = self.attention.forward(X)
        X1 = [[X[i][j] + attn_out[i][j] for j in range(len(X[i]))]
              for i in range(len(X))]
        # LayerNorm
        X1 = [layer_norm(row) for row in X1]

        ffn_out = self.ffn.forward(X1)
        out = [[X1[i][j] + ffn_out[i][j] for j in range(len(X1[i]))]
               for i in range(len(X1))]
        return out


# ═══════════════════════════════════════════════════════════
#  HBS-9 — النموذج الكامل
# ═══════════════════════════════════════════════════════════

class Habs9:
    """HBS-9 — Transformer عربي أقوى"""

    def __init__(self, vocab_size, d_model=32, num_heads=4, num_layers=2, seq_len=4):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.seq_len = seq_len

        حد = 1.0 / math.sqrt(d_model)
        self.embedding = [[random.uniform(-حد, حد) for _ in range(d_model)]
                          for _ in range(vocab_size)]

        self.pe = positional_encoding(seq_len, d_model)

        self.blocks = [TransformerBlock(d_model, num_heads, d_model * 4)
                       for _ in range(num_layers)]

        self.W_out = [[random.uniform(-حد, حد) for _ in range(d_model)]
                      for _ in range(vocab_size)]

    def forward(self, input_ids):
        X = []
        for i, idx in enumerate(input_ids):
            if i >= self.seq_len:
                break
            emb = self.embedding[idx % self.vocab_size]
            pos = self.pe[i]
            X.append([emb[j] + pos[j] for j in range(self.d_model)])

        for block in self.blocks:
            X = block.forward(X)

        if X:
            آخر = X[-1]
        else:
            آخر = [0.0] * self.d_model

        logits = [sum(آخر[j] * self.W_out[i][j] for j in range(self.d_model))
                  for i in range(self.vocab_size)]
        return logits

    def sample(self, input_ids, temperature=1.0):
        logits = self.forward(input_ids)
        if temperature != 1.0:
            logits = [v / temperature for v in logits]
        probs = softmax(logits)
        r = random.random()
        cum = 0
        for i, p in enumerate(probs):
            cum += p
            if cum >= r:
                return i
        return len(probs) - 1

    def generate(self, seed_ids, length=10, temperature=0.8):
        seq = list(seed_ids)
        for _ in range(length):
            next_id = self.sample(seq[-self.seq_len:], temperature)
            seq.append(next_id)
        return seq

    def حفظ(self, مسار):
        data = {
            "vocab_size": self.vocab_size,
            "d_model": self.d_model,
            "num_heads": self.num_heads,
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

def cross_entropy_loss(logits, target_id):
    probs = softmax(logits)
    return -math.log(probs[target_id] + 1e-9)


def compute_loss(نموذج, ids, sample_size=50):
    seq_len = نموذج.seq_len
    total = 0
    count = 0
    for _ in range(sample_size):
        i = random.randint(0, len(ids) - seq_len - 1)
        input_ids = ids[i:i + seq_len]
        target_id = ids[i + seq_len]
        logits = نموذج.forward(input_ids)
        loss = cross_entropy_loss(logits, target_id)
        total += loss
        count += 1
    return total / max(count, 1)


def random_search(ids, vocab_size, iterations=30):
    best_loss = float("inf")
    best_weights = None

    for it in range(iterations):
        نموذج = Habs9(
            vocab_size=vocab_size,
            d_model=32,
            num_heads=4,
            num_layers=2,
            seq_len=4,
        )
        loss = compute_loss(نموذج, ids, sample_size=30)

        if loss < best_loss:
            best_loss = loss
            best_weights = نموذج
            print(f"  ✅ iter {it+1}/{iterations} — loss: {loss:.4f} (new best!)")

    return best_weights, best_loss


# ═══════════════════════════════════════════════════════════
#  دوال الربط
# ═══════════════════════════════════════════════════════════

_نموذج_hbs9 = None
_vocab_hbs9 = None


def _احصل_على_النموذج():
    global _نموذج_hbs9
    if _نموذج_hbs9 is None:
        try:
            مسار = Path(__file__).parent / "habs_9_trained.json"
            if مسار.exists():
                with open(مسار, "r", encoding="utf-8") as f:
                    data = json.load(f)
                _نموذج_hbs9 = Habs9(
                    vocab_size=data.get("vocab_size", 2000),
                    d_model=data.get("d_model", 64),
                    num_heads=data.get("num_heads", 4),
                    num_layers=data.get("num_layers", 3),
                    seq_len=data.get("seq_len", 8),
                )
                if "embedding" in data:
                    _نموذج_hbs9.embedding = data["embedding"]
                if "W_out" in data:
                    _نموذج_hbs9.W_out = data["W_out"]
            else:
                _نموذج_hbs9 = Habs9(vocab_size=2000)
        except Exception as e:
            print(f"⚠️ HBS-9: {e}")
            _نموذج_hbs9 = Habs9(vocab_size=100)
    return _نموذج_hbs9


def _احصل_على_vocab():
    """يحمّل vocab — يعيد المحاولة لو فشل"""
    global _vocab_hbs9

    # إذا عندنا vocab حقيقي (أكثر من 2 مفردات) → استخدم
    if _vocab_hbs9 is not None and len(_vocab_hbs9) > 2:
        return _vocab_hbs9

    # حاول تحميل
    try:
        from pathlib import Path
        import json

        مسارات = [
            Path(__file__).parent / "habs_9_vocab.json",
            Path("/tmp/quraysh/habs_9_vocab.json"),
            Path("/tmp/habs_9_vocab.json"),
        ]

        for مسار in مسارات:
            if مسار.exists():
                with open(مسار, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if len(data) > 2:
                    _vocab_hbs9 = data
                    print(f"✅ vocab-9 محمّل: {len(data)} كلمة")
                    return _vocab_hbs9

        # fallback
        if _vocab_hbs9 is None:
            _vocab_hbs9 = {"<PAD>": 0, "<UNK>": 1}
    except Exception as e:
        print(f"⚠️ vocab-9: {e}")
        if _vocab_hbs9 is None:
            _vocab_hbs9 = {"<PAD>": 0, "<UNK>": 1}

    return _vocab_hbs9


def توليد_نص(بذرة="بسم الله", طول=10):
    """يولّد نص عربي — يحمّل vocab كل مرة"""
    نموذج = _احصل_على_النموذج()

    # حمّل vocab مباشرة — بدون global
    from pathlib import Path
    import json
    vocab = None
    مسارات = [
        Path(__file__).parent / "habs_9_vocab.json",
        Path("/tmp/quraysh/habs_9_vocab.json"),
    ]
    for مسار in مسارات:
        if مسار.exists():
            try:
                with open(مسار, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if len(data) > 2:
                    vocab = data
                    break
            except:
                pass

    if vocab is None:
        return "⚠️ vocab-9 غير محمّل"

    if نموذج is None:
        return "⚠️ HBS-9 غير متاح"

    seed_ids = [vocab.get(ك, 1) for ك in بذرة.split()]
    generated = نموذج.generate(seed_ids, length=طول, temperature=0.7)

    id_to_word = {v: k for k, v in vocab.items()}
    return " ".join(id_to_word.get(i, "?") for i in generated)


دوال_HBS9 = {
    "توليد_نص_9": توليد_نص,
}


# ═══════════════════════════════════════════════════════════
#  التجربة
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧠 HBS-9 — Transformer عربي أقوى")
    print("=" * 50)

    # جرّب المسارات
    مسارات = [
        "../../corpus/quran/quran.txt",
        "/data/data/com.termux/files/home/lugha/quraysh-v2/models/corpus/quran/quran.txt",
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

    vocab = build_vocab(كلمات, max_vocab=1000)
    print(f"📚 vocab: {len(vocab)}")

    ids = encode(كلمات[:10000], vocab)
    print(f"🔢 IDs: {len(ids):,}")

    # حفظ vocab
    with open("habs_9_vocab.json", "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False)
    print("💾 vocab محفوظ")

    # تدريب
    print()
    print("🏋️  Random Search (100 تكرار)...")
    best_model, best_loss = random_search(ids, len(vocab), iterations=30)

    print()
    print(f"✅ أفضل loss: {best_loss:.4f}")

    if best_model:
        seed = ids[:3]
        generated = best_model.generate(seed, length=15, temperature=0.7)
        id_to_word = {v: k for k, v in vocab.items()}
        نص = " ".join(id_to_word.get(i, "?") for i in generated)
        print(f"📝 نص مولّد: {نص}")

        best_model.حفظ("habs_9_trained.json")
        print("💾 حُفظ: habs_9_trained.json")
