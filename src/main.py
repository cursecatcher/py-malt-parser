#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import tree
from parser import Parser
#leggere training set
#per ogni frase: ricostruire dipendenze in formato "comodo"
#ricostruire sequenza operatori per fare il parsing corretto

class TreebankParser(object):
    def __init__(self, filename):
        """ """


        for i, sentence in enumerate(self.get_sentence(filename)):
            t = tree.tree(lines=sentence)
            t.visit()

            sentence = " ".join([word[1] for word in sentence])
        #    print("Current sentence: {}".format(sentence))

            self.do_stuff(sentence, t)

            if i == 1:
                break



    def get_sentence(self, filename):
        result = list()

        with open(filename) as f:
            for line in f:
                line = line.split()
                if len(line) != 10:
                    yield result
                    result.clear()
                else:
                    result.append(line)

    def do_stuff(self, sentence, tree):
        parser = Parser(sentence)

        while not parser.is_final_state():
            do_shift = True

    #        print("q: {}, s: {}".format(parser.queue_size(), parser.stack_size()))

            if parser.stack_size() > 0 and parser.queue_size() > 0:
                q, s = parser.next_queue()[0], parser.next_stack()[0]

                # verifico applicabilità left: esiste dipendenza (q, s)?
                rel = tree.dependency_exists(q, s)
                if rel:
                    parser.left(rel)
                    do_shift = False
                    print("left_{}, ".format(rel), end="")
                else:
                    # verifico applicabilità right: esiste dipendenza (s, q) e
                    # ho tutte le dipendenze con head q?
                    rel = tree.dependency_exists(s, q)
                    if rel and len(tree.get_dependencies_by_head(q)) == len(parser.get_dependencies_by_head(q)):
#                    if rel and self.do_other_stuff(tree.get_dependencies_by_head(q), parser.get_dependencies_by_head(q)):
            #        if rel and sorted(tree.get_dependencies_by_head(q)) == sorted(parser.get_dependencies_by_head(q)):
                        parser.right(rel)
                        do_shift = False
                        print("right_{}, ".format(rel), end="")


            if do_shift and parser.queue_size() > 0:
                parser.shift()
                print("shift, ", end="")

#            parser.print_deps()

    def do_other_stuff(self, dep1, dep2):
        if dep1 is False and dep2 is False:
            return True
        if dep1 and not dep2 or not dep1 and dep2:
            return False
        return sorted(dep1) == sorted(dep2)













if __name__ == "__main__":
    p = TreebankParser(sys.argv[1])
