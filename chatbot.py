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
SH.setFormatter(logging.Formatter("%(message)s"))
FH.setFormatter(logging.Formatter("%(asctime)s:%(lineno)s:%(funcName)s:%(levelname)s:%(message)s"))
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(SH)
LOGGER.addHandler(FH)

import ircserver
from ircserver import get_argparser
from ircserver import DEF_PORT
from ircserver import NICK_SUFF
from ircserver import IRCBot

class ChatBot(IRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        super().__init__(channel, nickname, server, port)
    def update_state(self, msg, info):
        print("FUCKAAAAAA: %s" % info)


def main():
    # ARGUMENTS
    parser = get_argparser()
    args = parser.parse_args()
    server_port = args.server.split(":")
    server = server_port[0]
    port = int(server_port[1]) if len(server_port) > 1 else DEF_PORT
    channel = args.channel if args.channel[0] == "#" else "#" + args.channel
    nickname = args.nickname if args.nickname[-4:] == NICK_SUFF else args.nickname + NICK_SUFF
    print("Server  : %s" % server)
    print("Port    : %s" % port)
    print("Channel : %s" % channel)
    print("Nickname: %s" % nickname)

    # BOT
    bot = ChatBot(channel, nickname, server, port)
    bot.start()
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
