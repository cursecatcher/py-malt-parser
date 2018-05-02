#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum

from sklearn import preprocessing


class FeatureType(Enum):
    POS = 1
    LEMMA = 2
    DEPENDENCY = 3

class feature(object):
    """Descrive una singola feature: è descritta dal tipo di feature e dal valore associato"""

    def __init__(self, feature_type, value):
        """Inizializza una feature"""
        self.__type = feature_type #enum
        self.__value = value

    @property
    def ftype(self):
        return self.__type

    @property
    def value(self):
        return self.__value


class FeatureEncoder(object):
    """Le feature raw sono stringhe. Per utilizzare i classificatori è
    necessario convertirle in valori numerici"""

    def __init__(self):
        #mapping da feature categoriali (?) a interi
        self.__pos = dict()
        self.__lemmas = dict()
        self.__deps = dict()

#        self.__labels = dict()
        self.__ohe = preprocessing.OneHotEncoder(handle_unknown="ignore")

    def encodeFeature(self, configuration):
        ### da usare in fase di predict
        fv = self.encode(configuration)
        return self.__ohe.transform([fv]) #potrebbe dare problemi

    def encode(self, configuration):
        raw_vector = Features(configuration).feature_vector()
        feature_vector = [0] * len(raw_vector)

        for index, f in enumerate(raw_vector):
            curr_dict = self.__deps

            if f.ftype is FeatureType.POS:
                curr_dict = self.__pos
            elif f.ftype is FeatureType.LEMMA:
                curr_dict = self.__lemmas

            if f.value not in curr_dict:
                #assegna numeri progressivi ai possibili valori delle feature
                curr_dict[f.value] = len(curr_dict)

            feature_vector[index] = curr_dict[f.value]

        return feature_vector

    # def encodeLabel(self, label):
    #     if label not in self.__labels:
    #         self.__labels[label] = len(self.__labels)
    #     return self.__labels[label]

    def oneHotEncoding(self, X):
        self.__ohe.fit(X)
        return self.__ohe.transform(X)
    #    return preprocessing.OneHotEncoder().fit_transform(X)





class Features(object):
    """Oggetto che descrive una configurazione del parser. Le feature utilizzate sono..."""

    def __init__(self, state):
        self.pos_s0 = feature(FeatureType.POS, state.s0.pos if state.s0 else None)
        self.pos_s1 = feature(FeatureType.POS, state.s1.pos if state.s1 else None)
        self.pos_q0 = feature(FeatureType.POS, state.q0.pos if state.q0 else None)
        self.pos_q1 = feature(FeatureType.POS, state.q1.pos if state.q1 else None)
        self.pos_q2 = feature(FeatureType.POS, state.q2.pos if state.q2 else None)
        self.pos_q3 = feature(FeatureType.POS, state.q3.pos if state.q3 else None)

        self.wf_s0h = feature(FeatureType.LEMMA, state.s0h.lemma if state.s0h else None)
        self.wf_s0 = feature(FeatureType.LEMMA, state.s0.lemma if state.s0 else None)
        self.wf_q0 = feature(FeatureType.LEMMA, state.q0.lemma if state.q0 else None)
        self.wf_q1 = feature(FeatureType.LEMMA, state.q1.lemma if state.q1 else None)

        self.dep_s0l = feature(FeatureType.DEPENDENCY, state.s0l[1] if state.s0l else None)
        self.dep_s0 = feature(FeatureType.DEPENDENCY, state.s0.dtype if state.s0 else None)
        self.dep_s0r = feature(FeatureType.DEPENDENCY, state.s0r[1] if state.s0r else None)
        self.dep_q0l = feature(FeatureType.DEPENDENCY, state.q0l[1] if state.q0l else None)


    def feature_vector(self):
        """Restituisce una lista di feature"""
        return [self.pos_s0, self.pos_s1, self.pos_q0, self.pos_q1, self.pos_q2, self.pos_q3,
                self.wf_s0h, self.wf_s0, self.wf_q0, self.wf_q1,
                self.dep_s0l, self.dep_s0, self.dep_s0r, self.dep_q0l]
