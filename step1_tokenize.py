import unicodedata
import regex  # unicode-aware regex, supports \X for grapheme clusters

with open("corpus.txt", encoding="utf-8") as f:
    raw_text = f.read()

# --- Normalize ---
# NFC ensures combining marks (matras, virama) attach consistently to their base
# consonant, so the same visual word always has the same byte sequence.
normalized = unicodedata.normalize("NFC", raw_text)

# --- Tokenize into words ---
# Nepali is space-delimited between words, so word-level split is safe.
# We strip Devanagari punctuation (danda '।', comma, etc.) from token edges.
PUNCT = "।,.!?\"'()"
def clean_token(tok):
    return tok.strip(PUNCT)

words = [clean_token(w) for w in normalized.split()]
words = [w for w in words if w]  # drop empties

print(f"Total word tokens: {len(words)}")
print(f"First 10 tokens: {words[:10]}")

# --- Grapheme-cluster split of ONE word, to show why we don't split by raw codepoint ---
sample = words[0]  # e.g. काठमाडौंको
codepoints = list(sample)
graphemes = regex.findall(r"\X", sample)  # \X = one grapheme cluster

print(f"\nSample word: {sample}")
print(f"Raw codepoints ({len(codepoints)}): {codepoints}")
print(f"Grapheme clusters ({len(graphemes)}): {graphemes}")
