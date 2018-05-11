#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enums

from sentence import *
from enums import ParserAction, RelationType
import features2 as f2

from treebank import Treebank, tree
from sklearn.linear_model import LogisticRegression
import collections #for Counter

class ParsingError(Exception):
    def __init__(self, message, partial_prediction):
        self.message = message
        self.tree = partial_prediction


class Parser(object):
    def __init__(self):
        self.__oracle = Oracle()
        self.__stack = list()
        self.__queue = list()
        self.__tree = None
        self.__history = list()

    def init(self, sentence):
        self.__stack = [Token(0)] #root
        self.__queue = [token for token in sentence]
        self.__tree = tree(sentence, False) #numero di nodi pari al numero di parole
        self.__history = list()

        return self

    def fit_oracle(self, training_set):
        self.__oracle.fit(training_set)
        return self

    def parse(self, sentence):
        self.init(sentence)

        while not self.is_final_state():
            avail_actions = self.__get_avail_actions()

            if len(avail_actions) == 0:
                raise ParsingError("Unable to parse the sentence", self.__tree)

            configuration = ParserState(self)
            action = self.oracle.predict(configuration)

            if action in avail_actions:
                #ci fidiamo dell'oracolo
                self.__exec(action)
            else:
                #azione random fattibile --> shift
                self.shift()

        return self.__tree

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
#        print("shift")

    def left(self, opt):
        """ Crea dipendenza tra la prossima parola nella lista e quella
        in cima allo stack, rimuovendola dalla pila."""

        dependent = self.__stack.pop()
        head = self.__queue[0]
        self.__tree.add_dependency(head.tid, dependent.tid, opt) #uso gli id
        self.__history.append(ParserAction.get_parser_action("left", opt))
#        print("left")


    def right(self, opt):
        """ Crea dipendenza tra la parola in cima allo stack e la prossima nella lista.
        Rimuove la parola dalla lista, poppa lo stack e inserisce tale parola nella lista,
        in prima posizione """

        dependent, self.__queue = self.__queue[0], self.__queue[1:]
        head = self.__stack.pop()
        self.__queue.insert(0, head)
        self.__tree.add_dependency(head.tid , dependent.tid, opt) #uso gli id
        self.__history.append(ParserAction.get_parser_action("right", opt))
#        print("right")

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
        i = 0

        while not parser.is_final_state():
            i += 1
            if i == 30:
                break
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
        #no svm perchè "hard to scale to dataset with more than a couple of 10000 samples" [cit. documentazione]
        self.__model = LogisticRegression(multi_class="multinomial", solver="newton-cg")
        self.__encoder = f2.FeatureEncoder()

    @property
    def encoder(self):
        return self.__encoder


    def __fit(self, training_set):
        """Addestra l'oracolo con le frasi di un treebank"""

        examples, labels = list(), list()
        #estrazione feature dalle frasi del treebank
        for sentence, dep_tree in TreebankParser(training_set):
            transitions, actions = Parser.get_transitions(sentence, dep_tree)
            examples.extend([self.encoder.encode(t) for t in transitions])
            labels.extend([label.value for label in actions]) #enum magic

        examples = self.encoder.oneHotEncoding(examples)
        print("Training model with {} examples".format(len(labels)))
        self.__model.fit(examples, labels)

        return self

    def fit(self, training_set):
        examples, labels = list(), list()

        for sentence, dep_tree in Treebank().parse(training_set):
            transitions, actions = Parser.get_transitions(sentence, dep_tree)

            for t, a in zip(transitions, actions):
                features = self.encoder.encodeFeatures(t)
                examples.extend(features)

                labels.extend([a.value] * len(features))

        examples = self.encoder.fit_oneHotEncoding(examples)
        print("Training model with {} examples".format(len(labels)))
        self.__model.fit(examples, labels)
        return self

    def predict(self, configuration):
        """ """

        predictions = collections.Counter()
        feature_vectors = self.encoder.encodeFeatures(configuration)

        for fv in feature_vectors:
           encoded = self.encoder.oneHotEncoding(fv)
           predictions[self.__model.predict(encoded)[0]] += 1

        return ParserAction(predictions.most_common(1)[0][0])


    def __predict(self, configuration):
        """Data una configurazione del parser, predice l'azione da eseguire"""

        feature_vector = self.encoder.encodeFeature(configuration)
        action = self.__model.predict(feature_vector.toarray())
        return ParserAction(action[0])



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

    def __getitem__(self, key): #key: enums.FeatureTemplateName
        try:
            if key is enums.FeatureTemplateName.POS_S0:
                return self.s0.pos
            if key is enums.FeatureTemplateName.POS_S1:
                return self.s1.pos
            if key is enums.FeatureTemplateName.POS_Q0:
                return self.q0.pos
            if key is enums.FeatureTemplateName.POS_Q1:
                return self.q1.pos
            if key is enums.FeatureTemplateName.POS_Q2:
                return self.q2.pos
            if key is enums.FeatureTemplateName.POS_Q3:
                return self.q3.pos

            if key is enums.FeatureTemplateName.WF_S0:
                return self.s0.lemma
            if key is enums.FeatureTemplateName.WF_Q0:
                return self.q0.lemma
            if key is enums.FeatureTemplateName.WF_Q1:
                return self.q1.lemma

            if key is enums.FeatureTemplateName.DEP_S0L:
                return self.s0l[1]
            if key is enums.FeatureTemplateName.DEP_S0:
                return self.tree[self.s0.tid].dtype
#                return self.s0.dtype ###curr
            if key is enums.FeatureTemplateName.DEP_S0R:
                return self.s0r[1]
            if key is enums.FeatureTemplateName.DEP_Q0L:
                return self.q0l[1]
        except (TypeError, AttributeError):
            return None


    def __str__(self):
        return "s0: {}\ns1: {}\nq0: {}\nq1: {}\nq2: {}\nq3: {}\ns0h: {}\ns0l: {}\ns0r: {}\nq0l: {}".format(self.s0, self.s1, self.q0, self.q1, self.q2, self.q3, self.s0h, self.s0l, self.s0r, self.q0l)
