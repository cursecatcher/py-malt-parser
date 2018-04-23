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


    # def __init__(self, sentence=None, lines=None):
    #     """ Initialize a dependency tree from a treebank's tree or from a sentence (list of (word, pos))"""
    #     self.nodes = [token_node(id=0)] #root dell'albero. NB: word e pos di nodes[0] non sono definiti
    #     #un po' ridondante, ma permette di recuperare velocemente l'head di un nodo
    #     #contiene tuple (w_h, w_d, dependency_type)
    #     self.dependencies = list()
    #
    #     if lines is not None:
    #         #crea albero completo a partire da albero su file
    #         self.nodes.extend([token_node(id=index+1) for index in range(len(lines))])
    #
    #         for index, line in enumerate(lines, 1):
    #             #inizializza nodo
    #             curr = self.nodes[index]
    #             curr.word = line[1]
    #             curr.lemma = line[2]
    #             curr.pos = line[3]
    #             #assegna dipendenza
    #             head = int(line[6])
    #             relation = self.__map_relation(line[7]) #relazione head->dependent
    #
    #             self.add_dependency(head, index, relation)
    #
    #     elif sentence is not None:
    #         #crea nodi dell'albero, le dipendenze verranno aggiunte a runtime
    #         self.nodes.extend([token_node(index, token[0], token[1], token[2]) for index, token in enumerate(sentence, 1)])

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
        return siblings[0] if len(siblings) > 0 else sentence.Token(None)

    def get_rightmost_child(self, tid):
        siblings = self.nodes[tid].siblings if tid else list()
        return siblings[-1] if len(siblings) > 0 else sentence.Token(None)

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

##############questo funziona
        # res = False
        # #questa roba si può riscrivere meglio con self.dependencies
        # for node, relation in self.nodes[head].siblings:
        #     if node.id == dep:
        #         if rel is None or rel == relation:
        #             res = relation
        #         break
        #
        # return res
############fine parte funzionante

    def get_dependencies_by_head(self, head):
        return self.nodes[head].siblings

    def __map_relation(self, relation):
        return relation if relation in ("nsubj", "dobj", "root") else "noname"

    def __str__(self):
        return " ".join([str(node) for node in self.nodes])

    def __getitem__(self, key):
        """ Accede al key-esimo nodo. """
        return self.nodes[key] if key else None

    def __str__(self):
        return "\n".join([str(node) for node in self.nodes])

    # def visit(self):
    #     for w in self.nodes:
    #         print(w)


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
