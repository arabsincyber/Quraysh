"""
HBS-8 — التدريب
=================

طريقة: Random Search على الأوزان.
- نولّد أوزان عشوائية جديدة
- نحسب loss على corpus صغير
- نحتفظ بالأفضل

بديل مبسّط لـ Backprop.
"""

import random
import math
from habs_8 import Habs8, load_corpus, build_vocab, encode, cross_entropy_loss


def compute_loss(نموذج, ids, sample_size=50):
    """يحسب متوسط loss على عيّنة"""
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


def random_search(ids, vocab_size, iterations=20):
    """يجرّب أوزان عشوائية ويحتفظ بالأفضل"""
    best_loss = float("inf")
    best_weights = None

    for it in range(iterations):
        نموذج = Habs8(
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
        else:
            print(f"  ⏳ iter {it+1}/{iterations} — loss: {loss:.4f}")

    return best_weights, best_loss


if __name__ == "__main__":
    print("🧠 HBS-8 — التدريب بـ Random Search")
    print("=" * 50)

    # حمّل
    كلمات = load_corpus("/data/data/com.termux/files/home/lugha/quraysh-v2/models/corpus/quran/quran.txt")
    print(f"📖 كلمات: {len(كلمات):,}")

    vocab = build_vocab(كلمات, max_vocab=500)
    ids = encode(كلمات[:5000], vocab)
    print(f"🔢 IDs: {len(ids):,}")

    # تدريب
    print()
    print("🏋️  بدء Random Search...")
    best_model, best_loss = random_search(ids, len(vocab), iterations=20)

    print()
    print(f"✅ أفضل loss: {best_loss:.4f}")

    # ولّد نص
    if best_model:
        seed = ids[:2]
        generated = best_model.generate(seed, length=15, temperature=0.7)
        id_to_word = {v: k for k, v in vocab.items()}
        نص = " ".join(id_to_word.get(i, "?") for i in generated)
        print(f"📝 نص مولّد: {نص}")

        # احفظ
        best_model.حفظ("habs_8_trained.json")
        print("💾 حُفظ: habs_8_trained.json")
