#! /usr/bin/env python3

import sys
import os

import random

"""Base State Class"""
class State(object):
    name = "BASE_STATE_CLASS"
    def __init__(self, cur_info):
        self.cur_info = cur_info
    def __str__(self):
        return self.name
    def __eq__(self, other):
        return other == "%s" % self
    def run(self):
        assert False, "%s not implemented" % self.run.__name__
    def next(self, info):
        assert False, "%s not implemented" % self.next.__name__

"""Start State"""
class OneStart(State):
    name = "1_START"
    def run(self):
        return None
    def next(self, info):
        nextState = self
        nextState = OneInitialOutreach(info)
        return nextState

"""Start State"""
class TwoStart(State):
    name = "2_START"
    def run(self):
        return None
    def next(self, info):
        nextState = None
        if info["intention"] == info["me"]:
            if info["text"] in OneInitialOutreach.replies or info["text"] in OneSecondaryOutreach:
                nextState = TwoOutreachReply(info)
        else:
            nextState = self
            self.cur_info = info
        return nextState

"""End State"""
class End(State):
    name = "END"
    replies = ["ok great talk"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return None

"""1 Initial Outreach"""
class OneInitialOutreach(State):
    name = "1_INITIAL_OUTREACH"
    replies = ["hi","hello"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return OneInquiry(info)

"""1 Secondary Outreach"""
class OneSecondaryOutreach(State):
    name = "1_SECONDARY_OUTREACH"
    replies = ["I said hi","excuse me, hello?"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return OneInquiry(info)

"""1 Inquiry"""
class OneInquiry(State):
    name = "1_INQUIRY"
    replies = ["how are you?","what's happening?"]
    responded_replies = [None, "that's good", "nice", "awesome"]
    waiting_replies = ["aren't you going to ask how I'm doing?"]
    def __init__(self, cur_info):
        super().__init__(cur_info)
        self.responded = False
        self.waiting = False
        return
    def run(self):
        if self.responded:
            reply = random.choice(self.responded_replies)
            self.responded = False
            self.waiting = True
        elif self.waiting:
            reply = random.choice(self.waiting_replies)
        else:
            reply = random.choice(self.replies)
            self.responded = True
        return (reply,)
    def next(self, info):
        nextState = self
        if info["text"] in TwoInquiry.replies:
            nextState = OneInquiryReply(info)
        else:
            self.waiting = True
        return nextState

"""1 Inquiry Reply"""
class OneInquiryReply(State):
    name = "1_INQUIRY_REPLY"
    replies = ["I'm good","I'm fine, thanks for asking"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return End(info)

"""2 Outreach Reply"""
class TwoOutreachReply(State):
    name = "2_OUTREACH_REPLY"
    replies = ["hi", "hello back at you!"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return TwoInquiryReply(info)

"""2 Outreach Reply"""
class TwoInquiryReply(State):
    name = "2_INQUIRY_REPLY"
    replies = ["I'm good", "I'm fine"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return TwoInquiry(info)

"""2 Inquiry"""
class TwoInquiry(State):
    name = "2_INQUIRY"
    replies = ["how about you?", "and yourself?"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return End(info)

def main():
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
