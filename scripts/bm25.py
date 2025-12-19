import math
from collections import defaultdict

class BM25:
    def __init__(self, index, doc_len, num_docs, k1=1.5, b=0.75):
        self.index = index
        self.doc_len = doc_len
        self.num_docs = num_docs
        self.avgdl = sum(doc_len.values()) / num_docs
        self.k1 = k1
        self.b = b

    def idf(self, term):
        df = len(self.index.get(term, {}))
        if df == 0:
            return 0
        return math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1)

    def rank(self, query_tokens):
        scores = defaultdict(float)

        for term in query_tokens:
            postings = self.index.get(term, {})
            idf = self.idf(term)

            for doc_id, tf in postings.items():
                dl = self.doc_len[doc_id]
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[doc_id] += idf * (tf * (self.k1 + 1)) / denom

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
