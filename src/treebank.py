#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tree
from parser import *
from sentence import Sentence, Token

from sklearn import preprocessing


class TreebankParser(object):
    def __init__(self, filename):
        """ """
        self.examples = list()
        self.labels = list()

        for i, sentence in enumerate(self.__get_sentence(filename)):
    #        print("{}. {}".format(i+1, sentence))
            dependency_tree = tree.tree(sentence).sort()
            transitions = SentenceTransitions(sentence, dependency_tree)
            data = [(Features(t).feature_vector(), label) for t, label in transitions.states]
            self.examples.extend([d[0] for d in data])
            self.labels.extend([d[1] for d in data])


            # for e in example:
            #     print("{} -> {}".format(e[0], e[1]))
            if i == 10:
                break


#            self.sentences.append(transitions)
#            print([x[1] for x in  list(self.sentences[0].states)])

        enc = preprocessing.OneHotEncoder()
        enc.fit(self.labels)

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
