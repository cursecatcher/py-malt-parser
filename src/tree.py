#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class node(object):
    def __init__(self, id, wordform=None, pos=None):
        self.id = int(id)
        self.word = wordform
        self.pos = pos
        self.siblings = list() #lista di coppie (node, relation)

    def add_dependency(self, node, relation):
        """Aggiunge una dipendenza tra il nodo corrente (head) e il nodo passato
        come parametro (dependent)"""
        self.siblings.append((node, relation))

    def __str__(self):
        return "({}, {}) -> {}".format(self.id, self.word, [s.id for s, rel in self.siblings])


class tree(object):
    def __init__(self, sentence=None, lines=None):
        """ Initialize a dependency tree from a treebank's tree or from a sentence"""
        self.nodes = [node(id=0)] #root dell'albero. NB: word e pos di nodes[0] non sono definiti

        if lines is not None:
            #crea albero completo a partire da albero su file
            self.nodes.extend([node(id=index+1) for index in range(len(lines))])

            for index, line in enumerate(lines, 1):
                #inizializza nodo
                curr = self.nodes[index]
                curr.word = line[1]
                curr.pos = line[2]
                #assegna dipendenza
                head = int(line[6])
                relation = self.__map_relation(line[7]) #relazione head->dependent
                self.nodes[head].add_dependency(curr, relation)

        elif sentence is not None:
            #crea nodi dell'albero, mancano le dipendenze che vengono aggiunte a runtime
            self.nodes.extend([node(id=index, wordform=token) for index, token in enumerate(sentence.split(), 1)])


    def add_dependency(self, head, dependent, relation):
        """Aggiunge all'albero la dipendenza (head, dependent)"""
        self.nodes[head].add_dependency(self.nodes[dependent], relation)

    def dependency_exists(self, head, dep, rel=None):
        """ Verifica se esiste la dipendenza (head, dep). Se rel != None,
        viene effettuata una ricerca 'tipata' sul tipo di relazione,
        altrimenti si verifica semplicemente un controllo d'esistenza"""
        res = False

        for node, relation in self.nodes[head].siblings:
            if node.id == dep:
                if rel is None or rel == relation:
                    res = relation
                break

        return res

    def get_dependencies_by_head(self, head):
        return self.nodes[head].siblings

    def __map_relation(self, relation):
        return relation if relation in ("nsubj", "dobj", "root") else "noname"

    def visit(self):
        for w in self.nodes:
            print(w)
