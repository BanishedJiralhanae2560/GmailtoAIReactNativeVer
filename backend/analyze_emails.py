import re
import math
from difflib import SequenceMatcher
from collections import Counter

def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def cosine_similarity(a, b):
    """Compute cosine similarity between two text inputs"""
    a_words = Counter(tokenize(a))
    b_words = Counter(tokenize(b))

    intersection = set(a_words.keys()) & set(b_words.keys())
    numerator = sum(a_words[x] * b_words[x] for x in intersection)

    sum1 = sum(v ** 2 for v in a_words.values())
    sum2 = sum(v ** 2 for v in b_words.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

def search_emails(query, emails):
    query = query.lower()
    keywords = tokenize(query)
    results = []

    for email in emails:
        text = f"{email.get('subject', '')} {email.get('from', '')} {email.get('snippet', '')}".lower()

        cos_sim = cosine_similarity(query, text)
        fuzz = SequenceMatcher(None, query, text).ratio()

        # Weighted blend (you can adjust 0.75/0.25 if needed)
        combined_score = (cos_sim * 0.75) + (fuzz * 0.25)

        if combined_score > 0.25 or any(word in text for word in keywords):
            results.append((combined_score, email))

    # Sort by similarity
    results = sorted(results, key=lambda x: x[0], reverse=True)

    # Filter out weak matches
    strong_results = [r for r in results if r[0] > 0.35]

    # If no strong matches, fall back to top 1–2 weak ones
    final_results = strong_results[:3] if strong_results else results[:2]
    
    return [r[1] for r in final_results]
