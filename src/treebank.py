#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sentence import Sentence, Token

from timeit import default_timer as timer


class TreebankParser(object):
    def __init__(self, tb_file):
        """ """
        self.__sentences = self.__get_sentence(tb_file) #è un generatore :D
        print("Init tbparser: {}".format(self.__sentences))

    def __iter__(self):
        for sentence in self.__sentences:
            yield sentence, tree(sentence)

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



class tree(object):
    def __init__(self, sentence, set_dependencies=True):
        #init nodi dell'albero: root + un nodo per token
        self.nodes = [token_node(id=index) for index in range(len(sentence) + 1)]
        self.dependencies = set()#list()
        #valorizzo nodi
        for index, token in enumerate(sentence, 1):
            curr = self.nodes[index] #questo è il motivo per cui faccio 2 loop piuttosto che uno :c
            #token_node
            curr.wordform = token.wordform
            curr.lemma = token.lemma
            curr.pos = token.pos
            #prev
            # head = token.head
            # relation_type = token.dtype
            head = curr.head = token.head
            relation_type = curr.relation_type = token.dtype

            if set_dependencies:
                self.add_dependency(head, index, relation_type)

    def __eq__(self, other):
        return set(self.dependencies) == set(other.dependencies)

    def get_sentence(self):
        """ Restituisce una lista rappresentante la frase presente nell'albero.
        Gli elementi della lista sono coppie (lemma, pos)"""

        return [(node.lemma, node.pos) for node in self.nodes]

    def add_dependency(self, head, dependent, relation):
        """Aggiunge all'albero la dipendenza (head, dependent)"""
        self.nodes[head].add_dependency(self.nodes[dependent], relation)
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
        """Restituisce l'head e il tipo di dipendenza del nodo dimmerda passato come parametro"""
        #eccetto il nodo root, tutti i nodi hanno soltanto una head
        try:
            #l'albero è ancora in costruzione, dunque è possibile che certi nodi non abbiano ancora l'head
#            print("looking for {} --> {}".format(id_node, self.dependencies))
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
        return "\n".join([str(node) for node in self.nodes])


class token_node(Token):
    def __init__(self, id, wordform=None, lemma=None, pos=None):
        Token.__init__(self, id, wordform, lemma, pos)
        #lista di nodi che hanno self come head (credo)
        self.siblings = list() #lista di coppie (nodo, relation_type)
        # self.id = int(id)
        # self.word = wordform
        # self.lemma = lemma
        # self.pos = pos
        # self.siblings = list() #lista di coppie (node, relation)

    def add_dependency(self, node, relation):
        """Aggiunge una dipendenza tra il nodo corrente (head) e il nodo passato
        come parametro (dependent)"""
        self.siblings.append((node, relation))

    def has_siblings(self):
        return len(self.siblings) > 0

    def get_token(self):
        return Token(self.tid, self.wordform, self.lemma, self.pos, self.head, self,dtype)

    def __str__(self):
        return "({}, {}, {}) -> {}".format(self.tid, self.wordform, self.pos, [s.tid for s, rel in self.siblings])

    def __repr__(self):
        return "({}, {}, {}) -> {}".format(self.tid, self.wordform, self.pos, [s.tid for s, rel in self.siblings])
