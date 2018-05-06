#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enums
from sklearn import preprocessing
from treebank import tree

class FeatureEncoder(object):
    def __init__(self):
        self.__mapping = {
            enums.FeatureType.POS: {None: 0},
            enums.FeatureType.LEMMA: {None: 0},
            enums.FeatureType.DEPENDENCY: {None: 0}
        }
        self.__ohe = preprocessing.OneHotEncoder(handle_unknown="ignore")


    def encodeFeatures(self, c):
        """ Prende configurazione c del parser e costruisce i relativi feature vector
        a numeri interi """

        vector = FeatureTemplate(
            Feature(enums.FeatureTemplateName.POS_S0, c.s0.pos if c.s0 else None, enums.FeatureType.POS),
            Feature(enums.FeatureTemplateName.POS_S1, c.s1.pos if c.s1 else None, enums.FeatureType.POS),
            Feature(enums.FeatureTemplateName.POS_Q0, c.q0.pos if c.q0 else None, enums.FeatureType.POS),
            Feature(enums.FeatureTemplateName.POS_Q1, c.q1.pos if c.q1 else None, enums.FeatureType.POS),
            Feature(enums.FeatureTemplateName.POS_Q2, c.q2.pos if c.q2 else None, enums.FeatureType.POS),
            Feature(enums.FeatureTemplateName.POS_Q3, c.q3.pos if c.q3 else None, enums.FeatureType.POS),

            Feature(enums.FeatureTemplateName.WF_S0, c.s0.lemma if c.s0 else None, enums.FeatureType.LEMMA),
            Feature(enums.FeatureTemplateName.WF_Q0, c.q0.lemma if c.q0 else None, enums.FeatureType.LEMMA),
            Feature(enums.FeatureTemplateName.WF_Q1, c.q1.lemma if c.q1 else None, enums.FeatureType.LEMMA),
            Feature(enums.FeatureTemplateName.DEP_S0L, c.s0l[1] if c.s0l else None, enums.FeatureType.DEPENDENCY),

            Feature(enums.FeatureTemplateName.DEP_S0, c.s0.dtype if c.s0 else None, enums.FeatureType.DEPENDENCY),
            Feature(enums.FeatureTemplateName.DEP_S0R, c.s0r[1] if c.s0r else None, enums.FeatureType.DEPENDENCY),
            Feature(enums.FeatureTemplateName.DEP_Q0L, c.q0l[1] if c.q0l else None, enums.FeatureType.DEPENDENCY)
        )
        return self.encodeTemplate(vector)#, add_unknown=False)

        #ma non dovremmo anche associare la label  ???
        # vectors = list()
        #
        # for feature_template in enums.FeatureModel:
        #     to_encode = FeatureTemplate(*feature_template.value) #funzionerà?
        #     vectors.append(self.encodeTemplate(to_encode))
        #
        # return vectors

    def encodeTemplate(self, template):#, add_unknown=True):
        """Codifica un oggetto FeatureTemplate in un vettore di numeri interi"""

        feature_vector = [0] * len(template)

        for feature in template.feature_vector():
            if feature.type is not None:
                currdict = self.__mapping[feature.type]

                if feature.value not in currdict:
                    currdict[feature.value] = len(currdict)
                feature_vector[feature.name.value] = currdict[feature.value]

        return feature_vector

    def fit_oneHotEncoding(self, X):
        print({k.name: len(self.__mapping[k]) for k in self.__mapping})
        return self.__ohe.fit_transform(X)

    def oneHotEncoding(self, feature_vector):
        return self.__ohe.transform([feature_vector])



class FeatureTemplate(object):
    def __init__(self, *args):
        self.__features = {f.name: f for f in args}

    def feature_vector(self):
        """Restituisce il feature vector ->
        lista in cui ogni elemento è di tipo Feature e
        solo le feature passate al costruttore sono istanziate,
        mentre le altre sono a None"""
        return [\
            self.__features[template_name] if template_name in self.__features \
            else Feature(template_name) \
            for template_name in enums.FeatureTemplateName\
        ]

    def __len__(self):
        return len(enums.FeatureTemplateName)

class Feature(object):
    """Descrive una singola feature: tipo di feature e valore associato"""

    def __init__(self, feature_name, value=None, feature_type=None):
        """Inizializza una feature"""
        self.__name = feature_name #enum
        self.__type = feature_type #enum
        self.__value = value

    @property
    def name(self):
        return self.__name

    @property
    def type(self):
        return self.__type

    @property
    def value(self):
        return self.__value

    def __str__(self):
        return "({}: {})".format(self.__type, self.__value)
