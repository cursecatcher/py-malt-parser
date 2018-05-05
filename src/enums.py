#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum

class FeatureType(enum.Enum):
    POS = 1
    LEMMA = 2
    DEPENDENCY = 3

class ParserAction(enum.Enum):
    SHIFT = 1
    LEFT = 2
    RIGHT = 3
    LEFT_NSUBJ = 4
    RIGHT_NSUBJ = 5
    LEFT_DOBJ = 6
    RIGHT_DOBJ = 7

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
    NONAME = 0
    NSUBJ = 1
    DOBJ = 2

    @classmethod
    def get_relation_type(cls, relation):
        if relation == "nsubj":
            return RelationType.NSUBJ
        if relation == "dobj":
            return RelationType.DOBJ
        return RelationType.NONAME
