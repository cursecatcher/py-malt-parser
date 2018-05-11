#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enums import RelationType

class Sentence(object):
    """ Rappresenta una frase: è una sequenza ordinata di token """

    def __init__(self):
        self.__tokens = list()

    def add_token(self, token):
        self.__tokens.append(token)

    def clear(self):
        self.__tokens.clear()

    def __str__(self):
        return " ".join(token.wordform for token in self.__tokens)

    def __iter__(self):
        for token in self.__tokens:
            yield token

    def __len__(self):
        return len(self.__tokens)



class Token(object):
    """ """
    def __init__(self, id, wordform=None, lemma=None, pos=None, xpos=None, feats=None, head=None, dep=None):
        self.__id = int(id) if id is not None else None 
        self.__wordform = wordform
        self.__lemma = lemma
        self.__pos = pos
        self.__xpos = xpos
        self.__feats = feats
        self.__head = int(head) if head else None
        self.__dtype = RelationType.get_relation_type(dep) if dep else None

    def init(self, wordform=None, lemma=None, pos=None, xpos=None, feats=None, head=None, dep=None):
        self.wordform = wordform
        self.lemma = lemma
        self.pos = pos
        self.xpos = xpos
        self.feats = feats
        self.head = int(head) if head else None
        self.dtype = dep

    @property
    def tid(self):
        return self.__id

    @property
    def wordform(self):
        return self.__wordform

    @property
    def lemma(self):
        return self.__lemma

    @property
    def pos(self):
        return self.__pos

    @property
    def xpos(self):
        return self.__xpos

    @property
    def feats(self):
        return self.__feats

    @property
    def head(self):
        return self.__head

    @property
    def dtype(self):
        return self.__dtype
    @wordform.setter
    def wordform(self, wf):
        self.__wordform = wf

    @lemma.setter
    def lemma(self, lemma):
        self.__lemma = lemma

    @pos.setter
    def pos(self, pos):
        self.__pos = pos

    @xpos.setter
    def xpos(self, xpos):
        self.__xpos = xpos

    @feats.setter
    def feats(self, feats):
        self.__feats = feats

    @head.setter
    def head(self, head):
        self.__head = head

    @dtype.setter
    def dtype(self, dtype):
            self.__dtype = RelationType.get_relation_type(dtype) if dtype else None

    def __str__(self):
        return "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t_\t_".format(self.tid, self.wordform, self.lemma, self.pos, self.xpos, self.feats, self.head if self.head else 0, self.dtype.name.lower() if self.dtype else "noname")
