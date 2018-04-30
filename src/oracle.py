#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression

from treebank import TreebankParser
from features import FeatureEncoder


class Oracle(object):
    def __init__(self):
        self.__model = None
        self.__encoder = FeatureEncoder()

    @property
    def featureEncoder(self):
        return self.__encoder


    def fit(self, training_set):
        """Addestra l'oracolo con le frasi di un treebank"""

        #legge treebank
        examples, labels = TreebankParser().parse(training_set)
        #ottiene raw feature vector di ciascun esempio
        examples = [self.__encoder.encode(e) for e in examples]
        labels = [self.__encoder.encodeLabel(l) for l in labels]
        #one hot encoding degli esempi
        examples = self.__encoder.oneHotEncoding(examples)
        #training
        self.__model = LogisticRegression(multi_class="ovr", solver="newton-cg").fit(examples, labels)
        return self



    def predict(self, configuration):
        return self.__model.predict(configuration.toarray())
#        fv = self.__encoder.encodeFeature(configuration)
#        return self.__model.predict(fv.toarray())



    def load_model(self, model_file):
        self.__model = joblib.loads(model_file)
