#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import tree
from parser import Parser
from treebank import TreebankParser, format_time

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.externals import joblib

from timeit import default_timer as timer
from oracle import Oracle




if __name__ == "__main__":
    print("Addestro oracolo", flush=True)
    oracle = Oracle().fit(sys.argv[1])

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

    print("Genero le feature del test set", flush=True)

    ex, labels = TreebankParser().parse(sys.argv[2])
    ex = [oracle.featureEncoder.encodeFeature(e) for e in ex]
    labels = [oracle.featureEncoder.encodeLabel(l) for l in labels]

    print("Testo l'oracolo sul test set", flush=True)
    correct, total = 0, 0

    for e, l in zip(ex, labels):
        if oracle.predict(e)[0] == l:
            correct += 1

    print("{}".format(correct/len(labels)))

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
