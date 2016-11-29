#! /usr/bin/env python3

import sys
import os
from argparse import ArgumentParser

# Logging
import logging
from logging import handlers
LOGGER = logging.getLogger(__file__)
SH = logging.StreamHandler()
FH = logging.handlers.RotatingFileHandler("irc.log", maxBytes=5 * 1000000, backupCount = 5)
SH.setFormatter(logging.Formatter("%(message)s"))
FH.setFormatter(logging.Formatter("%(asctime)s:%(lineno)s:%(funcName)s:%(levelname)s:%(message)s"))
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(SH)
LOGGER.addHandler(FH)

import irc
import irc.bot
from irc.bot import SingleServerIRCBot

import datetime

NICK_SUFF = "-bot"
DEF_PORT = 6667
def get_argparser():
    parser = ArgumentParser()
    parser.add_argument(
            dest="server",
            metavar = "server[:port]",
            help="server URL and optional port number, delimited by a colon ':'")
    parser.add_argument(
            dest="channel",
            metavar = "[#]channel",
            help="channel to connect to ('#' will be prepended if omitted)")
    parser.add_argument(
            dest="nickname",
            metavar = "nickname[%s]" % NICK_SUFF,
            help="desired nickname in the chat ('%s' will be appended if omitted)" % NICK_SUFF)
    return parser

class IRCBot(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        super().__init__([(server, port)], nickname, nickname)
        self.channel = channel

    def get_nickname(self):
        return self.connection.get_nickname()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        e.__dict__["timestamp"] = datetime.datetime.now()
        self.handle_msg(e)
        return

    def on_pubmsg(self, c, e):
        e.__dict__["timestamp"] = datetime.datetime.now()
        self.handle_msg(e)
        return
    def handle_msg(self, msg):
        info = self.get_msg_data(msg)
        LOGGER.info("%s-[%s] <%s> %s" %
                (info["type"].upper(),
                    info["timestamp"].strftime("%H:%M"),
                    info["source"],info["msg"])
                )
        self.update_state(msg, info)
        return
    def update_state(self, msg, input):
        if input["intention"] == self.get_nickname():
            self.do_command(msg, input["text"])
        return
    def do_command(self, e, input):
        cmd = input["text"]
        nick = input["source"]
        c = self.connection
        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die("ugh fine bye")
        elif cmd == "stats":
            print("CHANNELS:%s" % self.channels.items())
            for chname, chobj in self.channels.items():
                users   = sorted(chobj.users())
                opers   = sorted(chobj.opers())
                voiced  = sorted(chobj.voiced())
                owners  = sorted(chobj.owners())
                halfops = sorted(chobj.halfops())
                admins  = sorted(chobj.admins())
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: %s" % chname)
                c.notice(nick, "Users  : %s" % ", ".join(users))
                c.notice(nick, "Opers  : %s" % ", ".join(opers))
                c.notice(nick, "Voiced : %s" % ", ".join(voiced))
                c.notice(nick, "Owners : %s" % ", ".join(owners))
                c.notice(nick, "Halfops: %s" % ", ".join(halfops))
                c.notice(nick, "Admins : %s" % ", ".join(admins))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        else:
            c.notice(nick, "Not understood: " + cmd)
    def get_msg_data(self, msg):
        info = {}
        # TIME
        info["timestamp"] = msg.__dict__["timestamp"]
        # TYPE
        type = msg.type
        if type == "pubmsg":
            info["type"] = "public"
        elif type == "privmsg":
            info["type"] = "private"
        else:
            info["type"] = "other"
        # SOURCE
        source = msg.source.split("!", 1)
        info["source"] = source[0]
        info["source_info"] = source[1]
        # TARGET
        target = msg.target
        info["target"] = target
        # INTENTION AND MESSAGE
        text = msg.arguments[0].split(":", 1)
        intention = None
        message = None
        if len(text) > 1:
            intention = text[0].strip()
            message = text[1].strip()
        else:
            message = text[0].strip()
        info["intention"] = intention
        info["text"] = message
        info["msg"] = msg.arguments[0].strip()
        return info
    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

def main():
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
    bot = IRCBot(channel, nickname, server, port)
    bot.start()
    return 0

if __name__ == "__main__":
    rtn = main()
    sys.exit(rtn)
