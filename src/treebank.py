#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tree
from parser import *
from sentence import Sentence, Token


class TreebankParser(object):
    def __init__(self, filename):
        """ """
        self.sentences = list() 

        for i, sentence in enumerate(self.get_sentence(filename)):
            print("{}. {}".format(i+1, sentence))
            dependency_tree = tree.tree(sentence)
            transitions = SentenceTransitions(sentence, dependency_tree)

            self.sentences.append(transitions)


    def get_sentence(self, filename):
        """Legge una frase dal treebank e la restituisce sottoforma di lista di liste;
        vi è una sottolista per ciascun token della frase, e riporta informazioni quali lemma, part of speech etc"""
        sentence = Sentence()

        with open(filename) as f:
            for line in f:
                token = self.parse_line(line)
                if token:
                    sentence.add_token(token)
                else:
                    yield sentence
                    sentence.clear()

    def parse_line(self, line):
        line, tk = line.split(), False

        if len(line) == 10:
            tk = Token(line[0], line[1], line[2], line[3], line[6], line[7])

        return tk
