#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import tree
from parser import Parser, Oracle
from treebank import TreebankParser, format_time
from features import FeatureEncoder
from evaluation import Evaluation

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.externals import joblib

from timeit import default_timer as timer




if __name__ == "__main__":
    print("Test Parser.get_transitions")

    tb = TreebankParser(sys.argv[1])
    enc = FeatureEncoder()

    examples, labels = list(), list()

    for index, (sentence, dep_tree) in enumerate(tb):
        print("{}. {}".format(index, sentence))

        transitions, _labels = Parser.get_transitions(sentence, dep_tree)
        print("{} actions: {}".format(len(transitions), [label.value for label in _labels]))

        examples.extend([enc.encode(t) for t in transitions])
        labels.extend([l.value for l in _labels])

        if index == 3:
            break

    examples = enc.oneHotEncoding(examples)
    print(type(examples))


    print("\n\n")

    print("Test Parser.fit_oracle")
    parser = Parser()
    parser.fit_oracle(sys.argv[1])

    print("Test Oracle.predict", flush=True)

    tb = TreebankParser(sys.argv[2])
    evaluation = Evaluation(num_classes=7)
    correct, total = 0, 0

    for index, (sentence, gold_tree) in enumerate(tb):
#        transitions, labels = Parser.get_transitions(sentence, gold_tree)

#        print("Parsing frase #{}...\n".format(index), end="", flush=True)
        predicted_tree = parser.parse(sentence)

        evaluation.update(gold_tree, predicted_tree)
        #
        # all_dependencies = set(gold_tree.dependencies).union(set(predicted_tree.dependencies))
        # corrette, solo_gold, solo_pred, tot = 0,0,0,0
        #
        # for dep in all_dependencies:
        #     tot += 1
        #     if dep in gold_tree.dependencies and dep in predicted_tree.dependencies:
        #         corrette += 1
        #     elif dep in gold_tree.dependencies:
        #         solo_gold += 1
        #     elif dep in predicted_tree.dependencies:
        #         solo_pred += 1

#        print("tot: {}, tp: {}, fp: {}, fn: {}".format(tot, corrette, solo_pred, solo_gold))

#        print(predicted_tree.dependencies)

    #    evaluation.update(labels, actions)

    print("Unlabelled attachment score: {}".format(evaluation.unlabelled_attachment_score))
    print("Labelled attachment score: {}".format(evaluation.labelled_attachment_score))

#    print("accuracy: {}".format(correct/tot))

#    print("accuracy: {}".format(evaluation.get_accuracy()))
#    print("precisions: {}".format(evaluation.get_precision()))
#    print("recall: {}".format(evaluation.get_recall()))

#        num_err = [bool(predicted is actual) for predicted, actual in zip(actions, labels)].count(False)
#        print("{}/{} errors --> {}".format(num_err, len(actions), num_err/len(actions)))
        #per ogni storia in transitions: fai predict e confronta col corrispettivo in labels

#         pcorrect, ptotal = 0, 0
#         for t, l in zip(transitions, labels):
# #            fv = parser.oracle.encoder.encodeFeature(t)
# #            print(fv, type(fv))
# #            predicted = parser.oracle.predict(fv)
#             predicted = parser.oracle.predict(t)
#
# #            print(predicted, l.value)
#
#             if predicted is l:
#                 correct += 1
#                 pcorrect += 1
#             total += 1
#             ptotal += 1
#         print("Per sentence accuracy: {}".format(pcorrect/ptotal))
# #            print("{} --> {}".format(parser.oracle.predict(fv), l.value))
#     print("Total accuracy: {}".format(correct/total))

    print("\n\n")


    # print("Addestro oracolo", flush=True)
    # oracle = Oracle().fit(sys.argv[1])

    # print("Genero le features", flush=True)
    # ex, labels = TreebankParser().parse(sys.argv[1])
    # ex = [oracle.featureEncoder.encodeFeature(e) for e in ex]
    # labels = [oracle.featureEncoder.encodeLabel(l) for l in labels]
    #
    # print("Testo oracolo sul training set", flush=True)
    # correct, total = 0, 0
    #
    # for e, l in zip(ex, labels):
    #     if oracle.predict(e)[0] == l:
    #         correct += 1
    #
    # print("{}".format(correct/len(labels)))


#        print("{} --> {}".format(oracle.predict(e), l))

    # print("Genero le feature del test set", flush=True)
    #
    # ex, labels = TreebankParser().parse(sys.argv[2])
    # ex = [oracle.featureEncoder.encodeFeature(e) for e in ex]
    # labels = [oracle.featureEncoder.encodeLabel(l) for l in labels]
    #
    # print("Testo l'oracolo sul test set", flush=True)
    # correct, total = 0, 0
    #
    # for e, l in zip(ex, labels):
    #     if oracle.predict(e)[0] == l:
    #         correct += 1
    #
    # print("{}".format(correct/len(labels)))

    # tbparser = TreebankParser()
    #
    # X_train, y_train = tbparser.parse(sys.argv[1])
    #
    # print("Training classifier...", flush=True, end="")
    # start = timer()
    # logi = LogisticRegression(multi_class="ovr", solver="newton-cg").fit(X_train, y_train)
    # joblib.dump(logi, "../data/clf/logit")
    # print(format_time(timer()-start))
    #
    # print("Training classifier...", flush=True, end="")
    # start = timer()
    # clf = SVC(kernel="poly", degree=2).fit(X_train, y_train)
    # joblib.dump(clf, "../data/clf/svm")
    # print(format_time(timer()-start))





#    X_test, y_test = tbparser.parse(sys.argv[2])
    #dev_set = TreebankParser(sys.argv[3])
#    test_set = TreebankParser(sys.argv[2])
