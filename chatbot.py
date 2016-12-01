#! /usr/bin/env python3

import sys
import os
from argparse import ArgumentParser

# Logging
import logging
from logging import handlers
LOGGER = logging.getLogger(__file__)
SH = logging.StreamHandler()
FH = logging.handlers.RotatingFileHandler("bot.log", maxBytes=5 * 1000000, backupCount = 5)
SH.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s", "%H:%M:%S"))
FH.setFormatter(logging.Formatter("%(asctime)s:%(lineno)s:%(funcName)s:%(levelname)s:%(message)s"))
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(SH)
LOGGER.addHandler(FH)

import ircbot
from ircbot import get_argparser
from ircbot import get_irc_args
from ircbot import IRCBot

from states import *
from threading import Timer

from numpy import random

import datetime
def now():
    return datetime.datetime.now()

class ChatBot(IRCBot):
    commands = {"die","*state", "*forget"}
    over_states = {"1_START","2_START", "END", "1_GIVEUP_FRUSTRATED", "2_GIVEUP_FRUSTRATED"}
    def __init__(self, channel, nickname, server, port, giveup):
        super().__init__(channel, nickname, server, port)
        self.convos = None
        self.convo_type = None
        self.max_poll_interval = 5
        self.poll_thread = None
        self.giveup = giveup
        self.reset()
    def reset(self):
        LOGGER.debug("(Re-)Initializing")
        self.convos = {}
        self.convo_type = {}
        return
    def on_welcome(self, c, e):
        super().on_welcome(c, e)
        self.start_checker()
    def start(self):
        LOGGER.debug("Starting bot")
        super().start()
        return
    def die(self, msg = "UGH I'M DYYYYIIIIING"):
        LOGGER.debug("Killing bot")
        self.stop_checker()
        super().die(msg)
        return
    def get_msg_data(self, msg):
        info = super().get_msg_data(msg)
        info["user"] = info["source"]
        info["timeout"] = self.giveup
        return info
    def start_checker(self):
        interval = random.uniform(0,self.max_poll_interval)
        #interval = random.binomial(100,0.9)/100 * self.max_poll_interval
        LOGGER.debug("Starting timer with %.3f" % interval)
        self.poll_thread = Timer(interval, self.poll)
        self.poll_thread.start()
    def stop_checker(self):
        LOGGER.debug("Ending Timer")
        self.poll_thread.cancel()
    def command(self, info):
        text = info["text"]
        if "die" == text:
            self.die()
        elif "*state" == text:
            user = info["user"]
            state_string = None
            if user in self.convos:
                state_string = "%s" % self.convos[user]
            else:
                state_string = "No conversation with %s yet" % user
            self.send_message(info, state_string)
        return
    def poll(self):
        with self.reactor.mutex:
            self.check_convos()
            self.maybe_start_convo()
            self.start_checker()
        return
    def start_convo(self, user):
        LOGGER.debug("Starting conversation with %s" % user)
        info = {"type": "public", "user" : user, "timestamp":now(), "timeout" : self.giveup}
        self.convos[user] = OneStart(info)
        self.convo_type[user] = info["type"]
        self.update_convo(info)
        return
    def maybe_start_convo(self):
        # Randomly Decide if we will
        options = [True, False]
        start_convo = random.choice(options, p=[1.00, 0.00])
        if start_convo:
            current_users = []
            self.get_users()
            current_users = ["test__"]
            no_convo_users = [u for u in current_users if u not in self.convos]
            user = None
            if no_convo_users and len(no_convo_users):
                user = random.choice(no_convo_users)
            if user:
                self.start_convo(user)
            else:
                LOGGER.debug("No one to start a conversation with")
        else:
            #LOGGER.debug("Not starting a conversation with anyone")
            pass
        return
    def send_message(self, info, msg, user = None):
        if "public" == info["type"]:
            # Public messages are sent to the channel
            if user:
                msg = "%s: %s" % (user, msg)
            self.connection.notice(self.channel, msg)
        elif "private" == info["type"]:
            # Private messages go to the user themself
            self.connection.notice(info["target"], msg)
    def check_convos(self):
        LOGGER.debug("Checking conversations")
        for user in [u for u in self.convos]:
            info  = {"type" : self.convo_type[user], "user" : user, "timestamp" : now(), "timeout" : self.giveup}
            if self.convos[user].is_timedout(info):
                self.update_convo(info)
        return
    def update_convo(self, info):
        user = info["user"]
        # Get Current State
        cur_state = self.convos[user]
        LOGGER.debug("Current State:%s" % cur_state)

        # Transition to next state
        cur_state = cur_state.next(info)
        LOGGER.debug("New State:%s" % cur_state)

        # Run State (Get Message)
        outgoing_messages = cur_state.run()
        LOGGER.debug("Outgoing Message:%s" % outgoing_messages)

        # Update
        self.convos[user] = cur_state
        for msg in outgoing_messages:
            if msg:
                self.send_message(info, msg, user)
        if cur_state.name in self.over_states:
            LOGGER.debug("Removing conversation for %s" % user)
            del self.convos[user]
            del self.convo_type[user]
        return
    def handle_msg(self, msg, info):
        if info["intention"] == self.get_nickname():
            # Someone's talking to me
            LOGGER.debug("%s's talking to me" % info["user"])
            if info["text"] in self.commands:
                self.command(info)
                return
            user = info["user"]
            # Initialize Conversation
            if user not in self.convos:
                LOGGER.debug("Starting new conversation with %s" % user)
                self.convos[user] = TwoStart(info)
                self.convo_type[user] = info["type"]
            self.update_convo(info)
        else:
            # Probably a general message
            pass
        return

def main():
    # ARGUMENTS
    parser = get_argparser()
    parser.add_argument("-d", "--debug",
            action = "store_true",
            default = False,
            help = "set console logging output to DEBUG")
    args = parser.parse_args()
    server, port, channel, nickname = get_irc_args(args)
    # Debug
    if args.debug:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug("DEBUG logging on")
    LOGGER.info("Server  : %s" % server)
    LOGGER.info("Port    : %s" % port)
    LOGGER.info("Channel : %s" % channel)
    LOGGER.info("Nickname: %s" % nickname)

    # BOT
    giveup = 10
    bot = ChatBot(channel, nickname, server, port, giveup)
    bot.start()
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
