# import regex
# import pickle
# import sys
# from itertools import combinations

# MAX_EDIT_DISTANCE = 2

# # On Windows, the console's default codepage often isn't UTF-8, which can
# # corrupt Devanagari input/output. This forces UTF-8 on stdin/stdout if the
# # Python version supports it (3.7+). Safe to leave in even if not needed.
# for stream in (sys.stdin, sys.stdout):
#     if hasattr(stream, "reconfigure"):
#         stream.reconfigure(encoding="utf-8")


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


# def load_resources():
#     with open("symspell_index.pkl", "rb") as f:
#         data = pickle.load(f)
#     delete_index = data["delete_index"]
#     unigram_freq = data["unigram_freq"]

#     bigram_freq = {}
#     with open("bigram_freq.txt", encoding="utf-8") as f:
#         for line in f:
#             pair, count = line.rstrip("\n").split("\t")
#             w1, w2 = pair.split(" ")
#             bigram_freq[(w1, w2)] = int(count)

#     return delete_index, unigram_freq, bigram_freq


# def get_candidates(query, delete_index, unigram_freq, max_edits=MAX_EDIT_DISTANCE):
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
#     candidates.sort(key=lambda c: (c[1], -c[2], c[0]))
#     return candidates


# def correct(query, delete_index, unigram_freq, bigram_freq, previous_word=None):
#     candidates = get_candidates(query, delete_index, unigram_freq)
#     if not candidates:
#         return None, candidates
#     if not previous_word:
#         return candidates[0][0], candidates

#     def bigram_score(c):
#         word, dist, freq = c
#         bg = bigram_freq.get((previous_word, word), 0)
#         return (dist, -bg, -freq)

#     reranked = sorted(candidates, key=bigram_score)
#     return reranked[0][0], reranked


# def main():
#     delete_index, unigram_freq, bigram_freq = load_resources()
#     print(f"Loaded {len(unigram_freq)} dictionary words, {len(delete_index)} delete-index keys.")
#     print("Type a Devanagari word to check/correct. Type 'quit' to exit.\n")

#     while True:
#         query = input("Enter word: ").strip()
#         if query.lower() in ("quit", "exit"):
#             print("Goodbye.")
#             break
#         if not query:
#             continue

#         previous_word = input("Previous word for context (press Enter to skip): ").strip()
#         previous_word = previous_word if previous_word else None

#         best, candidates = correct(query, delete_index, unigram_freq, bigram_freq, previous_word)

#         print(f"\nQuery: {query}")
#         if not candidates:
#             print("No candidates found within edit distance 2.\n")
#             continue

#         print("Candidates (word, edit_distance, unigram_freq):")
#         for c in candidates:
#             print(f"  {c}")
#         print(f"Best correction: {best}\n")


# if __name__ == "__main__":
#     main()


##for whole sentence.
import regex
import pickle
import sys
from itertools import combinations

MAX_EDIT_DISTANCE = 2

# On Windows, the console's default codepage often isn't UTF-8, which can
# corrupt Devanagari input/output. This forces UTF-8 on stdin/stdout if the
# Python version supports it (3.7+). Safe to leave in even if not needed.
for stream in (sys.stdin, sys.stdout):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


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


def load_resources():
    with open("symspell_index.pkl", "rb") as f:
        data = pickle.load(f)
    delete_index = data["delete_index"]
    unigram_freq = data["unigram_freq"]

    bigram_freq = {}
    with open("bigram_freq.txt", encoding="utf-8") as f:
        for line in f:
            pair, count = line.rstrip("\n").split("\t")
            w1, w2 = pair.split(" ")
            bigram_freq[(w1, w2)] = int(count)

    return delete_index, unigram_freq, bigram_freq


def get_candidates(query, delete_index, unigram_freq, max_edits=MAX_EDIT_DISTANCE):
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
    candidates.sort(key=lambda c: (c[1], -c[2], c[0]))
    return candidates


def correct(query, delete_index, unigram_freq, bigram_freq, previous_word=None):
    candidates = get_candidates(query, delete_index, unigram_freq)
    if not candidates:
        return None, candidates
    if not previous_word:
        return candidates[0][0], candidates

    def bigram_score(c):
        word, dist, freq = c
        bg = bigram_freq.get((previous_word, word), 0)
        return (dist, -bg, -freq)

    reranked = sorted(candidates, key=bigram_score)
    return reranked[0][0], reranked


def main():
    delete_index, unigram_freq, bigram_freq = load_resources()
    print(f"Loaded {len(unigram_freq)} dictionary words, {len(delete_index)} delete-index keys.")
    print("Type a Devanagari word to check/correct. Type 'quit' to exit.\n")

    while True:
        query = input("Enter word: ").strip()
        if query.lower() in ("quit", "exit"):
            print("Goodbye.")
            break
        if not query:
            continue

        previous_word = input("Previous word for context (press Enter to skip): ").strip()
        previous_word = previous_word if previous_word else None

        best, candidates = correct(query, delete_index, unigram_freq, bigram_freq, previous_word)

        print(f"\nQuery: {query}  |  raw repr: {repr(query)}  |  codepoints: {[hex(ord(c)) for c in query]}")
        if not candidates:
            print("No candidates found within edit distance 2.\n")
            continue

        print("Candidates (word, edit_distance, unigram_freq):")
        for c in candidates:
            print(f"  {c}")
        print(f"Best correction: {best}\n")


if __name__ == "__main__":
    main()