"""
HBS-6.1 — تحسين HBS-6
========================

- نموذج أصغر
- lr أصغر
- Dropout بسيط
"""

import math
import random


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


class Habs6_1:

    def __init__(self, vocab_size, d_model=16, d_ff=16, seed=42):
        random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.d_ff = d_ff

        def rand_matrix(rows, cols):
            scale_v = math.sqrt(2.0 / (rows + cols))
            return [[random.gauss(0, scale_v) for _ in range(cols)]
                    for _ in range(rows)]

        # Embedding
        self.embed = rand_matrix(vocab_size, d_model)

        # FF
        self.W1 = rand_matrix(d_model, d_ff)
        self.b1 = [0.0] * d_ff
        self.W2 = rand_matrix(d_ff, vocab_size)
        self.b2 = [0.0] * vocab_size

        # Dropout rate
        self.dropout = 0.2

    def forward(self, token_ids, training=True):
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

        # 3. Dropout على h (التدريب فقط)
        if training:
            self.dropout_mask = [
                0.0 if random.random() < self.dropout else 1.0 / (1 - self.dropout)
                for _ in range(d)
            ]
            h = [h[i] * self.dropout_mask[i] for i in range(d)]

        # 4. FF Layer 1
        h1 = [
            sum(h[i] * self.W1[i][j] for i in range(d)) + self.b1[j]
            for j in range(d_ff)
        ]

        # 5. ReLU
        h1_relu = [relu(v) for v in h1]

        # 6. FF Layer 2
        logits = [
            sum(h1_relu[i] * self.W2[i][j] for i in range(d_ff)) + self.b2[j]
            for j in range(V)
        ]

        # Cache
        self.cache = {
            'X': X, 'h': h, 'h1': h1, 'h1_relu': h1_relu,
            'logits': logits, 'tokens': token_ids, 'seq_len': seq_len,
            'training': training,
        }

        return logits

    def backward(self, target_id, lr=0.01):
        c = self.cache
        X = c['X']
        h = c['h']
        h1 = c['h1']
        h1_relu = c['h1_relu']
        logits = c['logits']
        tokens = c['tokens']
        seq_len = c['seq_len']
        training = c['training']
        d = self.d_model
        d_ff = self.d_ff
        V = self.vocab_size

        # Loss
        probs = softmax(logits)
        loss = -math.log(probs[target_id] + 1e-9)

        # dL/dLogits
        d_logits = probs[:]
        d_logits[target_id] -= 1.0

        # dL/dW2, dL/db2
        d_W2 = [
            [h1_relu[i] * d_logits[j] for j in range(V)]
            for i in range(d_ff)
        ]
        d_b2 = d_logits[:]

        # dL/dh1_relu
        d_h1_relu = [
            sum(self.W2[i][j] * d_logits[j] for j in range(V))
            for i in range(d_ff)
        ]

        # dL/dh1 (عبر ReLU)
        d_h1 = [d_h1_relu[i] * relu_grad(h1[i]) for i in range(d_ff)]

        # dL/dW1, dL/db1
        d_W1 = [
            [h[i] * d_h1[j] for j in range(d_ff)]
            for i in range(d)
        ]
        d_b1 = d_h1[:]

        # dL/dh
        d_h = [
            sum(self.W1[i][j] * d_h1[j] for j in range(d_ff))
            for i in range(d)
        ]

        # Dropout gradient
        if training:
            d_h = [d_h[i] * self.dropout_mask[i] for i in range(d)]

        # dL/dEmbed
        d_X = [
            [d_h[j] / seq_len for j in range(d)]
            for _ in range(seq_len)
        ]

        # Update
        for i in range(d_ff):
            for j in range(V):
                self.W2[i][j] -= lr * d_W2[i][j]
        for j in range(V):
            self.b2[j] -= lr * d_b2[j]

        for i in range(d):
            for j in range(d_ff):
                self.W1[i][j] -= lr * d_W1[i][j]
        for j in range(d_ff):
            self.b1[j] -= lr * d_b1[j]

        for i, tid in enumerate(tokens):
            for j in range(d):
                self.embed[tid][j] -= lr * d_X[i][j]

        return loss

    def generate(self, start, word2id, id2word, length=5, temperature=0.8):
        tokens = [word2id.get(w, word2id["<BOS>"]) for w in start.split()]

        for _ in range(length):
            logits = self.forward(tokens, training=False)

            if temperature != 1.0:
                logits = [x / temperature for x in logits]

            probs = softmax(logits)
            chosen = max(range(len(probs)), key=lambda i: probs[i])

            if id2word[chosen] == "<EOS>":
                break
            tokens.append(chosen)

        return " ".join(id2word[t] for t in tokens if id2word[t] not in ("<BOS>", "<EOS>"))


def train(model, batch, word2id, epochs=30, lr=0.01):
    losses = []

    for epoch in range(epochs):
        # خلط
        random.shuffle(batch)
        epoch_loss = 0

        for input_words, target_word in batch:
            input_ids = [word2id.get(w, 0) for w in input_words]
            target_id = word2id.get(target_word, 0)

            model.forward(input_ids, training=True)
            loss = model.backward(target_id, lr)
            epoch_loss += loss

        avg = epoch_loss / len(batch)
        losses.append(avg)
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  [Epoch {epoch+1:2d}] Loss: {avg:.4f}")

    return losses


def main():
    print("═" * 60)
    print("  🧠 HBS-6.1 — تحسين HBS-6")
    print("═" * 60)
    print()

    lines = load_corpus("data/corpus.txt")
    print(f"📖 البيانات: {len(lines)} سطر")
    print()

    vocab, word2id, id2word = build_vocab(lines)
    print(f"📚 القاموس: {len(vocab)} كلمة")
    print()

    # Batch — جمل متنوعة
    batch = []
    for line in lines:
        words = line.split()
        if 3 <= len(words) <= 6:
            batch.append((words[:-1], words[-1]))

    print(f"🎓 Batch: {len(batch)} عينة")
    print()

    # النموذج — أصغر
    model = Habs6_1(vocab_size=len(vocab), d_model=16, d_ff=16)

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
    print("🎨 التوليد (مع تنوع):")
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
