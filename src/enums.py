#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum


class FeatureType(enum.Enum):
    """ Indica i possibili tipi di feature utilizzati """
    POS = 0             # part of speech
    LEMMA = 1
    DEPENDENCY = 2

    @classmethod
    def get_feature_type(cls, template):
        if template in (FeatureTemplateName.POS_S0, FeatureTemplateName.POS_S1, FeatureTemplateName.POS_Q0, FeatureTemplateName.POS_Q1, FeatureTemplateName.POS_Q2, FeatureTemplateName.POS_Q3):
            return FeatureType.POS
        if template in (FeatureTemplateName.WF_S0, FeatureTemplateName.WF_Q0, FeatureTemplateName.WF_Q1):
            return FeatureType.LEMMA

        return FeatureType.DEPENDENCY


class ParserAction(enum.Enum):
    "Indica le azioni eseguibili dal parser"

    SHIFT = 0
    LEFT = 1
    RIGHT = 2
    LEFT_NSUBJ = 3
    RIGHT_NSUBJ = 4
    LEFT_DOBJ = 5
    RIGHT_DOBJ = 6

    @classmethod
    def get_parser_action(cls, action, relation):
        if action == "left":
            if relation is RelationType.NSUBJ:
                return ParserAction.LEFT_NSUBJ
            else:
                return ParserAction.LEFT_DOBJ if relation is RelationType.DOBJ else ParserAction.LEFT
        elif action == "right":
            if relation is RelationType.NSUBJ:
                return ParserAction.RIGHT_NSUBJ
            else:
                return ParserAction.RIGHT_DOBJ if relation is RelationType.DOBJ else ParserAction.RIGHT

        return ParserAction.SHIFT


class RelationType(enum.Enum):
    """ Indica i possibili tipi di dipendenze accettate """
    NONAME = 0
    NSUBJ = 1
    DOBJ = 2

    @classmethod
    def get_relation_type(cls, relation):
        if isinstance(relation, RelationType):
            return relation

        if relation == "nsubj":
            return RelationType.NSUBJ
        if relation == "dobj":
            return RelationType.DOBJ
        return RelationType.NONAME


class FeatureTemplateName(enum.Enum):
    """ Indica le possibili feature che è possibile estrarre dalla configurazione  """
    POS_S0 = 0      #POS token in cima allo stack
    POS_S1 = 1      #POS token in seconda posizione nello stack
    POS_Q0 = 2      #POS primo token nella lista
    POS_Q1 = 3      #POS secondo token nella lista
    POS_Q2 = 4      # "  terzo      "   "      "
    POS_Q3 = 5      # "  quarto      "   "      "
    WF_S0 = 6       # wordform del token in cima allo stack
    WF_Q0 = 7       # wordform del primo token della lista
    WF_Q1 = 8       # wordform del secondo token della lista
    DEP_S0L = 9     #
    DEP_S0 = 10     #
    DEP_S0R = 11    #
    DEP_Q0L = 12    #

class FeatureModel(enum.Enum):
    """ Descrive i feature vectors utilizzati dal modello """
    F = FeatureTemplateName.POS_S0, FeatureTemplateName.POS_S1, FeatureTemplateName.POS_Q0, \
        FeatureTemplateName.POS_Q1, FeatureTemplateName.POS_Q2, FeatureTemplateName.POS_Q3, \
        FeatureTemplateName.WF_S0, FeatureTemplateName.WF_Q0, FeatureTemplateName.WF_Q1, \
        FeatureTemplateName.DEP_S0L,  FeatureTemplateName.DEP_S0R, \
        FeatureTemplateName.DEP_Q0L, FeatureTemplateName.DEP_S0,
    # F1 = FeatureTemplateName.POS_S0, FeatureTemplateName.DEP_S0, \
    #     FeatureTemplateName.DEP_S0L,  FeatureTemplateName.DEP_S0R
    # F2 = FeatureTemplateName.POS_Q0, FeatureTemplateName.DEP_Q0L, FeatureTemplateName.POS_Q1
