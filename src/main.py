#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import tree
from parser import Parser
from treebank import TreebankParser

#leggere training set
#per ogni frase: ricostruire dipendenze in formato "comodo"
#ricostruire sequenza operatori per fare il parsing corretto




if __name__ == "__main__":
    p = TreebankParser(sys.argv[1])
