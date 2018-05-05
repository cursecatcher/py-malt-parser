#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

#https://linguistics.stackexchange.com/questions/6863/how-is-the-f1-score-computed-when-assessing-dependency-parsing
#1. exact match: percentuale di frasi correttamente parsate
#2. attachment score
#   2.1 unlabelled attachment score
#   2.2 labelled attachment score
#3. Precision/recall
#   3.1 precision: it is the percentage of dependencies with a specific type in the parser output that were correct.
#   3.2 recall: it is the percentage of dependencies with a specific type in the test set that were correctly parsed.
#   3.3 F-measure: armonic mean of precision and recall

class Evaluation(object):
    def __init__(self, num_classes):
        #aggiungo una riga e una colonna alla confusion matrix per indicare
        #la possibilità che la dipendenza non sia stata predetta o non esista
        self.__num_classes = num_classes
        self.__cm = np.zeros(shape=(num_classes+1, num_classes+1))

        self.__uas = [0, 0]
        self.__las = [0, 0]
        self.__exact = [0, 0]

    @property
    def confusion_matrix(self):
        return self.__cm.tolist()

    @property
    def num_exact_tree(self):
        return self.__exact[0]

    @property
    def tot_tree(self):
        return self.__exact[1]

    @property
    def unlabelled_attachment_score(self):
        return self.__uas[0] / self.__uas[1]

    @property
    def labelled_attachment_score(self):
        return self.__las[0] / self.__las[1]

    @property
    def exact_match(self):
        return self.__exact[0] / self.__exact[1] * 100

    def __update_cm(self, gold_tree, predicted_tree):
        gold = {(h, d): r for (h, d, r) in gold_tree.dependencies}
        pred = {(h, d): r for (h, d, r) in predicted_tree.dependencies}
        #insieme di dipendenze senza info sul tipo di relazione
        all_deps = set(gold.keys()).union(set(pred.keys()))

        for dep in all_deps:
            if dep in gold and dep in pred:
                self.__cm[gold[dep].value][pred[dep].value] += 1
            elif dep in gold:
                #false negative
                self.__cm[gold[dep].value][self.__num_classes] += 1
            else:
                #false positive
                self.__cm[self.__num_classes][pred[dep].value] += 1

        return set(gold.keys()), set(pred.keys())


    def update(self, gold_tree, predicted_tree):
        gold_deps, pred_deps = self.__update_cm(gold_tree, predicted_tree)

        # update labelled attachment score
        self.__las[0] += len(gold_tree.dependencies.intersection(predicted_tree.dependencies))
        self.__las[1] += len(gold_tree.dependencies)

        #update unlabelled attachment score
        self.__uas[0] += len(gold_deps.intersection(pred_deps))
        self.__uas[1] += len(gold_deps)

        #update exact match
        self.__exact[1] += 1
        if gold_tree == predicted_tree:
            self.__exact[0] += 1

    def get_precision(self):
        return  self.__cm.diagonal() / self.__cm.sum(axis=0)

    def get_recall(self):
        return self.__cm.diagonal() / self.__cm.sum(axis=1)

    def get_accuracy(self):
        return self.__cm.diagonal().sum() / self.__cm.sum()
