"""
HBS-5 — Backprop بسيط
========================

Embedding + Output فقط.
Backprop واضح — خطوة خطوة.
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
#  HBS-5 — بسيط
# ═══════════════════════════════════════════════════════════

class Habs5:

    def __init__(self, vocab_size, d_model=32, seed=42):
        random.seed(seed)
        self.vocab_size = vocab_size
        self.d_model = d_model

        # Embedding — مصفوفة (vocab × d_model)
        scale_e = math.sqrt(2.0 / (vocab_size + d_model))
        self.embed = [
            [random.gauss(0, scale_e) for _ in range(d_model)]
            for _ in range(vocab_size)
        ]

        # Output — مصفوفة (d_model × vocab)
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

        1. Embedding
        2. Average
        3. Output
        """
        seq_len = len(token_ids)
        d = self.d_model

        # 1. Embedding
        X = [self.embed[tid][:] for tid in token_ids]

        # 2. Average
        h = [
            sum(X[i][j] for i in range(seq_len)) / seq_len
            for j in range(d)
        ]

        # 3. Output
        logits = [
            sum(h[i] * self.W_out[i][j] for i in range(d))
            for j in range(self.vocab_size)
        ]

        # Cache
        self.cache = {
            'X': X, 'h': h, 'logits': logits,
            'tokens': token_ids, 'seq_len': seq_len,
        }

        return logits

    # ═══════════════════════════════════════════════════════════
    #  Backward
    # ═══════════════════════════════════════════════════════════

    def backward(self, target_id, lr=0.1):
        """
        Backprop — بسيط.

        من Loss → Logits → h → W_out → Embed.
        """
        c = self.cache
        X = c['X']
        h = c['h']
        logits = c['logits']
        tokens = c['tokens']
        seq_len = c['seq_len']
        d = self.d_model
        V = self.vocab_size

        # ═══ 1. Loss ═══
        probs = softmax(logits)
        loss = -math.log(probs[target_id] + 1e-9)

        # ═══ 2. dL/dLogits ═══
        d_logits = probs[:]
        d_logits[target_id] -= 1.0

        # ═══ 3. dL/dW_out ═══
        # dL/dW_out[i][j] = h[i] × d_logits[j]
        d_W_out = [
            [h[i] * d_logits[j] for j in range(V)]
            for i in range(d)
        ]

        # ═══ 4. dL/dh ═══
        # dL/dh[i] = sum_j(W_out[i][j] × d_logits[j])
        d_h = [
            sum(self.W_out[i][j] * d_logits[j] for j in range(V))
            for i in range(d)
        ]

        # ═══ 5. dL/dEmbed ═══
        # dL/dX[i][j] = d_h[j] / seq_len
        # (لأن h = mean(X))
        d_X = [
            [d_h[j] / seq_len for j in range(d)]
            for _ in range(seq_len)
        ]

        # ═══ 6. Update ═══

        # 6.1: W_out
        for i in range(d):
            for j in range(V):
                self.W_out[i][j] -= lr * d_W_out[i][j]

        # 6.2: Embedding
        for i, tid in enumerate(tokens):
            for j in range(d):
                self.embed[tid][j] -= lr * d_X[i][j]

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

def train(model, batch, word2id, epochs=20, lr=0.1):
    losses = []

    for epoch in range(epochs):
        epoch_loss = 0

        for input_words, target_word in batch:
            input_ids = [word2id.get(w, 0) for w in input_words]
            target_id = word2id.get(target_word, 0)

            # Forward
            model.forward(input_ids)

            # Backward
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
    print("  🧠 HBS-5 — Backprop بسيط")
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

    # Batch — جمل قصيرة
    batch = []
    for line in lines:
        words = line.split()
        if 2 <= len(words) <= 4:
            batch.append((words[:-1], words[-1]))

    print(f"🎓 Batch: {len(batch)} عينة")
    print()

    # النموذج
    model = Habs5(vocab_size=len(vocab), d_model=32)

    # التدريب
    print("🎓 جاري التدريب...")
    print()
    losses = train(model, batch, word2id, epochs=20, lr=0.1)

    print()
    print(f"📉 الابتدائي: {losses[0]:.4f}")
    print(f"📉 النهائي:   {losses[-1]:.4f}")
    imp = (losses[0] - losses[-1]) / losses[0] * 100
    print(f"📈 التحسين:   {imp:.1f}%")

    # التوليد
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
