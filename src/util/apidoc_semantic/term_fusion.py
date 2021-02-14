#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import re

import textdistance
from kgtools.annotation import TimeLog, Cache
from nltk.corpus import wordnet
from tqdm import tqdm

from .common import lemmatize
from .synset import Synset
from ..utils import single_line_print


class Fusion:
    def __init__(self):
        self.DL = textdistance.DamerauLevenshtein()

    @Cache
    def get_synonyms_from_wordnet(self, word):
        """
        全部同义词集合
        :param word:
        :return:
        """
        # todo: has problem. need to fixed
        synonyms = []
        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                synonyms.append(l.name())
        print("word=", word, "syms=", synonyms)
        return set(synonyms)

    def get_simple_type_for_term(self, term):

        seperate_words = [" of ", " Of "]

        # A of B type
        for s_w in seperate_words:
            if s_w in term:
                words = term.split(s_w)
                if len(words) != 2:
                    return term
                child = words[0]
                parent = words[1]
                return (parent + " " + child).replace("  ", " ")

        seperate_words = ["'s ", "' "]

        # A's B => A B
        for s_w in seperate_words:
            if s_w in term:
                words = term.split(s_w)
                if len(words) != 2:
                    return term
                parent = words[0]
                child = words[1]

                return (parent + " " + child).replace("  ", " ")

        seperate_words = ["[][]", "[] []", "[ ] [ ]"]

        for s_w in seperate_words:
            if s_w in term:
                words = term.split(s_w)
                if len(words) != 2:
                    return term
                parent = words[0]
                child = words[1]

                return ("array of " + parent + " array " + child).replace("  ", " ").strip()

        seperate_words = ["[]", "[ ]"]

        for s_w in seperate_words:
            if s_w in term:
                words = term.split(s_w)
                if len(words) != 2:
                    return term
                parent = words[0]
                child = words[1]

                return ("array of " + parent + " " + child).replace("  ", " ").strip()

        return term

    @Cache
    def clean_name_for_synonym(self, term):
        term = lemmatize(term).lower()
        term = re.sub(r'[-/_]', "", term)

        term = re.sub(r"\s+", " ", term)
        term = self.get_simple_type_for_term(term)
        return term

    def check_synonym(self, long_term, short_term, max_dis=2, threshold=1 / 5):

        long_name = self.clean_name_for_synonym(long_term)
        short_name = self.clean_name_for_synonym(short_term)

        if long_name == short_name:
            return True
        if long_name.replace(" ", "") == short_name.replace(" ", ""):
            return True
        if long_term.lower().rstrip("s") == short_term.lower().rstrip("s"):
            return True

        if long_term.isupper() and short_term.isupper():
            return False

        long_words, short_words = long_name.split(), short_name.split()

        if len(long_words) != len(short_words):
            return False
        for word1, word2 in zip(long_words, short_words):
            if word1[0] != word2[0]:
                return False
            if re.findall(r'[0-9]+', word1) != re.findall(r'[0-9]+', word2):
                return False
            if self.compute_DL_distance(word1, word2) > max_dis or self.compute_DL_distance_normalize(word1,
                                                                                                      word2) >= threshold:
                return False
        return True

    @Cache
    def compute_DL_distance_normalize(self, word1, word2):
        return self.DL.normalized_distance(word1, word2)

    @Cache
    def compute_DL_distance(self, word1, word2):
        return self.DL.distance(word1, word2)

    def check_abbr(self, long_term, short_term, stopwords=None):
        def __check_prefix(long_name, short_name):
            if len(short_name) >= 2 and len(short_name) / len(long_name) < 2 / 3 and long_name.startswith(short_name):
                return True
            return False

        def __check_phrase_word(phrase, word, stopwords):
            long_words = phrase.split()
            if len(word) < len(long_words):
                return False
            if len(long_words) == 1:
                return __check_word_word(phrase, word, stopwords)
            else:
                all_pairs = itertools.combinations(
                    [i for i in range(1, len(word), 1)], len(long_words) - 1)
                queue = []
                for pair in all_pairs:

                    temp = []
                    pair = (0,) + pair + (len(word),)
                    # print(pair)
                    long_word = long_words[0]
                    segment = word[pair[0]:pair[1]]
                    if long_word[0] == segment[0] or (
                            len(long_word) > 1 and long_word[0] in set("aeiou") and segment[0] == long_word[1]):
                        temp.append((long_word, segment))
                    else:
                        continue
                    for i in range(1, len(pair) - 1):
                        long_word = long_words[i]
                        segment = word[pair[i]:pair[i + 1]]
                        if long_word[0] == segment[0]:
                            temp.append((long_word, segment))
                        else:
                            break
                    else:
                        queue.append(temp)
                # print(queue)
                for pairs in queue:
                    for long_word, segment in pairs:
                        # print(segment)
                        if not __check_word_word(long_word, segment, stopwords):
                            return False
                        if len(segment) > 1 and segment != "re":
                            return False
                    else:
                        return True
                return False

        def __check_word_word(long_word, word, stopwords):
            if (len(word) == 1 and (word[0] == long_word[0])) or __check_prefix(long_word, word):
                return True
            return False

        def __in(short_name, long_name):
            beg = 0
            length = len(long_name)
            for ch in short_name:
                index = long_name.find(ch, beg)
                if index == -1:
                    return False
                beg = index + 1
                if beg >= length:
                    return False
            return True

        long_name = lemmatize(long_term).lower()
        short_name = lemmatize(short_term).lower()
        long_name, short_name = re.sub(
            r'[-/]', "", long_name), re.sub(r'[-/]', "", short_name)
        long_name, short_name = re.sub(
            r"\s+", " ", long_name), re.sub(r"\s+", " ", short_name)

        if not __in(short_name, long_name):
            return False

        # print(long_name, short_name)

        if len(short_name.split()) == 1:
            return __check_phrase_word(long_name, short_name, stopwords)
        else:
            short_words = short_name.split()
            long_words = long_name.split()
            if len(long_words) < len(short_words):
                return False
            while len(short_words) > 0 and short_words[0] == long_words[0]:
                short_words.pop(0)
                long_words.pop(0)
            while len(short_words) > 0 and short_words[-1] == long_words[-1]:
                short_words.pop(-1)
                long_words.pop(-1)
            if len(short_words) == 1:
                # print(long_words, short_words)
                return __check_phrase_word(" ".join(long_words), short_words[0], stopwords)
            else:
                return False

    def handle_pairs(self, terms, stopwords):
        inner_synonyms = set()
        inner_abbreviations = set()
        total = int(len(terms) * (len(terms) - 1) / 2)
        count = 0
        for i in range(len(terms) - 1):
            for j in range(i + 1, len(terms)):
                # for t1, t2 in pair_list:
                # print("%s, %s" % (t1.text, t2.text))
                t1 = terms[i]
                t2 = terms[j]
                if len(t1) == 1 or len(t2) == 1:
                    continue
                short_term, long_term = (t1, t2) if len(
                    t1) <= len(t2) else (t2, t1)
                if self.check_synonym(long_term, short_term):
                    inner_synonyms.add((long_term, short_term))
                elif self.check_abbr(long_term, short_term, stopwords):
                    inner_abbreviations.add((short_term, long_term))
                count += 1
                single_line_print(
                    f"detecting syn and abbr relations: {count} of {total}")
        return inner_synonyms, inner_abbreviations

    def detect_relations(self, terms, stopwords):
        #pairs = [(t1, t2) for t1, t2 in itertools.combinations(terms, 2)]
        return self.handle_pairs(list(terms), stopwords)

    def merge_synonyms(self, synonyms_relations):
        queue = [set(r) for r in synonyms_relations]

        # print(queue)
        # print("Merge synonyms")

        def __merge(queue):
            synonyms = []
            done = True
            while len(queue) > 0:
                now = queue.pop(0)
                # print("now:", now)
                merged = []
                for r in queue:
                    if len(r & now) > 0:
                        now |= r
                        merged.append(r)
                        done = False
                for r in merged:
                    queue.remove(r)
                synonyms.append(now)
            if done:
                return synonyms
            else:
                return __merge(synonyms)

        synonyms = set([Synset(synonym) for synonym in __merge(queue)])
        return synonyms

    def merge_abbrs(self, abbr_relations, synonyms, threshold=0.5):
        term2synset = {}
        for synset in synonyms:
            for term in synset.terms:
                term2synset[term] = synset

        abbr2fullname = {}
        for start, end in abbr_relations:
            if start not in term2synset:
                term2synset[start] = Synset(set([start]))
            if end not in term2synset:
                term2synset[end] = Synset(set([end]))
            start_synset = term2synset[start]
            end_synset = term2synset[end]
            if start_synset not in abbr2fullname:
                abbr2fullname[start_synset] = set()
            abbr2fullname[start_synset].add(end_synset)

        abbrs = set()
        for abbr, fullnames in abbr2fullname.items():
            for fn in fullnames:
                fn += abbr
        synsets = set(term2synset.values())
        return synsets

    def handle_pair_for_synonym(self, t1, t2):
        inner_synonyms = set()

        # print("%s, %s" % (t1.text, t2.text))
        if len(t1) == 1 or len(t2) == 1:
            return inner_synonyms
        short_term, long_term = (t1, t2) if len(t1) <= len(t2) else (t2, t1)
        if self.check_synonym(long_term, short_term):
            inner_synonyms.add((long_term, short_term))
        #     wordnet 可以融合
        # if self.get_synonyms_from_wordnet(short_term) & self.get_synonyms_from_wordnet(long_term):
        #     inner_synonyms.add((long_term, short_term))
        return inner_synonyms

    def handle_pairs_for_synonym(self, pair_list, stopwords):
        inner_synonyms = set()
        for t1, t2 in pair_list:
            inner_synonyms = inner_synonyms | self.handle_pair_for_synonym(
                t1, t2)
        return inner_synonyms

    def handle_term_to_list_for_synonym(self, start_term, end_term_list):
        inner_synonyms = set()
        for end_term in end_term_list:
            inner_synonyms = inner_synonyms | self.handle_pair_for_synonym(
                start_term, end_term)
        return inner_synonyms

    def detect_synonym_relations(self, terms, stopwords):
        result = set()
        terms = list(terms)
        print("loop start")
        for start_term_index, start_t in tqdm(enumerate(terms)):
            end_term_list = terms[(start_term_index + 1):]
            result = result | self.handle_term_to_list_for_synonym(
                start_t, end_term_list)
            # single_line_print(f"{start_term_index} of {len(terms)}")

        for t in terms:
            lemma = lemmatize(t).lower()
            if lemma != t:
                result.add((t, lemma))
        return result

    @TimeLog
    def fuse_by_synonym(self, terms, term_count=None, stopwords=None):
        if type(terms) != set:
            terms = set(terms)
        print("start detecting syn relations")
        synonym_relations = self.detect_synonym_relations(terms, stopwords)
        print("end detecting syn relations")
        # print("syn: ", [(t1.text, t2.text) for t1, t2 in synonym_relations])
        # print("abbr:", [(t1.text, t2.text) for t1, t2 in abbr_relations])
        print("start merging syn relations")
        synsets = self.merge_synonyms(synonym_relations)
        print("final processing")
        visited = set()
        for synset in synsets:
            visited.update(synset.terms)
        for term in terms - visited:
            synsets.add(Synset({term}))

        if term_count is not None:
            for synset in synsets:
                synset.init_count(term_count)
        print("processed! return synsets now.")
        return synsets

    @TimeLog
    def fuse(self, terms, term_count=None, stopwords=None):
        print("start detecting syn and abbr relations")
        synonym_relations, abbr_relations = self.detect_relations(
            terms, stopwords)
        print("end detecting syn and abbr relations")
        # print("syn: ", [(t1.text, t2.text) for t1, t2 in synonym_relations])
        # print("abbr:", [(t1.text, t2.text) for t1, t2 in abbr_relations])
        print("start merging syn and abbr relations")
        synonyms = self.merge_synonyms(synonym_relations)
        synsets = self.merge_abbrs(abbr_relations, synonyms)
        print("end merging syn and abbr relations")
        print("final processing")
        visited = set()
        for synset in synsets:
            visited.update(synset.terms)
        for term in terms - visited:
            synsets.add(Synset({term}))

        if term_count is not None:
            for synset in synsets:
                synset.init_count(term_count)
        print("processed! return synsets now.")
        return synsets
