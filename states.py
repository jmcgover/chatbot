#! /usr/bin/env python3

import sys
import os

import random

"""Base State Class"""
class State(object):
    def __str__(self):
        return "%s State" % self.__class__.__name__
    def __eq__(self, other):
        return other == "%s" % self
    def run(self):
        assert False, "%s not implemented" % self.run.__name__
    def next(self, input):
        assert False, "%s not implemented" % self.next.__name__

"""Start State"""
class OneStart(State):
    def __str__(self):
        return "1_START"
    def run(self):
        return None
    def next(self, input):
        nextState = self
        nextState = OneInitialOutreach()
        return nextState

"""Start State"""
class TwoStart(State):
    def __str__(self):
        return "2_START"
    def run(self):
        return None
    def next(self, input):
        nextState = self
        if input["intention"] == input["me"]:
            if input["text"] in OneInitialOutreach.replies or input["text"] in OneSecondaryOutreach:
                nextState = TwoOutreachReply()
        return nextState

"""End State"""
class End(State):
    def __str__(self):
        return "END"
    def run(self):
        return "ok great talk bye"
    def next(self, input):
        return None

"""1 Initial Outreach"""
class OneInitialOutreach(State):
    replies = ["hi","hello"]
    def __str__(self):
        return "1_INITIAL_OUTREACH"
    def run(self):
        reply = random.choice(self.replies)
        return reply
    def next(self, input):
        return OneInquiry()

"""1 Secondary Outreach"""
class OneSecondaryOutreach(State):
    replies = ["I said hi","excuse me, hello?"]
    def __str__(self):
        return "1_SECONDARY_OUTREACH"
    def run(self):
        reply = random.choice(self.replies)
        return reply
    def next(self, input):
        return OneInquiry()

"""1 Inquiry"""
class OneInquiry(State):
    replies = ["how are you?","what's happening?"]
    responded_replies = [None, "that's good", "nice", "awesome"]
    waiting_replies = ["aren't you going to ask how I'm doing?"]
    def __init__(self):
        super().__init__()
        self.responded = False
        self.waiting = False
        return
    def __str__(self):
        return "1_INQUIRY"
    def run(self):
        if self.responded:
            reply = random.choice(self.responded_replies)
            self.responded = False
            self.waiting = True
        elif self.waiting:
            print("Waiting")
            reply = random.choice(self.waiting_replies)
        else:
            reply = random.choice(self.replies)
            self.responded = True
        return reply
    def next(self, input):
        nextState = self
        if input["text"] in TwoInquiry.replies:
            nextState = OneInquiryReply()
        else:
            self.waiting = True
        return nextState

"""1 Inquiry Reply"""
class OneInquiryReply(State):
    replies = ["I'm good","I'm fine, thanks for asking"]
    def __str__(self):
        return "1_INQUIRY_REPLY"
    def run(self):
        reply = random.choice(self.replies)
        return reply
    def next(self, input):
        return End()

"""2 Outreach Reply"""
class TwoOutreachReply(State):
    replies = ["hi", "hello back at you!"]
    def __str__(self):
        return "2_OUTREACH_REPLY"
    def run(self):
        reply = random.choice(self.replies)
        return reply
    def next(self, input):
        return TwoInquiryReply()

"""2 Outreach Reply"""
class TwoInquiryReply(State):
    replies = ["I'm good", "I'm fine"]
    def __str__(self):
        return "2_INQUIRY_REPLY"
    def run(self):
        reply = random.choice(self.replies)
        return reply
    def next(self, input):
        return TwoInquiry()

"""2 Inquiry"""
class TwoInquiry(State):
    replies = ["how about you?", "and yourself?"]
    def __str__(self):
        return "2_INQUIRY"
    def run(self):
        reply = random.choice(self.replies)
        return reply
    def next(self, input):
        return End()

def main():
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
