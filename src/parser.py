#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tree
from sentence import *
from features import Features

#oracle
from treebank import TreebankParser
from features import FeatureEncoder
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression

import enum

class ParserAction(enum.Enum):
    SHIFT = 1
    LEFT = 2
    RIGHT = 3
    LEFT_NSUBJ = 4
    RIGHT_NSUBJ = 5
    LEFT_DOBJ = 6
    RIGHT_DOBJ = 7

    @classmethod
    def get_parser_action(cls, action, relation):
        if action == "left":
            if relation is RelationType.NSUBJ:
                return ParserAction.LEFT_NSUBJ
            else:
                return ParserAction.LEFT_DOBJ if relation is RelationType.DOBJ else ParserAction.LEFT
        elif action == "right":
            if relation is RelationType.NSUBJ:
                return ParserAction.RIGHT_NSUBJ
            else:
                return ParserAction.RIGHT_DOBJ if relation is RelationType.DOBJ else ParserAction.RIGHT

        return ParserAction.SHIFT


class Parser(object):
    def __init__(self):
        self.__oracle = Oracle()
        self.__stack = list()#[Token(0)] #root
        self.__queue = list()#[token for token in sentence]
        self.__tree = list()#tree.tree(sentence, False) #numero di nodi pari al numero di parole
        self.__history = list()

    def init(self, sentence):
        self.__stack = [Token(0)] #root
        self.__queue = [token for token in sentence]
        self.__tree = tree.tree(sentence, False) #numero di nodi pari al numero di parole
        self.__history = list()
        return self

    def parse(self, sentence):
        self.init(sentence)

        while not self.is_final_state():
            avail_actions = self.__get_avail_actions()

            if len(avail_actions) == 0:
                raise Exception("Unable to parse the sentence")

            configuration = ParserState(self)
            action = self.oracle.predict(configuration)

            if action in avail_actions:
                #ci fidiamo dell'oracolo
                self.__exec(action)
            else:
                #azione random fattibile --> shift
                self.shift()

        return self.history()

    def __exec(self, action):
        if action is ParserAction.SHIFT:
            self.shift()
        elif action is ParserAction.LEFT:
            self.left(RelationType.NONAME)
        elif action is ParserAction.LEFT_DOBJ:
            self.left(RelationType.DOBJ)
        elif action is ParserAction.LEFT_NSUBJ:
            self.left(RelationType.NSUBJ)
        elif action is ParserAction.RIGHT:
            self.right(RelationType.NONAME)
        elif action is ParserAction.RIGHT_DOBJ:
            self.right(RelationType.DOBJ)
        elif action is ParserAction.RIGHT_NSUBJ:
            self.right(RelationType.NSUBJ)




    def __get_avail_actions(self):
        """Restituisce l'insieme delle azioni fattibili in base allo stato del parser"""
        moves = set()

        if self.queue_size() > 0:
            moves.add(ParserAction.SHIFT)
            if self.stack_size() > 0:
                moves.update({action for action in ParserAction})

        return moves

    @property
    def oracle(self):
        return self.__oracle

    def history(self):
        return self.__history

    def fit_oracle(self, training_set):
        self.__oracle.fit(training_set)

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
        self.__history.append(ParserAction.SHIFT)

    def left(self, opt):
        """ Crea dipendenza tra la prossima parola nella lista e quella
        in cima allo stack, rimuovendola dalla pila."""

        dependent = self.__stack.pop()
        head = self.__queue[0]
        self.__tree.add_dependency(head.tid, dependent.tid, opt) #uso gli id
        self.__history.append(ParserAction.get_parser_action("left", opt))


    def right(self, opt):
        """ Crea dipendenza tra la parola in cima allo stack e la prossima nella lista.
        Rimuove la parola dalla lista, poppa lo stack e inserisce tale parola nella lista,
        in prima posizione """

        dependent, self.__queue = self.__queue[0], self.__queue[1:]
        head = self.__stack.pop()
        self.__queue.insert(0, head)
        self.__tree.add_dependency(head.tid , dependent.tid, opt) #uso gli id
        self.__history.append(ParserAction.get_parser_action("right", opt))

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




    def is_final_state(self):
        """Condizione di terminazione del parsing: lo stack contiene solo la
        radice e la coda è vuota, in quanto tutte le parole sono state analizzate"""
        return len(self.__queue) == 0 and len(self.__stack) == 1

    @staticmethod
    def get_transitions(sentence, tree):
        parser = Parser().init(sentence)
        transitions = list()

        while not parser.is_final_state():
            do_shift = True

            transitions.append(ParserState(parser))

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

        return (transitions, parser.history())

class Oracle(object):
    def __init__(self):
        self.__model = LogisticRegression(multi_class="multinomial", solver="newton-cg")
        self.__encoder = FeatureEncoder()

    @property
    def encoder(self):
        return self.__encoder


    def fit(self, training_set):
        """Addestra l'oracolo con le frasi di un treebank"""

        examples, labels = list(), list()
        #estrazione feature dalle frasi del treebank
        for sentence, dep_tree in TreebankParser(training_set):
            transitions, actions = Parser.get_transitions(sentence, dep_tree)
            examples.extend([self.encoder.encode(t) for t in transitions])
            labels.extend([label.value - 1 for label in actions]) #enum magic

        examples = self.encoder.oneHotEncoding(examples)
        print("Training model with {} examples".format(len(labels)))
        self.__model.fit(examples, labels)

        return self



    def predict(self, configuration):
        """Data una configurazione del parser, predice l'azione da eseguire"""
#        print(type(configuration))
        feature_vector = self.encoder.encodeFeature(configuration)
        action = self.__model.predict(feature_vector.toarray())
        return ParserAction(action[0]+1)
#        fv = self.__encoder.encodeFeature(configuration)
#        return self.__model.predict(fv.toarray())



    def load_model(self, model_file):
        self.__model = joblib.loads(model_file)



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
