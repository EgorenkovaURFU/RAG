

def normalize_results(results: list, source: str):
    if not results:
        return results

    scores = [r["score"] for r in results]
    min_s, max_s = min(scores), max(scores)

    for r in results:
        if min_s == max_s:
            r["norm_score"] = 1.0
        else:
            r["norm_score"] = (r["score"] - min_s) / (max_s - min_s)

        r["_source"] = source

    return results

