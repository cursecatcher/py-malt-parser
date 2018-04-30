#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tree
from parser import *
from sentence import Sentence, Token
from features import FeatureEncoder

from timeit import default_timer as timer

def format_time(time):
    strtime = "{:03.5f} m".format(time/60) if time >= 60 else "{:03.5f} s".format(time)
    return strtime

#codificare feature stringhe in interi
#codificare interi in vettori binari (con sklearn)
#addestrare classificatore


class TreebankParser(object):
    def __init__(self):
        """ """
        self.__encoder = FeatureEncoder()
#
#         print("Extracting features...", flush=True, end="")
#         start = timer()
#
#         for sentence in self.__get_sentence(filename):
#             dependency_tree = tree.tree(sentence).sort()
#             transitions = SentenceTransitions(sentence, dependency_tree)
#
#             for t, label in transitions.states:
#                 self.examples.append(encoder.encode(t))
#                 self.labels.append(encoder.encodeLabel(label))
#
#         print(" completed in {}".format(format_time(timer()-start)))
#
#         print("Training classifier...", end="", flush=True)
#         start = timer()
#
# #        logi = LogisticRegression(multi_class="ovr", solver="newton-cg", max_iter=1000).fit(self.examples, self.labels)
#         clf = SVC(kernel="poly", degree=2).fit(self.examples, self.labels)
#
#         print(" completed in {}".format(format_time(timer()-start)))


    def parse(self, filename):
        examples = list()
        labels = list()

        print("Extracting features...", flush=True, end="")
        start = timer()

        for sentence in self.__get_sentence(filename):
            dependency_tree = tree.tree(sentence).sort()
            transitions = SentenceTransitions(sentence, dependency_tree)

            for t, label in transitions.states:
                examples.append(t)
                labels.append(label)
        #
        #     for t, label in transitions.states:
        #         examples.append(self.__encoder.encode(t))
        #         labels.append(self.__encoder.encodeLabel(label))
        #
        # X = self.__encoder.oneHotEncoding(examples)
        print(" completed in {}".format(format_time(timer()-start)))
        return examples, labels

        # return X, labels



    def __get_sentence(self, filename):
        """Legge una frase dal treebank e la restituisce sottoforma di lista di liste;
        vi è una sottolista per ciascun token della frase, e riporta informazioni quali lemma, part of speech etc"""
        sentence = Sentence()

        with open(filename) as f:
            for line in f:
                token = self.__parse_line(line)
                if token:
                    sentence.add_token(token)
                else:
                    yield sentence
                    sentence.clear()

    def __parse_line(self, line):
        line, tk = line.split(), False

        if len(line) == 10:
            tk = Token(line[0], line[1], line[2], line[3], line[6], line[7])

        return tk
