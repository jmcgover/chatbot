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
    def __init__(self, channel, nickname, server, port=6667):
        super().__init__(channel, nickname, server, port)
        self.convos = None
        self.max_poll_interval = 5
        self.poll_thread = None
        self.reset()
    def reset(self):
        LOGGER.debug("(Re-)Initializing")
        self.convos = {}
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
            source = info["source"]
            state_string = None
            if source in self.convos:
                state_string = "%s" % self.convos[source]
            else:
                state_string = "No conversation with %s yet" % source
            self.send_message(info, state_string)
        return
    def poll(self):
        with self.reactor.mutex:
            self.check_convos()
            self.maybe_start_convo()
            self.start_checker()
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
            LOGGER.debug("Not starting a conversation with anyone")
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
    def start_convo(self, user):
        LOGGER.debug("Starting conversation with %s" % user)
        self.convos[user] = OneStart()

        # Get Current State
        cur_state = self.convos[user]
        LOGGER.debug("Current State:%s" % cur_state)

        # Transition to next state
        info = {"type": "public", "source" : user}
        cur_state = cur_state.next(info)
        LOGGER.debug("New State:%s" % cur_state)

        # Run State (Get Message)
        outgoing_message = cur_state.run()
        LOGGER.debug("Outgoing Message:%s" % outgoing_message)

        # Update
        self.convos[user] = cur_state
        if outgoing_message:
            self.send_message(info, outgoing_message, user)
        if "START" == cur_state or "END" == cur_state:
            LOGGER.debug("Removing conversation for %s" % user)
            self.convos.pop(user, None)
        return
    def check_convos(self):
        LOGGER.debug("Checking conversations")
        return
    def handle_msg(self, msg, info):
        outgoing_message = None
        if info["intention"] == self.get_nickname():
            # Someone's talking to me
            LOGGER.debug("%s's talking to me" % info["source"])
            if info["text"] in self.commands:
                self.command(info)
                return
            source = info["source"]

            # Initialize Conversation
            if source not in self.convos:
                LOGGER.debug("Starting new conversation with %s" % source)
                self.convos[source] = TwoStart()

            # Get Current State
            cur_state = self.convos[source]
            LOGGER.debug("Current State:%s" % cur_state)

            # Transition to next state
            cur_state = cur_state.next(info)
            LOGGER.debug("New State:%s" % cur_state)

            # Run State (Get Message)
            outgoing_message = cur_state.run()
            LOGGER.debug("Outgoing Message:%s" % outgoing_message)

            # Update
            self.convos[source] = cur_state
            if outgoing_message:
                self.send_message(info, outgoing_message)
            if "START" == cur_state or "END" == cur_state:
                LOGGER.debug("Removing conversation for %s" % source)
                self.convos.pop(source, None)
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
    bot = ChatBot(channel, nickname, server, port)
    bot.start()
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
