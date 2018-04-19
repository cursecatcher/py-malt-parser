#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tree

class Parser(object):
    def __init__(self, sentence):
        self.__stack = [(0, None)] #root
        self.__queue = [id_and_word for id_and_word in enumerate(sentence.split(), 1)] #lista di tuple (id, word)
        self.__tree = tree.tree(sentence=sentence) #numero di nodi pari al numero di parole
        self.__dependencies = dict() #inutile
        self.__history = list()

    def get_tree(self):
        return self.__tree

    def print_deps(self):
        self.__tree.visit()

    def shift(self):
        """ Estrae prossima parola dalla lista e la pusha sullo stack """
        self.__stack.append(self.__queue[0])
        self.__queue = self.__queue[1:]

        self.__history.append("shift")

    def left(self, opt):
        """ Crea dipendenza tra la prossima parola nella lista e quella
        in cima allo stack, rimuovendola dalla pila."""
        dependent = self.__stack.pop()
        head = self.__queue[0]
        self.__tree.add_dependency(head[0], dependent[0], opt) #uso gli id
        self.__history.append("left_{}".format(opt))

    def right(self, opt):
        """ Crea dipendenza tra la parola in cima allo stack e la prossima nella lista.
        Rimuove la parola dalla lista, poppa lo stack e inserisce tale parola nella lista,
        in prima posizione """
        dependent, self.__queue = self.__queue[0], self.__queue[1:]
        head = self.__stack.pop()
        self.__queue.insert(0, head)

        self.__tree.add_dependency(head[0], dependent[0], opt) #uso gli id
        self.__history.append("right_{}".format(opt))


    def get_dependencies_by_head(self, head):
        return self.__tree.get_dependencies_by_head(head)

    #<partially_useless_methods>  (o forse no...)
    def next_stack(self):
        return self.__stack[-1]

    def next_queue(self):
        return self.__queue[0]

    def stack_size(self):
        return len(self.__stack)

    def queue_size(self):
        return len(self.__queue)
    #</partially_useless_methods>

    def history(self):
        return self.__history

    def is_final_state(self):
        """Condizione di terminazione del parsing: lo stack contiene solo la
        radice e la coda è vuota, in quanto tutte le parole sono state analizzate"""
        return len(self.__queue) == 0 and self.__stack == [(0, None)]
