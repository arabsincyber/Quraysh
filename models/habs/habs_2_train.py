"""
HBS-2 — التدريب المبسّط
=========================

تدريب Transformer — بـ Numerical Gradient.

⚠️  تعليمي فقط.
"""

import math
import random
from pathlib import Path
from copy import deepcopy


# ═══════════════════════════════════════════════════════════
#  الأساسيات
# ═══════════════════════════════════════════════════════════

def softmax(x):
    m = max(x)
    exps = [math.exp(v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


def log_softmax(x):
    """Log Softmax — للاستقرار"""
    m = max(x)
    shifted = [v - m for v in x]
    log_sum = math.log(sum(math.exp(v) for v in shifted))
    return [v - log_sum for v in shifted]


def matmul(A, B):
    cols_B = len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(cols_B)] for i in range(len(A))]


def transpose(M):
    return [list(row) for row in zip(*M)]


def scale(M, f):
    return [[x * f for x in row] for row in M]


def add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def layer_norm(X, eps=1e-6):
    result = []
    for row in X:
        mean = sum(row) / len(row)
        var = sum((x - mean) ** 2 for x in row) / len(row)
        std = math.sqrt(var + eps)
        result.append([(x - mean) / std for x in row])
    return result


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
#  Embedding
# ═══════════════════════════════════════════════════════════

class Embedding:
    def __init__(self, vocab_size, d_model, seed=42):
        random.seed(seed)
        self.d_model = d_model
        self.vocab_size = vocab_size
        scale_v = math.sqrt(2.0 / (vocab_size + d_model))
        self.table = [
            [random.gauss(0, scale_v) for _ in range(d_model)]
            for _ in range(vocab_size)
        ]

    def __call__(self, token_id):
        return self.table[token_id]


def positional_encoding(seq_len, d_model):
    pe = [[0.0] * d_model for _ in range(seq_len)]
    for pos in range(seq_len):
        for i in range(d_model):
            if i % 2 == 0:
                pe[pos][i] = math.sin(pos / (10000 ** (i / d_model)))
            else:
                pe[pos][i] = math.cos(pos / (10000 ** ((i - 1) / d_model)))
    return pe


# ═══════════════════════════════════════════════════════════
#  Attention
# ═══════════════════════════════════════════════════════════

def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = len(Q[0])
    scores = matmul(Q, transpose(K))
    scores = scale(scores, 1.0 / math.sqrt(d_k))

    if mask:
        for i in range(len(scores)):
            for j in range(len(scores[i])):
                if mask[i][j] == 0:
                    scores[i][j] = -1e9

    weights = [softmax(row) for row in scores]
    output = matmul(weights, V)
    return output, weights


def causal_mask(seq_len):
    return [[1 if j <= i else 0 for j in range(seq_len)] for i in range(seq_len)]


# ═══════════════════════════════════════════════════════════
#  Simple Transformer (بدون Multi-Head — للتبسيط)
# ═══════════════════════════════════════════════════════════

class SimpleHabs2:
    """
    Transformer مبسّط:
    - Single-Head Attention
    - Single Layer
    - بدون Residual (للبساطة)
    """

    def __init__(self, vocab_size, d_model=16, d_ff=32, seed=42):
        random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.d_ff = d_ff

        def rand_matrix(rows, cols):
            scale_v = math.sqrt(2.0 / (rows + cols))
            return [[random.gauss(0, scale_v) for _ in range(cols)]
                    for _ in range(rows)]

        self.embedding = Embedding(vocab_size, d_model, seed)

        # Attention
        self.W_q = rand_matrix(d_model, d_model)
        self.W_k = rand_matrix(d_model, d_model)
        self.W_v = rand_matrix(d_model, d_model)

        # FF
        self.W1 = rand_matrix(d_model, d_ff)
        self.W2 = rand_matrix(d_ff, d_model)

        # Output
        self.W_out = rand_matrix(d_model, vocab_size)

    def forward(self, token_ids):
        seq_len = len(token_ids)

        # Embedding
        X = [self.embedding(tid) for tid in token_ids]

        # PE
        pe = positional_encoding(seq_len, self.d_model)
        X = add(X, pe)

        # Attention
        Q = matmul(X, self.W_q)
        K = matmul(X, self.W_k)
        V = matmul(X, self.W_v)

        mask = causal_mask(seq_len)
        attn_out, _ = scaled_dot_product_attention(Q, K, V, mask)

        # FF
        h = matmul(attn_out, self.W1)
        h = [[max(0, v) for v in row] for row in h]  # ReLU
        ff_out = matmul(h, self.W2)

        # Output
        logits = matmul(ff_out, self.W_out)
        return logits


# ═══════════════════════════════════════════════════════════
#  Loss Function
# ═══════════════════════════════════════════════════════════

def cross_entropy_loss(logits, target_id):
    """
    Cross-Entropy — لآخر توقع.
    logits: قائمة أرقام
    target_id: الرقم الصحيح
    """
    log_probs = log_softmax(logits)
    return -log_probs[target_id]


# ═══════════════════════════════════════════════════════════
#  Numerical Gradient (للتجربة)
# ═══════════════════════════════════════════════════════════

def compute_loss(model, input_ids, target_id):
    """يحسب الـ Loss لجملة"""
    logits = model.forward(input_ids)
    return cross_entropy_loss(logits[-1], target_id)


def numerical_gradient(model, input_ids, target_id, param_name, eps=1e-4):
    """
    Gradient تقريبي — لمعامل واحد.
    """
    # الوصول للمعامل
    param = getattr(model, param_name)

    # حفظ القيمة الأصلية
    original = deepcopy(param)

    # حساب L+
    # ... (نبسطها — بس لمعامل واحد)

    return None  # placeholder


# ═══════════════════════════════════════════════════════════
#  التدريب المبسّط — Random Search
# ═══════════════════════════════════════════════════════════

def train_step_random(model, batch, word2id):
    """
    خطوة تدريب — Random Search.
    نجرب تعديلات عشوائية — نحتفظ بالأفضل.
    """
    # حساب Loss الحالي
    current_loss = 0
    for input_words, target_word in batch:
        input_ids = [word2id[w] for w in input_words]
        target_id = word2id[target_word]
        current_loss += compute_loss(model, input_ids, target_id)
    current_loss /= len(batch)

    # نجرب تعديلات
    best_loss = current_loss
    best_model = None

    for _ in range(5):  # 5 محاولات
        # نسخة من النموذج
        trial = deepcopy(model)

        # تعديل عشوائي — على W_out
        for i in range(len(trial.W_out)):
            for j in range(len(trial.W_out[i])):
                trial.W_out[i][j] += random.gauss(0, 0.01)

        # حساب Loss
        trial_loss = 0
        for input_words, target_word in batch:
            input_ids = [word2id[w] for w in input_words]
            target_id = word2id[target_word]
            trial_loss += compute_loss(trial, input_ids, target_id)
        trial_loss /= len(batch)

        # هل أفضل؟
        if trial_loss < best_loss:
            best_loss = trial_loss
            best_model = trial

    return best_model, best_loss


# ═══════════════════════════════════════════════════════════
#  التشغيل
# ═══════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  🧠 HBS-2 — التدريب المبسّط (Random Search)")
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

    # Batch — بسيط
    batch = []
    for line in lines[:20]:
        words = line.split()
        if len(words) >= 2:
            input_words = words[:-1]
            target_word = words[-1]
            batch.append((input_words, target_word))

    print(f"🎓 Batch: {len(batch)} عينة")
    print()

    # النموذج
    model = SimpleHabs2(vocab_size=len(vocab), d_model=16, d_ff=32)

    # Loss الابتدائي
    initial_loss = 0
    for input_words, target_word in batch[:5]:
        input_ids = [word2id[w] for w in input_words]
        target_id = word2id[target_word]
        initial_loss += compute_loss(model, input_ids, target_id)
    initial_loss /= 5

    print(f"📉 Loss الابتدائي: {initial_loss:.4f}")
    print()

    # التدريب — 5 دورات
    print("🎓 جاري التدريب (Random Search)...")
    print()

    current_model = model
    current_loss = initial_loss

    for epoch in range(5):
        best_model, best_loss = train_step_random(current_model, batch[:5], word2id)
        if best_model and best_loss < current_loss:
            current_model = best_model
            current_loss = best_loss
            print(f"  [Epoch {epoch+1}] Loss: {current_loss:.4f}  ✓ تحسين")
        else:
            print(f"  [Epoch {epoch+1}] Loss: {current_loss:.4f}")

    print()
    print(f"📉 Loss النهائي: {current_loss:.4f}")
    print(f"   التحسين: {((initial_loss - current_loss) / initial_loss * 100):.1f}%")
    print()

    print("═" * 60)
    print("  ⚠️  تعليمي فقط — احترام القرآن.")
    print("═" * 60)


if __name__ == "__main__":
    main()
