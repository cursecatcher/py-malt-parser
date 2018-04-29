#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tree
from sentence import Sentence, Token
from features import Features


class Parser(object):
    def __init__(self, sentence):
        self.__stack = [Token(0)] #root
        self.__queue = [token for token in sentence]
        self.__tree = tree.tree(sentence, False) #numero di nodi pari al numero di parole
        self.__history = list()

    def __str__(self):
        return "-> stack: {}\nqueue: {}".format(
        [token.tid for token in self.__stack], [token.tid for token in self.__queue])


    def get_tree(self):
        return self.__tree

    def get_stack(self):
        return list(self.__stack)

    def get_queue(self):
        return list(self.__queue)

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
        self.__tree.add_dependency(head.tid, dependent.tid, opt) #uso gli id
        self.__history.append("left_{}".format(opt))

    def right(self, opt):
        """ Crea dipendenza tra la parola in cima allo stack e la prossima nella lista.
        Rimuove la parola dalla lista, poppa lo stack e inserisce tale parola nella lista,
        in prima posizione """
        dependent, self.__queue = self.__queue[0], self.__queue[1:]
        head = self.__stack.pop()
        self.__queue.insert(0, head)

        self.__tree.add_dependency(head.tid , dependent.tid, opt) #uso gli id
        self.__history.append("right_{}".format(opt))


    def get_dependencies_by_head(self, head):
        return self.__tree.get_dependencies_by_head(head)

    #<partially_useless_methods>  (o forse no...)
    def next_stack(self):
        return self.__stack[-1] if self.stack_size() > 0 else False

    def next_queue(self):
        return self.__queue[0] if self.queue_size() > 0 else False

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
        return len(self.__queue) == 0 and len(self.__stack) == 1



class SentenceTransitions(object):
    def __init__(self, sentence, tree):
        self.sentence = sentence
        self.states = None

        parser = Parser(sentence)
        transitions = list()

        while not parser.is_final_state():
            do_shift = True

            transitions.append(ParserState(parser))
    #        print(transitions[-1])

            if parser.stack_size() > 0 and parser.queue_size() > 0:
                q, s = parser.next_queue().tid, parser.next_stack().tid
                #verifico applicabilità left
                rel = tree.dependency_exists(q, s)
                if rel:
                    parser.left(rel)
                    do_shift = False
                else:
                    #verifico applicabilità right
                    rel = tree.dependency_exists(s, q)
                    if rel and len(tree.get_dependencies_by_head(q)) == len(parser.get_dependencies_by_head(q)):
                        parser.right(rel)
                        do_shift = False
            #verifico applicabilità shift
            if do_shift and parser.queue_size() > 0:
                parser.shift()

        self.states = zip(transitions, parser.history())



class ParserState(object):
    def __init__(self, parser):
        stack, queue = parser.get_stack(), parser.get_queue()
        tree = parser.get_tree()

        self.s0 = stack[-1] if len(stack) > 0 else None
        self.s1 = stack[-2] if len(stack) > 1 else None
        self.q0 = queue[0] if len(queue) > 0 else None
        self.q1 = queue[1] if len(queue) > 1 else None
        self.q2 = queue[2] if len(queue) > 2 else None
        self.q3 = queue[3] if len(queue) > 3 else None

        #head del top dello stack
        self.s0h = tree.get_head(self.s0.tid)[0] if self.s0 else None
        self.s0l = tree.get_leftmost_child(self.s0.tid) if self.s0 else None
        self.s0r = tree.get_rightmost_child(self.s0.tid) if self.s0 else None
        self.q0l = tree.get_leftmost_child(self.q0.tid) if self.q0 else None



#        print(Token(None))

    def __str__(self):
        return "s0: {}\ns1: {}\nq0: {}\nq1: {}\nq2: {}\nq3: {}\ns0h: {}\ns0l: {}\ns0r: {}\nq0l: {}".format(self.s0, self.s1, self.q0, self.q1, self.q2, self.q3, self.s0h, self.s0l, self.s0r, self.q0l)
