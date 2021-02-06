from kgtools.annotation import Lazy
from .common import lemmatize


class Synset:
    def __init__(self, terms):
        self.terms = terms
        self.text = "<%s>" % ", ".join(
            [term for term in list(sorted(self.terms, key=lambda x: x))])
        self.term2count = {}

    @Lazy
    def key(self):
        count2terms = {}
        for term in self.terms:
            count = self.term2count.get(term, 0)
            if count not in count2terms:
                count2terms[count] = set()
            count2terms[count].add(term)

        _, candidates = max(count2terms.items(), key=lambda item: item[0])
        canidate_name = max(candidates, key=lambda x: len(x))
        lemma = lemmatize(canidate_name).lower()
        return lemma

    def init_count(self, term_count):
        for term in self.terms:
            self.term2count[term] = term_count.get(term, 0)

    def __iadd__(self, other):
        self.terms |= other.terms
        self.term2count.update(other.term2count)
        return self

    def __add__(self, other):
        synset = Synset(self.terms | other.terms)
        synset.term2count = dict(
            set(self.term2count.items()) | set(other.term2count.items()))
        return synset

    def __str__(self):
        return self.text

    def __hash__(self):
        return hash(str(self))

    def __iter__(self):
        return iter(self.terms)

    def __eq__(self, other):
        return hash(self) == hash(other)
