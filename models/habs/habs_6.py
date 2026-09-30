"""
HBS-6 — Embedding + FF + Output
==================================

Backprop أعمق — طبقة مخفية.
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
#  HBS-6
# ═══════════════════════════════════════════════════════════

class Habs6:

    def __init__(self, vocab_size, d_model=32, d_ff=64, seed=42):
        random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.d_ff = d_ff

        def rand_matrix(rows, cols, scale=1.0):
            scale_v = math.sqrt(2.0 / (rows + cols)) * scale
            return [[random.gauss(0, scale_v) for _ in range(cols)]
                    for _ in range(rows)]

        # Embedding
        self.embed = rand_matrix(vocab_size, d_model)

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

        # 2. Average
        h = [
            sum(X[i][j] for i in range(seq_len)) / seq_len
            for j in range(d)
        ]

        # 3. FF Layer 1
        h1 = [
            sum(h[i] * self.W1[i][j] for i in range(d)) + self.b1[j]
            for j in range(d_ff)
        ]

        # 4. ReLU
        h1_relu = [relu(v) for v in h1]

        # 5. FF Layer 2 (Output)
        logits = [
            sum(h1_relu[i] * self.W2[i][j] for i in range(d_ff)) + self.b2[j]
            for j in range(V)
        ]

        # Cache
        self.cache = {
            'X': X, 'h': h, 'h1': h1, 'h1_relu': h1_relu,
            'logits': logits, 'tokens': token_ids, 'seq_len': seq_len,
        }

        return logits

    # ═══════════════════════════════════════════════════════════
    #  Backward
    # ═══════════════════════════════════════════════════════════

    def backward(self, target_id, lr=0.1):
        c = self.cache
        X = c['X']
        h = c['h']
        h1 = c['h1']
        h1_relu = c['h1_relu']
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

        # ═══ 3. dL/dW2, dL/db2 ═══
        d_W2 = [
            [h1_relu[i] * d_logits[j] for j in range(V)]
            for i in range(d_ff)
        ]
        d_b2 = d_logits[:]

        # ═══ 4. dL/dh1_relu ═══
        d_h1_relu = [
            sum(self.W2[i][j] * d_logits[j] for j in range(V))
            for i in range(d_ff)
        ]

        # ═══ 5. dL/dh1 (عبر ReLU) ═══
        d_h1 = [d_h1_relu[i] * relu_grad(h1[i]) for i in range(d_ff)]

        # ═══ 6. dL/dW1, dL/db1 ═══
        d_W1 = [
            [h[i] * d_h1[j] for j in range(d_ff)]
            for i in range(d)
        ]
        d_b1 = d_h1[:]

        # ═══ 7. dL/dh ═══
        d_h = [
            sum(self.W1[i][j] * d_h1[j] for j in range(d_ff))
            for i in range(d)
        ]

        # ═══ 8. dL/dEmbed ═══
        d_X = [
            [d_h[j] / seq_len for j in range(d)]
            for _ in range(seq_len)
        ]

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

        # Embedding
        for i, tid in enumerate(tokens):
            for j in range(d):
                self.embed[tid][j] -= lr * d_X[i][j]

        return loss

    # ═══════════════════════════════════════════════════════════
    #  التوليد
    # ═══════════════════════════════════════════════════════════

    def generate(self, start, word2id, id2word, length=5, temperature=1.0):
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

def train(model, batch, word2id, epochs=20, lr=0.1):
    losses = []

    for epoch in range(epochs):
        epoch_loss = 0

        for input_words, target_word in batch:
            input_ids = [word2id.get(w, 0) for w in input_words]
            target_id = word2id.get(target_word, 0)

            model.forward(input_ids)
            loss = model.backward(target_id, lr)
            epoch_loss += loss

        avg = epoch_loss / len(batch)
        losses.append(avg)
        print(f"  [Epoch {epoch+1:2d}] Loss: {avg:.4f}")

    return losses


# ═══════════════════════════════════════════════════════════
#  التشغيل
# ═══════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  🧠 HBS-6 — Embedding + FF + Output")
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
        if 2 <= len(words) <= 4:
            batch.append((words[:-1], words[-1]))

    print(f"🎓 Batch: {len(batch)} عينة")
    print()

    model = Habs6(vocab_size=len(vocab), d_model=32, d_ff=64)

    print("🎓 جاري التدريب...")
    print()
    losses = train(model, batch, word2id, epochs=20, lr=0.1)

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

    for s in ["قل", "هو", "إنا", "يوم"]:
        result = model.generate(s, word2id, id2word, length=5)
        print(f"   [{s}] → {result}")

    print()
    print("═" * 60)
    print("  ⚠️  تعليمي فقط — احترام القرآن.")
    print("═" * 60)


if __name__ == "__main__":
    main()
