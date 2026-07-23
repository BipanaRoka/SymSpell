# import regex
# import pickle
# from itertools import combinations
# from collections import defaultdict

# MAX_EDIT_DISTANCE = 2

# def graphemes(word):
#     """Split a Devanagari word into human-perceived units, not raw codepoints."""
#     return regex.findall(r"\X", word)

# def delete_variants(word, max_edits=MAX_EDIT_DISTANCE):
#     """
#     Generate all strings obtainable by deleting up to `max_edits` grapheme
#     clusters from `word`. This is the 'symmetric delete' precomputation --
#     both dictionary words and future misspelled queries only ever need
#     deletes generated, never full edit-distance computed against every word.
#     """
#     gs = graphemes(word)
#     n = len(gs)
#     variants = {word}  # distance-0: the word itself
#     for edits in range(1, max_edits + 1):
#         if edits > n:
#             break
#         for combo in combinations(range(n), n - edits):
#             variant = "".join(gs[i] for i in combo)
#             if variant:
#                 variants.add(variant)
#     return variants

# # --- Load unigram dictionary ---
# unigram_freq = {}
# with open("unigram_freq.txt", encoding="utf-8") as f:
#     for line in f:
#         word, count = line.rstrip("\n").split("\t")
#         unigram_freq[word] = int(count)

# # --- Build the deletes index: delete_variant -> [dictionary words] ---
# delete_index = defaultdict(set)
# for word in unigram_freq:
#     for variant in delete_variants(word):
#         delete_index[variant].add(word)

# print(f"Dictionary size: {len(unigram_freq)} words")
# print(f"Delete-index size: {len(delete_index)} unique variant keys")

# # Show a concrete example: तरकारी (vegetable)
# example = "तरकारी"
# example_deletes = delete_variants(example)
# print(f"\nExample word: {example}")
# print(f"Its grapheme clusters: {graphemes(example)}")
# print(f"Number of delete-variants generated: {len(example_deletes)}")
# print(f"Some variants: {list(example_deletes)[:8]}")

# # Save the index and frequency table for the runtime step
# with open("symspell_index.pkl", "wb") as f:
#     pickle.dump({"delete_index": dict(delete_index), "unigram_freq": unigram_freq}, f)

# print("\nSaved symspell_index.pkl")


##above was for the single word and now we will be implementing for the sentence also.
import regex
import pickle
from itertools import combinations
from collections import defaultdict

MAX_EDIT_DISTANCE = 2

def graphemes(word):
    """Split a Devanagari word into human-perceived units, not raw codepoints."""
    return regex.findall(r"\X", word)

def delete_variants(word, max_edits=MAX_EDIT_DISTANCE):
    """
    Generate all strings obtainable by deleting up to `max_edits` grapheme
    clusters from `word`. This is the 'symmetric delete' precomputation --
    both dictionary words and future misspelled queries only ever need
    deletes generated, never full edit-distance computed against every word.
    """
    gs = graphemes(word)
    n = len(gs)
    variants = {word}  # distance-0: the word itself
    for edits in range(1, max_edits + 1):
        if edits > n:
            break
        for combo in combinations(range(n), n - edits):
            variant = "".join(gs[i] for i in combo)
            variants.add(variant)  # empty string IS a valid delete-variant
    return variants

# --- Load unigram dictionary ---
unigram_freq = {}
with open("unigram_freq.txt", encoding="utf-8") as f:
    for line in f:
        word, count = line.rstrip("\n").split("\t")
        unigram_freq[word] = int(count)

# --- Build the deletes index: delete_variant -> [dictionary words] ---
delete_index = defaultdict(set)
for word in unigram_freq:
    for variant in delete_variants(word):
        delete_index[variant].add(word)

print(f"Dictionary size: {len(unigram_freq)} words")
print(f"Delete-index size: {len(delete_index)} unique variant keys")

# Show a concrete example: तरकारी (vegetable)
example = "तरकारी"
example_deletes = delete_variants(example)
print(f"\nExample word: {example}")
print(f"Its grapheme clusters: {graphemes(example)}")
print(f"Number of delete-variants generated: {len(example_deletes)}")
print(f"Some variants: {list(example_deletes)[:8]}")

# Save the index and frequency table for the runtime step
with open("symspell_index.pkl", "wb") as f:
    pickle.dump({"delete_index": dict(delete_index), "unigram_freq": unigram_freq}, f)

print("\nSaved symspell_index.pkl")