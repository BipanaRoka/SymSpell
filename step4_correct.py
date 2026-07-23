# import regex
# import pickle
# from itertools import combinations

# MAX_EDIT_DISTANCE = 2

# def graphemes(word):
#     return regex.findall(r"\X", word)

# def delete_variants(word, max_edits=MAX_EDIT_DISTANCE):
#     gs = graphemes(word)
#     n = len(gs)
#     variants = {word}
#     for edits in range(1, max_edits + 1):
#         if edits > n:
#             break
#         for combo in combinations(range(n), n - edits):
#             variant = "".join(gs[i] for i in combo)
#             if variant:
#                 variants.add(variant)
#     return variants

# def grapheme_edit_distance(a, b):
#     """Levenshtein distance operating on grapheme clusters, not codepoints."""
#     ga, gb = graphemes(a), graphemes(b)
#     n, m = len(ga), len(gb)
#     dp = [[0] * (m + 1) for _ in range(n + 1)]
#     for i in range(n + 1):
#         dp[i][0] = i
#     for j in range(m + 1):
#         dp[0][j] = j
#     for i in range(1, n + 1):
#         for j in range(1, m + 1):
#             cost = 0 if ga[i - 1] == gb[j - 1] else 1
#             dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
#     return dp[n][m]

# # --- Load the prebuilt index ---
# with open("symspell_index.pkl", "rb") as f:
#     data = pickle.load(f)
# delete_index = data["delete_index"]
# unigram_freq = data["unigram_freq"]

# # --- Load bigram table ---
# bigram_freq = {}
# with open("bigram_freq.txt", encoding="utf-8") as f:
#     for line in f:
#         pair, count = line.rstrip("\n").split("\t")
#         w1, w2 = pair.split(" ")
#         bigram_freq[(w1, w2)] = int(count)

# def get_candidates(query, max_edits=MAX_EDIT_DISTANCE):
#     """Generate query deletes, match against index, return candidates with true edit distance."""
#     query_variants = delete_variants(query, max_edits)
#     matched_words = set()
#     for variant in query_variants:
#         if variant in delete_index:
#             matched_words.update(delete_index[variant])
#     candidates = []
#     for word in matched_words:
#         dist = grapheme_edit_distance(query, word)
#         if dist <= max_edits:
#             candidates.append((word, dist, unigram_freq[word]))
#     # Rank: closer edit distance first, then higher frequency
#     candidates.sort(key=lambda c: (c[1], -c[2]))
#     return candidates

# def correct(query, previous_word=None, max_edits=MAX_EDIT_DISTANCE):
#     candidates = get_candidates(query, max_edits)
#     if not candidates:
#         return None, candidates

#     if previous_word is None:
#         return candidates[0][0], candidates

#     # Re-rank using bigram context: prefer candidates that commonly
#     # follow `previous_word`, breaking ties from the unigram-only ranking.
#     def bigram_score(c):
#         word, dist, freq = c
#         bg = bigram_freq.get((previous_word, word), 0)
#         return (dist, -bg, -freq)  # still respect edit distance first

#     reranked = sorted(candidates, key=bigram_score)
#     return reranked[0][0], reranked

# # ---- Demo 1: a real typo from our corpus ----
# # तरकारी (vegetable) with one grapheme dropped -> तकारी
# typo1 = "तकारी"
# best, cands = correct(typo1)
# print(f"Query: {typo1}")
# print(f"Candidates (word, edit_dist, unigram_freq): {cands}")
# print(f"Best correction: {best}\n")

# # ---- Demo 2: same typo pattern applied to मूल्य (price) -> मूय ----
# typo2 = "मूय"
# best2, cands2 = correct(typo2)
# print(f"Query: {typo2}")
# print(f"Candidates (word, edit_dist, unigram_freq): {cands2}")
# print(f"Best correction: {best2}\n")

# # ---- Demo 3: bigram re-ranking in action ----
# # छ and छन् both got dropped a matra/virama to become the same 1-grapheme-shorter string "छ" itself is already valid,
# # so let's simulate ambiguity explicitly: "छ्" is 1 edit away from both "छ" and could plausibly relate to "छन्".
# typo3 = "छ"  # exact match case -- distance 0 candidate should dominate regardless of context
# best3, cands3 = correct(typo3, previous_word="बढेको")
# print(f"Query: {typo3} (context previous word: बढेको)")
# print(f"Candidates: {cands3}")
# print(f"Best correction: {best3}")


##for the whole sentence.
import regex
import pickle
from itertools import combinations

MAX_EDIT_DISTANCE = 2

def graphemes(word):
    return regex.findall(r"\X", word)

def delete_variants(word, max_edits=MAX_EDIT_DISTANCE):
    gs = graphemes(word)
    n = len(gs)
    variants = {word}
    for edits in range(1, max_edits + 1):
        if edits > n:
            break
        for combo in combinations(range(n), n - edits):
            variant = "".join(gs[i] for i in combo)
            variants.add(variant)  # empty string IS a valid delete-variant
    return variants

def grapheme_edit_distance(a, b):
    """Levenshtein distance operating on grapheme clusters, not codepoints."""
    ga, gb = graphemes(a), graphemes(b)
    n, m = len(ga), len(gb)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ga[i - 1] == gb[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[n][m]

# --- Load the prebuilt index ---
with open("symspell_index.pkl", "rb") as f:
    data = pickle.load(f)
delete_index = data["delete_index"]
unigram_freq = data["unigram_freq"]

# --- Load bigram table ---
bigram_freq = {}
with open("bigram_freq.txt", encoding="utf-8") as f:
    for line in f:
        pair, count = line.rstrip("\n").split("\t")
        w1, w2 = pair.split(" ")
        bigram_freq[(w1, w2)] = int(count)

def get_candidates(query, max_edits=MAX_EDIT_DISTANCE):
    """Generate query deletes, match against index, return candidates with true edit distance."""
    query_variants = delete_variants(query, max_edits)
    matched_words = set()
    for variant in query_variants:
        if variant in delete_index:
            matched_words.update(delete_index[variant])
    candidates = []
    for word in matched_words:
        dist = grapheme_edit_distance(query, word)
        if dist <= max_edits:
            candidates.append((word, dist, unigram_freq[word]))
    # Rank: closer edit distance first, then higher frequency
    candidates.sort(key=lambda c: (c[1], -c[2]))
    return candidates

def correct(query, previous_word=None, max_edits=MAX_EDIT_DISTANCE):
    candidates = get_candidates(query, max_edits)
    if not candidates:
        return None, candidates

    if previous_word is None:
        return candidates[0][0], candidates

    # Re-rank using bigram context: prefer candidates that commonly
    # follow `previous_word`, breaking ties from the unigram-only ranking.
    def bigram_score(c):
        word, dist, freq = c
        bg = bigram_freq.get((previous_word, word), 0)
        return (dist, -bg, -freq)  # still respect edit distance first

    reranked = sorted(candidates, key=bigram_score)
    return reranked[0][0], reranked

# ---- Demo 1: a real typo from our corpus ----
# तरकारी (vegetable) with one grapheme dropped -> तकारी
typo1 = "तकारी"
best, cands = correct(typo1)
print(f"Query: {typo1}")
print(f"Candidates (word, edit_dist, unigram_freq): {cands}")
print(f"Best correction: {best}\n")

# ---- Demo 2: same typo pattern applied to मूल्य (price) -> मूय ----
typo2 = "मूय"
best2, cands2 = correct(typo2)
print(f"Query: {typo2}")
print(f"Candidates (word, edit_dist, unigram_freq): {cands2}")
print(f"Best correction: {best2}\n")

# ---- Demo 3: bigram re-ranking in action ----
# छ and छन् both got dropped a matra/virama to become the same 1-grapheme-shorter string "छ" itself is already valid,
# so let's simulate ambiguity explicitly: "छ्" is 1 edit away from both "छ" and could plausibly relate to "छन्".
typo3 = "छ"  # exact match case -- distance 0 candidate should dominate regardless of context
best3, cands3 = correct(typo3, previous_word="बढेको")
print(f"Query: {typo3} (context previous word: बढेको)")
print(f"Candidates: {cands3}")
print(f"Best correction: {best3}")