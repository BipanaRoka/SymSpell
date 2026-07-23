import regex, pickle
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
            if variant:
                variants.add(variant)
    return variants

def grapheme_edit_distance(a, b):
    ga, gb = graphemes(a), graphemes(b)
    n, m = len(ga), len(gb)
    dp = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1): dp[i][0] = i
    for j in range(m+1): dp[0][j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if ga[i-1] == gb[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[n][m]

with open("symspell_index.pkl", "rb") as f:
    data = pickle.load(f)
delete_index = {k: set(v) for k, v in data["delete_index"].items()}
unigram_freq = dict(data["unigram_freq"])

# --- Inject two synthetic near-duplicate words with the SAME unigram frequency ---
# आलु (potato) already exists. We add a fabricated look-alike "आलई" with equal
# frequency purely to force a genuine tie -- our real 59-word corpus is too small
# to contain a natural one. In production, ties emerge naturally from bigger data.
unigram_freq["आलई"] = unigram_freq["आलु"]  # force equal frequency
for w in ["आलु", "आलई"]:
    for variant in delete_variants(w):
        delete_index.setdefault(variant, set()).add(w)

bigram_freq = {}
with open("bigram_freq.txt", encoding="utf-8") as f:
    for line in f:
        pair, count = line.rstrip("\n").split("\t")
        w1, w2 = pair.split(" ")
        bigram_freq[(w1, w2)] = int(count)

# Fabricate context signal: "किलो" (kilo) commonly precedes आलु in real Nepali,
# never आलई (which isn't even a real word) -- so context should favor आलु strongly.
bigram_freq[("किलो", "आलु")] = 12
bigram_freq[("किलो", "आलई")] = 0

def get_candidates(query, max_edits=MAX_EDIT_DISTANCE):
    query_variants = delete_variants(query, max_edits)
    matched = set()
    for v in query_variants:
        if v in delete_index:
            matched.update(delete_index[v])
    out = []
    for w in matched:
        d = grapheme_edit_distance(query, w)
        if d <= max_edits:
            out.append((w, d, unigram_freq[w]))
    # Tertiary key is plain alphabetical -- a neutral, meaning-free tie-break
    # standing in for "whatever order the data happened to load in".
    out.sort(key=lambda c: (c[1], -c[2], c[0]))
    return out

def correct(query, previous_word=None):
    cands = get_candidates(query)
    if not cands or previous_word is None:
        return (cands[0][0] if cands else None), cands
    def score(c):
        w, d, freq = c
        bg = bigram_freq.get((previous_word, w), 0)
        return (d, -bg, -freq)
    reranked = sorted(cands, key=score)
    return reranked[0][0], reranked

query = "आल"  # one grapheme short of BOTH आलु and आलई -- a genuine tie
best_no_context, cands_no_context = correct(query)
print(f"Query: {query}  (no context)")
print(f"Tied candidates (word, edit_dist, unigram_freq): {cands_no_context}")
print(f"Winner without context (first in list, essentially arbitrary): {best_no_context}\n")

best_with_context, cands_with_context = correct(query, previous_word="किलो")
print(f"Query: {query}  (previous word: किलो)")
print(f"Re-ranked candidates (word, edit_dist, unigram_freq): {cands_with_context}")
print(f"Winner with bigram context: {best_with_context}")
