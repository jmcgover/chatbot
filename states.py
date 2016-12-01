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

class TimeoutState(State):
    def __init__(self, cur_info):
        super().__init__(cur_info)
    def is_timedout(self, info):
        last = self.cur_info["timestamp"]
        cur = info["timestamp"]
        if (cur - last).total_seconds() > self.cur_info["timeout"]:
            return True
        return False

"""1 Giveup Frustrated"""
class OneGiveupFrustrated(State):
    name = "1_GIVEUP_FRUSTRATED"
    replies = ["Ok, forget you.", "Whatever."]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return End(info)

"""2 Giveup Frustrated"""
class TwoGiveupFrustrated(State):
    name = "2_GIVEUP_FRUSTRATED"
    replies = ["Ok, forget you.", "Whatever."]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return End(info)

"""1 Start State"""
class OneStart(State):
    name = "1_START"
    def run(self):
        return None
    def next(self, info):
        nextState = self
        nextState = OneInitialOutreach(info)
        return nextState

"""2 Start State"""
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
class OneInitialOutreach(TimeoutState):
    name = "1_INITIAL_OUTREACH"
    replies = ["hi","hello"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        if "text" not in info:
            if self.is_timedout(info):
                return OneSecondaryOutreach(info)
            # Keep original state
            return self
        return OneInquiry(info)

"""1 Secondary Outreach"""
class OneSecondaryOutreach(TimeoutState):
    name = "1_SECONDARY_OUTREACH"
    replies = ["I said hi","excuse me, hello?"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        if "text" not in info:
            if self.is_timedout(info):
                return OneGiveupFrustrated(info)
            # Keep original state
            return self
        return OneInquiry(info)

"""1 Inquiry"""
class OneInquiry(TimeoutState):
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
        if "text" not in info:
            if self.is_timedout(info):
                return OneGiveupFrustrated(info)
            # Keep original time
            return self
        if info["text"] in TwoInquiry.replies:
            # Update time
            nextState = OneInquiryReply(info)
        else:
            self.waiting = True
        return nextState

"""1 Inquiry Reply"""
class OneInquiryReply(TimeoutState):
    name = "1_INQUIRY_REPLY"
    replies = ["I'm good","I'm fine, thanks for asking"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return End(info)

"""2 Outreach Reply"""
class TwoOutreachReply(TimeoutState):
    name = "2_OUTREACH_REPLY"
    replies = ["hi", "hello back at you!"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        if "text" not in info:
            if self.is_timedout(info):
                return TwoGiveupFrustrated(info)
            # Keep original time
            return self
        return TwoInquiryReply(info)

"""2 Outreach Reply"""
class TwoInquiryReply(TimeoutState):
    name = "2_INQUIRY_REPLY"
    replies = ["I'm good", "I'm fine"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        return TwoInquiry(info)

"""2 Inquiry"""
class TwoInquiry(TimeoutState):
    name = "2_INQUIRY"
    replies = ["how about you?", "and yourself?"]
    def run(self):
        reply = random.choice(self.replies)
        return (reply,)
    def next(self, info):
        if "text" not in info:
            if self.is_timedout(info):
                return TwoGiveupFrustrated(info)
            # Keep original time
            return self
        return End(info)

def main():
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
