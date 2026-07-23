import unicodedata
import json
from collections import Counter

with open("corpus.txt", encoding="utf-8") as f:
    raw_text = f.read()

normalized = unicodedata.normalize("NFC", raw_text)
PUNCT = "।,.!?\"'()"

# Keep sentence boundaries so bigrams don't cross '।' incorrectly
sentences = [s.strip() for s in normalized.replace("।", "।|").split("|") if s.strip()]

def clean_token(tok):
    return tok.strip(PUNCT)

tokenized_sentences = []
for sent in sentences:
    toks = [clean_token(w) for w in sent.split()]
    toks = [w for w in toks if w]
    tokenized_sentences.append(toks)

# --- Unigram counts ---
unigram_counts = Counter()
for toks in tokenized_sentences:
    unigram_counts.update(toks)

# --- Bigram counts ---
bigram_counts = Counter()
for toks in tokenized_sentences:
    for w1, w2 in zip(toks, toks[1:]):
        bigram_counts[(w1, w2)] += 1

print(f"Vocabulary size (unique unigrams): {len(unigram_counts)}")
print(f"Unique bigrams: {len(bigram_counts)}\n")

print("Top 10 unigrams by frequency:")
for word, count in unigram_counts.most_common(10):
    print(f"  {word:15s} {count}")

print("\nTop 10 bigrams by frequency:")
for (w1, w2), count in bigram_counts.most_common(10):
    print(f"  {w1} -> {w2:15s} {count}")

# Save as the actual dictionary files SymSpell will load
with open("unigram_freq.txt", "w", encoding="utf-8") as f:
    for word, count in unigram_counts.most_common():
        f.write(f"{word}\t{count}\n")

with open("bigram_freq.txt", "w", encoding="utf-8") as f:
    for (w1, w2), count in bigram_counts.most_common():
        f.write(f"{w1} {w2}\t{count}\n")

print("\nSaved unigram_freq.txt and bigram_freq.txt")
