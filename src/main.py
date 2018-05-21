#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from parser import Parser, Oracle, ParsingError
from treebank import Treebank, tree
from evaluation import Evaluation

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.externals import joblib

from timeit import default_timer as timer
import random



def format_time(time):
    strtime = "{:03.5f} m".format(time/60) if time >= 60 else "{:03.5f} s".format(time)
    return strtime


if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit("Usage: ./{} training_set dev_set test_set output_file".format(sys.argv[0]))

    training_set = sys.argv[1]
    dev_set = sys.argv[2]
    test_set = sys.argv[3]
    result_file = sys.argv[4]

################################################################################

    print("Training parser on {}... ".format(training_set), flush=True)
    start = timer()
    parser = Parser().fit_oracle(training_set)
    print("Training completed in {}".format(format_time(timer() - start)), flush=True)

    print("Test parser on {}".format(dev_set), flush=True)
    tb = Treebank().parse(dev_set)
    evaluation = Evaluation(num_classes=3)

    for index, (sentence, gold_tree) in enumerate(tb):
        try:
            predicted_tree = parser.parse(sentence)
            evaluation.update(gold_tree, predicted_tree)
        except ParsingError:
            print("Can't parse sentence {}".format(index))

    print("\nExact match: {} ({}/{})".format(evaluation.exact_match, evaluation.num_exact_tree, evaluation.tot_tree))
    print("Unlabelled attachment score: {}".format(evaluation.unlabelled_attachment_score))
    print("Labelled attachment score: {}".format(evaluation.labelled_attachment_score))
    print("Precision: {}".format(evaluation.get_precision()))
    print("Recall: {}\n".format(evaluation.get_recall()))

################################################################################

    print("Testing parser on {}".format(test_set))

    tb = Treebank().parse(test_set, labelled=False)
    predictions = Treebank()

    for index, sentence in enumerate(tb):
        try:
            predicted_tree = parser.parse(sentence)
        except ParsingError as pe:
            print("Can't parse sentence {}".format(index))
            predicted_tree = pe.tree

        predictions.add_sentence(predicted_tree)
    else:
        predictions.persist(result_file)
        print("Results wrote in {}".format(result_file))
