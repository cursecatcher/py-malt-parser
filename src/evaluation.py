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
        self.__cm = np.zeros(shape=(num_classes, num_classes))
        self.__uas = 0 #unlabelled attachment score
        self.__tot_unlabelled = 0
        self.__las = 0 #labelled attachment score
        self.__tot_labelled = 0

    @property
    def confusion_matrix(self):
        return self.__cm

    @property
    def unlabelled_attachment_score(self):
        return self.__uas / self.__tot_unlabelled

    @property
    def labelled_attachment_score(self):
        return self.__las / self.__tot_labelled




    def update(self, gold_tree, predicted_tree):
        gold_deps = set(gold_tree.dependencies)
        pred_deps = set(predicted_tree.dependencies)

        self.__las += len(gold_deps.intersection(pred_deps))
        self.__tot_labelled += len(gold_deps)

        gold_deps_no_type = {(x, y) for (x, y, _) in gold_deps}
        pred_deps_no_type = {(x, y) for (x, y, _) in pred_deps}

        self.__uas += len(gold_deps_no_type.intersection(pred_deps_no_type))
        self.__tot_unlabelled += len(gold_deps_no_type)


    def get_precision(self):
        return  self.__cm.diagonal() / self.__cm.sum(axis=0)

    def get_recall(self):
        return self.__cm.diagonal() / self.__cm.sum(axis=1)

    def get_accuracy(self):
        return self.__cm.diagonal().sum() / self.__cm.sum()
