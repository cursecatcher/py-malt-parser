#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enums

from sentence import *
from enums import ParserAction, RelationType
import features

from treebank import Treebank, tree
from sklearn.linear_model import LogisticRegression
import collections #for Counter

class ParsingError(Exception):
    """ Rappresenta quell'eccezione che vorresti non fosse mai lanciata. Temila """

    def __init__(self, message, partial_prediction):
        self.message = message
        self.tree = partial_prediction


class Parser(object):
    def __init__(self):
        self.__oracle = Oracle()
        self.__stack = list()
        self.__buffer = list()
        self.__tree = None
        self.__history = list()

    def init(self, sentence):
        self.__stack = [Token(0)] #root
        self.__buffer = [token for token in sentence]
        self.__tree = tree(sentence, set_dependencies=False) #numero di nodi pari al numero di parole
        self.__history = list()

        return self

    @property
    def oracle(self):
        return self.__oracle


    def get_tree(self):
        return self.__tree

    def get_stack(self):
        return list(self.__stack)

    def get_buffer(self):
        return list(self.__buffer)

    def history(self):
        return self.__history


    def fit_oracle(self, training_set):
        self.__oracle.fit(training_set)
        return self

    def parse(self, sentence):
        self.init(sentence)

        while not self.__is_final_state():
            avail_actions = self.__get_avail_actions()

            if len(avail_actions) == 0:
                raise ParsingError("Unable to parse the sentence", self.__tree)

            configuration = ParserState(self)
            action = self.oracle.predict(configuration)

            if action in avail_actions: self.__exec(action)
            else:                       self.shift()

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

        if self.buffer_size() > 0:
            moves.add(ParserAction.SHIFT)
            if self.stack_size() > 0:
                moves.update({action for action in ParserAction})

        return moves

    def shift(self):
        """ Estrae prossima parola dalla lista e la pusha sullo stack """

        self.__stack.append(self.__buffer[0])
        self.__buffer = self.__buffer[1:]
        self.__history.append(ParserAction.SHIFT)
#        print("shift")

    def left(self, opt):
        """ Crea dipendenza tra la prossima parola nella lista e quella
        in cima allo stack, rimuovendola dalla pila."""

        dependent = self.__stack.pop()
        head = self.__buffer[0]
        self.__tree.add_dependency(head.tid, dependent.tid, opt) #uso gli id
        self.__history.append(ParserAction.get_parser_action("left", opt))
#        print("left")


    def right(self, opt):
        """ Crea dipendenza tra la parola in cima allo stack e la prossima nella lista.
        Rimuove la parola dalla lista, poppa lo stack e inserisce tale parola nella lista,
        in prima posizione """

        dependent, self.__buffer = self.__buffer[0], self.__buffer[1:]
        head = self.__stack.pop()
        self.__buffer.insert(0, head)
        self.__tree.add_dependency(head.tid , dependent.tid, opt) #uso gli id
        self.__history.append(ParserAction.get_parser_action("right", opt))
#        print("right")

    def get_dependencies_by_head(self, head):
        return self.__tree.get_dependencies_by_head(head)

    #<partially_useless_methods>  (o forse no...)
    def next_stack(self):
        return self.__stack[-1] if self.stack_size() > 0 else False

    def next_buffer(self):
        return self.__buffer[0] if self.buffer_size() > 0 else False

    def stack_size(self):
        return len(self.__stack)

    def buffer_size(self):
        return len(self.__buffer)
    #</partially_useless_methods>



    def __is_final_state(self):
        """Condizione di terminazione del parsing: lo stack contiene solo la
        radice e la coda è vuota, in quanto tutte le parole sono state analizzate"""

        return len(self.__buffer) == 0 and len(self.__stack) == 1

    @staticmethod
    def get_transitions(sentence, tree):
        """ Costruisce, utilizzando il gold_tree come guida, la sequenza di operazioni
        necessarie a parsare la frase. Restituisce due liste, contenenti la prima le
        configurazioni del parser durante il processo, e la seconda le azioni eseguite dal parser """

        parser = Parser().init(sentence)
        transitions = list()

        while not parser.__is_final_state():
            do_shift = True

            transitions.append(ParserState(parser))

            if parser.stack_size() > 0 and parser.buffer_size() > 0:
                q, s = parser.next_buffer().tid, parser.next_stack().tid
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
            if do_shift and parser.buffer_size() > 0:
                parser.shift()

        return (transitions, parser.history())


class Oracle(object):
    def __init__(self):
        #no svm perchè "hard to scale to dataset with more than a couple of 10000 samples" [cit. documentazione]
        self.__model = LogisticRegression(multi_class="multinomial", solver="newton-cg")
        self.__encoder = features.FeatureEncoder()

    @property
    def encoder(self):
        return self.__encoder


    def fit(self, training_set):
        """ Addestra l'oracolo estraendo le features necessarie dagli esempi del training set;
        le configurazioni del parser durante il parsing corretto della frase sono gli esempi
        utilizzati nel training, e le azioni compiute dal parser sono le corrispondenti labels. """

        examples, labels = list(), list()

        for sentence, dep_tree in Treebank().parse(training_set):
            #ottiene configurazioni del parser e sequenza di operazioni
            #necessarie a parsare correttamente la frase
            transitions, actions = Parser.get_transitions(sentence, dep_tree)

            #codifica features e costruzione del training set
            for t, a in zip(transitions, actions):
                #associa le configurazioni del parser alla corrispondente azione eseguita
                features = self.encoder.encodeFeatures(t)
                examples.extend(features)
                labels.extend([a.value] * len(features))

        #one hot encoding delle features
        examples = self.encoder.fit_oneHotEncoding(examples)
        print("Training model with {} examples".format(len(labels)))
        #addestramento del modello
        self.__model.fit(examples, labels)

        return self

    def predict(self, configuration):
        """Data una configurazione del parser, predice l'azione da eseguire"""

        predictions = collections.Counter()
        feature_vectors = self.encoder.encodeFeatures(configuration)

        for fv in feature_vectors:
           encoded = self.encoder.oneHotEncoding(fv)
           predictions[self.__model.predict(encoded)[0]] += 1

        return ParserAction(predictions.most_common(1)[0][0])


class ParserState(object):
    """ La classe rappresenta lo stato interno del parser, ossia una sua configurazione.
    Essa è caratterizzata dai primi due elementi in cima allo stack e dai primi quattro
    elementi nella coda. Permette l'estrazione delle feature per l'apprendimento.  """

    def __init__(self, parser):
        """Inizializza l'oggetto estraendo gli elementi necessari dalle strutture dati
        del parser: stack, lista e albero parziale. """

        stack, buffer = parser.get_stack(), parser.get_buffer()
        tree = parser.get_tree()

        def get(iterable, index, threshold=None):
            if threshold is None:
                threshold = index if index >= 0 else abs(index+1)

            return iterable[index] if len(iterable) > threshold else None

        #feature statiche
        self.s0 = get(stack, -1)
        self.s1 = get(stack, -2)
        self.q0 = get(buffer, 0)
        self.q1 = get(buffer, 1)
        self.q2 = get(buffer, 2)
        self.q3 = get(buffer, 3)

        def get(tree_method, token):
            return tree_method(token.tid) if token else None

        #feature dinamiche
        self.s0h = get(tree.get_head, self.s0)
        self.s0l = get(tree.get_leftmost_child, self.s0)
        self.s0r = get(tree.get_rightmost_child, self.s0)
        self.q0l = get(tree.get_leftmost_child, self.q0)

    def __getitem__(self, key): #key: enums.FeatureTemplateName
        """ Overloading delle []: permette di accedere agli attributi dell'oggetto
        utilizzando i nomi delle possibili feature, definite nell'enumerativo
        FeatureTemplateName """

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
            if key is enums.FeatureTemplateName.DEP_S0R:
                return self.s0r[1]
            if key is enums.FeatureTemplateName.DEP_Q0L:
                return self.q0l[1]
        except (TypeError, AttributeError):
            return None


    def __str__(self):
        return "s0: {}\ns1: {}\nq0: {}\nq1: {}\nq2: {}\nq3: {}\ns0h: {}\ns0l: {}\ns0r: {}\nq0l: {}".format(self.s0, self.s1, self.q0, self.q1, self.q2, self.q3, self.s0h, self.s0l, self.s0r, self.q0l)
