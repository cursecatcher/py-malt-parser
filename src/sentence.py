#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Sentence(object): #e se ereditasse da list???
    def __init__(self):
        self.__tokens = list()

    def add_token(self, token):
        self.__tokens.append(token)

    def __str__(self):
        return " ".join(token.wordform for token in self.__tokens)

    def __iter__(self):
        for token in self.__tokens:
            yield token

    def __len__(self):
        return len(self.__tokens)

    def clear(self):
        self.__tokens.clear()




class Token(object):
    def __init__(self, id, wordform=None, lemma=None, pos=None, head=None, dep=None):
        self.__token = {"id": int(id) if id is not None else None}
        self.wordform = wordform
        self.lemma = lemma
        self.pos = pos
        self.head = head
        self.dtype = dep

    @property
    def tid(self):
        return self.__token["id"]

    @property
    def wordform(self):
        return self.__token["wordform"] if "wordform" in self.__token else None

    @property
    def lemma(self):
        return self.__token["lemma"] if "lemma" in self.__token else None

    @property
    def pos(self):
        return self.__token["pos"] if "pos" in self.__token else None

    @property
    def head(self):
        return self.__token["head"] if "head" in self.__token else None

    @property
    def dtype(self):
        return self.__token["dtype"] if "dtype" in self.__token else None

    @wordform.setter
    def wordform(self, wf):
        self.__token["wordform"] = wf

    @lemma.setter
    def lemma(self, lemma):
        self.__token["lemma"] = lemma

    @pos.setter
    def pos(self, pos):
        self.__token["pos"] = pos

    @head.setter
    def head(self, head):
        self.__token["head"] = int(head) if head else None

    @dtype.setter
    def dtype(self, dtype):
        self.__token["dtype"] = dtype if dtype in ("nsubj", "dobj", "root", None) else "noname"

    def __str__(self):
        return str(self.__token)
