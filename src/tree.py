#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sentence

class tree(object):
    def __init__(self, sentence, set_dependencies=True):
        #init nodi dell'albero: root + un nodo per token
        self.nodes = [token_node(id=index) for index in range(len(sentence) + 1)]
        self.dependencies = list()
        #valorizzo nodi
        for index, token in enumerate(sentence, 1):
            curr = self.nodes[index]
            curr.wordform = token.wordform
            curr.lemma = token.lemma
            curr.pos = token.pos
            head = token.head
            relation_type = token.dtype

            if set_dependencies:
                self.add_dependency(head, index, relation_type)

    def sort(self):
        """ Ordina le dipendenze in maniera crescente in base all'id del nodo.
        Il nodo con indice minore il leftmost child, quello con indice maggiore è il
        rightmost child"""

        for node in self.nodes:
            node.siblings.sort(key=lambda x: x[0].tid if x[0] is not None else -1)
        return self

    def get_sentence(self):
        """ Restituisce una lista rappresentante la frase presente nell'albero.
        Gli elementi della lista sono coppie (lemma, pos)"""

        return [(node.lemma, node.pos) for node in self.nodes]

    def add_dependency(self, head, dependent, relation):
        """Aggiunge all'albero la dipendenza (head, dependent)"""
        self.nodes[head].add_dependency(self.nodes[dependent], relation)
        self.dependencies.append((head, dependent, relation))

    def get_leftmost_child(self, tid):
        siblings = self.nodes[tid].siblings if tid else list()
        return siblings[0] if len(siblings) > 0 else None

    def get_rightmost_child(self, tid):
        siblings = self.nodes[tid].siblings if tid else list()
        return siblings[-1] if len(siblings) > 0 else None

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


    # def __str__(self):
    #     return " ".join([str(node) for node in self.nodes])

    def __getitem__(self, key):
        """ Accede al key-esimo nodo. """
        return self.nodes[key] if key else None

    def __str__(self):
        return "\n".join([str(node) for node in self.nodes])



#class token_node(object):
class token_node(sentence.Token):
    def __init__(self, id, wordform=None, lemma=None, pos=None):
        sentence.Token.__init__(self, id, wordform, lemma, pos)
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

    def get_token(self):
        return sentence.Token(self.tid, self.wordform, self.lemma, self.pos, self.head, self,dtype)

    def __str__(self):
        return "({}, {}, {}) -> {}".format(self.tid, self.wordform, self.pos, [s.tid for s, rel in self.siblings])

    def __repr__(self):
        return "({}, {}, {}) -> {}".format(self.tid, self.wordform, self.pos, [s.tid for s, rel in self.siblings])
