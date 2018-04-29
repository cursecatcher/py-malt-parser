#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from parser import ParserState

class Features(object):
    def __init__(self, state):
        self.pos_s0 = state.s0.pos if state.s0 else None
        self.pos_s1 = state.s1.pos if state.s1 else None
        self.pos_q0 = state.q0.pos if state.q0 else None
        self.pos_q1 = state.q1.pos if state.q1 else None
        self.pos_q2 = state.q2.pos if state.q2 else None
        self.pos_q3 = state.q3.pos if state.q3 else None

        self.wf_s0h = state.s0h.wordform if state.s0h else None
        self.wf_s0 = state.s0.wordform if state.s0 else None
        self.wf_q0 = state.q0.wordform if state.q0 else None
        self.wf_q1 = state.q1.wordform if state.q1 else None

        self.dep_s0l = state.s0l[1] if state.s0l else None
        self.dep_s0 = state.s0.dtype if state.s0 else None
        self.dep_s0r = state.s0r[1] if state.s0r else None
        self.dep_q0l = state.q0l[1] if state.q0l else None


    def feature_vector(self):
        return [self.pos_s0, self.pos_s1, self.pos_q0, self.pos_q1, self.pos_q2, self.pos_q3,
                self.wf_s0h, self.wf_s0, self.wf_q0, self.wf_q1,
                self.dep_s0l, self.dep_s0, self.dep_s0r, self.dep_q0l]
