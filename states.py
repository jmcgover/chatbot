#! /usr/bin/env python3

import sys
import os

"""Base State Class"""
class State(object):
    def __str__(self):
        return "%s State" % self.__class__.__name__
    def run(self):
        assert False, "%s not implemented" % self.run.__name__
    def next(self, input):
        assert False, "%s not implemented" % self.next.__name__

"""Start State"""
class Start(State):
    def run(self):
        print("Running %s" % self)
        return None
    def next(self, input):
        print("%s Transition" % self)
        nextState = self
        return nextState

class ChatBot(object):
    def __init__(self):
        return

def main():
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
