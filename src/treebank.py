#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sentence import Sentence, Token
import enums


class Treebank(object):
    def __init__(self):
        """ """
        self.__labelled = None
        self.__sentences = list()
        print("Init Treebank: {}".format(self))

    def parse(self, tb_file, labelled=True):
        """ Parserizza un treebank """
        self.__labelled = labelled
        self.__sentences = self.__get_sentence(tb_file)
        print("Loaded treebank from {}".format(tb_file))
        return self

    def add_sentence(self, tree):
        self.__sentences.append(tree)

    def persist(self, output_file):
        with open(output_file, "w") as of:
            for tree in self.__sentences:
                of.write("{}\n".format(tree))


    def __iter__(self):
        for sentence in self.__sentences:
            yield (sentence, tree(sentence)) if self.__labelled else sentence

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

        if self.__labelled and len(line) == 10:
            tk = Token(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7])
        elif not self.__labelled and len(line) == 6:
            tk = Token(line[0], line[1], line[2], line[3], line[4], line[5])

        return tk


class tree(object):
    def __init__(self, sentence, set_dependencies=True):
        #init nodi dell'albero: root + un nodo per token
        self.nodes = [token_node(id=index) for index in range(len(sentence) + 1)]
        self.dependencies = set()

        #valorizzo nodi
        for index, token in enumerate(sentence, 1):
            self.nodes[index].init(token.wordform, token.lemma, token.pos, token.xpos, token.feats)#, token.head, token.dtype)

            if set_dependencies:
                self.add_dependency(token.head, index, token.dtype)
                self.nodes[index].head = token.head
                self.nodes[index].dtype = token.dtype

    def __eq__(self, other):
        return set(self.dependencies) == set(other.dependencies)

    def get_sentence(self):
        """ Restituisce una lista rappresentante la frase presente nell'albero.
        Gli elementi della lista sono coppie (lemma, pos)"""

        return [(node.lemma, node.pos) for node in self.nodes]

    def add_dependency(self, head, dependent, relation):
        """Aggiunge all'albero la dipendenza (head, dependent)"""

        self.nodes[int(dependent)].head = int(head)
        self.nodes[int(dependent)].dtype = relation
        self.nodes[int(head)].add_dependency(self.nodes[dependent], relation)
        self.dependencies.add((head, dependent, relation))


    def get_leftmost_child(self, tid):
        """ """
        siblings = filter(lambda tupla: tupla[0] == tid, self.dependencies) #seleziono dipendenze con head == tid
        try:
            child = min(siblings, key=lambda tupla: tupla[1]) #nodo con indice minore
            child = self.nodes[child[1]], child[2] #nodo figlio, relazione head-dependent
        except ValueError:
            child = None
        return child

    def get_rightmost_child(self, tid):
        siblings = filter(lambda tupla: tupla[0] == tid, self.dependencies) #seleziono dipendenze con head == tid
        try:
            child = max(siblings, key=lambda tupla: tupla[1]) #nodo con indice minore
            child = self.nodes[child[1]], child[2] #nodo figlio, relazione head-dependent
        except ValueError:
            child = None
        return child

    def get_head(self, id_node):
        """Restituisce l'head e il tipo di dipendenza del nodo passato come parametro"""
        #eccetto il nodo root, tutti i nodi hanno soltanto una head
        try:
            #l'albero è ancora in costruzione, dunque è possibile che certi nodi non abbiano ancora l'head
            head, _, dt = next(filter(lambda triple: triple[1] == id_node, self.dependencies))
        except StopIteration:
            head, dt = None, None

        return self[head], dt


    def dependency_exists(self, head, dep, rel=None):
        """ Verifica se esiste la dipendenza (head, dep). Se rel != None,
        viene effettuata una ricerca 'tipata' sul tipo di relazione,
        altrimenti si verifica semplicemente un controllo d'esistenza"""

        try:
            res = next(filter(lambda triple: triple[0] == head and triple[1] == dep, self.dependencies))[-1]
            res = res if not rel or rel == res else False
        except StopIteration:
            res = False

        return res

    def get_dependencies_by_head(self, head):
        return self.nodes[head].siblings

    def __map_relation(self, relation):
        return relation if relation in ("nsubj", "dobj", "root") else "noname"

    def __getitem__(self, key):
        """ Accede al key-esimo nodo. """
        return self.nodes[key] if key else None

    def __str__(self):
        for (h, d, r) in self.dependencies:
            self.nodes[d].head = h
            self.nodes[d].dtype = r
        return "\n".join([str(node) for node in self.nodes[1:]]) + "\n"


class token_node(Token):
    def __init__(self, id, wordform=None, lemma=None, pos=None, xpos=None, feats=None):
        Token.__init__(self, id, wordform, lemma, pos, xpos, feats)
        self.siblings = list() #lista di coppie (nodo, relation_type)

    def add_dependency(self, node, relation):
        """Aggiunge una dipendenza tra il nodo corrente (head) e il nodo passato
        come parametro (dependent)"""
        self.siblings.append((node, relation))

    def has_siblings(self):
        return len(self.siblings) > 0

    def get_token(self):
        return Token(self.tid, self.wordform, self.lemma, self.pos, self.xpos, self.feats, self.head, self.dtype)

    def __repr__(self):
        return "({}, {}, {}) -> {}".format(self.tid, self.wordform, self.pos, [s.tid for s, rel in self.siblings])
