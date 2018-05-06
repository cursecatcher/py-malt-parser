#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
#import tree
from parser import Parser, Oracle
from treebank import TreebankParser, tree
from features import FeatureEncoder
from evaluation import Evaluation
import random

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.externals import joblib

from timeit import default_timer as timer

import features2 as f2


def format_time(time):
    strtime = "{:03.5f} m".format(time/60) if time >= 60 else "{:03.5f} s".format(time)
    return strtime



if __name__ == "__main__":
    if False:
        print("Test features2")

        tb = TreebankParser(sys.argv[1])
        enc = f2.FeatureEncoder()
        oracle = Oracle().fit2(sys.argv[1])

        # for index, (sentence, dep_tree) in enumerate(tb):
        #     transitions, labels = Parser.get_transitions(sentence, dep_tree)
        #     encoded = [enc.encodeFeatures(t) for t in transitions]
        #    print(encoded)


    if False:
        tb = TreebankParser(sys.argv[1])
        enc = FeatureEncoder()

        print("Test Parser.get_transitions")
        examples, labels = list(), list()

        for index, (sentence, dep_tree) in enumerate(tb):
    #        print("{}. {}".format(index, sentence))
            transitions, _labels = Parser.get_transitions(sentence, dep_tree)
            if index > 7:
                print("{} actions: {}".format(len(transitions), [label.value for label in _labels]))

            examples.extend([enc.encode(t) for t in transitions])
            labels.extend([l.value for l in _labels])

            if index == 10:
                break

        examples = enc.oneHotEncoding(examples)
        print(type(examples))
        print("\n\n")

    if True:
        print("Test Parser.fit_oracle", flush=True)
        start = timer()
        parser = Parser().fit_oracle(sys.argv[1])
        print("Parser.fit_oracle completed in {}".format(format_time(timer() - start)), flush=True)

        print("Test Oracle.predict", flush=True)

        tb = TreebankParser(sys.argv[2])
        evaluation = Evaluation(num_classes=3)

        for index, (sentence, gold_tree) in enumerate(tb):
            predicted_tree = parser.parse(sentence)
            # if index % 50 == 0:
            #     print("\nSentence: {}".format(sentence))
            #     print("Gold tree: {}".format(gold_tree.dependencies))
            #     print("Predicted: {}".format(predicted_tree.dependencies))
            #     print("Are they equals? {}".format(gold_tree == predicted_tree))
            evaluation.update(gold_tree, predicted_tree)

        print("Exact match: {} ({}/{})".format(evaluation.exact_match, evaluation.num_exact_tree, evaluation.tot_tree))
        print("Unlabelled attachment score: {}".format(evaluation.unlabelled_attachment_score))
        print("Labelled attachment score: {}".format(evaluation.labelled_attachment_score))
    #    print("Confusion matrix: {}".format(evaluation.confusion_matrix))
        print("Precision: {}".format(evaluation.get_precision()))
        print("Recall: {}".format(evaluation.get_recall()))
