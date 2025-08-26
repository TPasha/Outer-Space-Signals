import sys
import random
import math
import string
from collections import Counter

# ----------------- CONFIG -----------------
MESSAGE_LENGTH = 721
MESSAGE_OFFSET = 33600   # where the real message starts in signal.txt
ETAOIN_ORDER = list("EATOINRSHULDCMWFGYPBVKJXQZ")

# ----------------- HELPERS -----------------
def decrypt_with_table(text, table):
    """Apply substitution table to ciphertext."""
    return "".join(table.get(ch, ch) for ch in text)

def score_plain(pt):
    """Score plaintext by common bigrams/words and vowel ratio."""
    COMMON_BIGRAMS = set([
        "TH","HE","IN","ER","AN","RE","ON","AT","EN","ND","TI","ES",
        "OR","TE","OF","ED","IS","IT","AL","AR","ST","TO","NT","NG",
        "SE","HA","AS","OU","IO","LE","VE","CO","ME","DE","HI","RI","RO","IC"
    ])
    COMMON_WORDS = set(["THE","AND","OF","TO","IN","IS","IT","AS","FOR","WAS","WITH","ON","BE","AT","BY"])
    
    s = 0.0
    # bigrams
    for i in range(len(pt)-1):
        a, b = pt[i], pt[i+1]
        if a == " " or b == " ": 
            continue
        if a+b in COMMON_BIGRAMS:
            s += 1.0
    # words
    for w in pt.split():
        if w in COMMON_WORDS:
            s += 2.0
    # vowel ratio
    letters = [c for c in pt if c != " "]
    if letters:
        v = sum(c in "AEIOU" for c in letters)/len(letters)
        s += -abs(v-0.42) * 20.0
    return s

def random_neighbor(key):
    """Swap two letters in key to create a neighbor."""
    k = key.copy()
    x, y = random.sample(string.ascii_uppercase, 2)
    k[x], k[y] = k[y], k[x]
    return k

def hill_climb(ciphertext, max_iters=9000, temperature=3.0, cooling=0.00025):
    """Simulated annealing hill-climb search for best key."""
    # initial key by frequency analysis
    counts = Counter(c for c in ciphertext if 'A' <= c <= 'Z')
    cipher_order = [p[0] for p in counts.most_common()] + [c for c in string.ascii_uppercase if c not in counts]
    key = {cipher_order[i]: ETAOIN_ORDER[i % 26] for i in range(26)}

    table = {c: key.get(c, c) for c in string.ascii_uppercase}
    pt = decrypt_with_table(ciphertext, table)
    best_key, best_score = key, score_plain(pt)
    curr_key, curr_score = key, best_score
    T = temperature
    
    for _ in range(max_iters):
        cand_key = random_neighbor(curr_key)
        cand_pt = decrypt_with_table(ciphertext, {c: cand_key.get(c, c) for c in string.ascii_uppercase})
        cand_score = score_plain(cand_pt)
        delta = cand_score - curr_score
        if delta > 0 or random.random() < math.exp(delta/max(T,1e-6)):
            curr_key, curr_score = cand_key, cand_score
            if cand_score > best_score:
                best_key, best_score = cand_key, cand_score
        T = max(0.0001, T*(1.0 - cooling))
    return best_key

# ----------------- MAIN -----------------
def main():
    """Main function to run the program."""
    print("🛸 NASA Signal Decoder - Deciphering Messages from Planet Dyslexia 🛸")
    print("Analyzing 64KB of alien signals...")
    print("Searching for 721-character encrypted message...")

    if len(sys.argv) < 2:
        print("Usage: decipher solver.py signal.txt(path to signal file)")
        return
    
    path = sys.argv[1]
    with open(path, "r") as f:
        signal = f.read()

    # extract the 721-char encrypted message
    ciphertext = signal[MESSAGE_OFFSET:MESSAGE_OFFSET + MESSAGE_LENGTH]

    # run multiple restarts to get a good key
    best_score = -1e9
    best_plain = ""
    for r in range(12):
        key = hill_climb(ciphertext)
        pt = decrypt_with_table(ciphertext, {c: key.get(c, c) for c in string.ascii_uppercase})
        score = score_plain(pt)
        if score > best_score:
            best_score, best_plain = score, pt

    print("\n🔓 Deciphered Message:")
    print(best_plain)

if __name__ == "__main__":
    main()
