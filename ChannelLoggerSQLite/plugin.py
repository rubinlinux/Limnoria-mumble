###
# Copyright (c) 2002-2004, Jeremiah Fincher
# Copyright (c) 2009-2010, James McCoy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import sqlite3
import os

import supybot.conf as conf
import supybot.world as world
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.irclib as irclib
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('ChannelLoggerSQLite')

class FakeLog(object):
    def flush(self):
        return
    def close(self):
        return
    def write(self, s):
        return

class ChannelLoggerSQLite(callbacks.Plugin):
    noIgnore = True
    def __init__(self, irc):
        self.__parent = super(ChannelLoggerSQLite, self)
        self.__parent.__init__(irc)
        self.lastMsgs = {}
        self.lastStates = {}
        self.logDir = self.getLogDir(irc)
        self.logName = 'log.db'
        self.log = os.path.join(self.logDir, self.logName)
        self.logconn = sqlite3.connect(self.log)
        
        with self.logconn:

            cur = self.logconn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS Log (
                  Time        timestamp default CURRENT_TIMESTAMP,
                  Channel     varchar(255),
                  Nick        varchar(255),
                  Action      varchar(255),
                  Msg         text);''')

    def die(self):
        return
       
    def __call__(self, irc, msg):
        try:
            # I don't know why I put this in, but it doesn't work, because it
            # doesn't call doNick or doQuit.
            # if msg.args and irc.isChannel(msg.args[0]):
            self.__parent.__call__(irc, msg)
            if irc in self.lastMsgs:
                if irc not in self.lastStates:
                    self.lastStates[irc] = irc.state.copy()
                self.lastStates[irc].addMsg(irc, self.lastMsgs[irc])
        finally:
            # We must make sure this always gets updated.
            self.lastMsgs[irc] = msg

    def reset(self):
        self.lastMsgs.clear()
        self.lastStates.clear()

    def getLogDir(self, irc):
        logDir = conf.supybot.directories.log.dirize(self.name())
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        return logDir

    def getLog(self, irc):
        return
      
    def doLog(self, irc, sqlite_data, channel):
        if not self.registryValue('enable', channel):
            return
        if len(sqlite_data) == 4:
  
            with self.logconn:
                cur = self.logconn.cursor()

                data = (sqlite_data['channel'], sqlite_data['nick'], sqlite_data['action'], sqlite_data['msg'])
                cur.execute('INSERT INTO Log VALUES(CURRENT_TIMESTAMP, ?, ?, ?, ?)', data)

    def doPrivmsg(self, irc, msg):
        (recipients, text) = msg.args
        for channel in recipients.split(','):
            if irc.isChannel(channel):
                noLogPrefix = self.registryValue('noLogPrefix', channel)
                action = 'PRIVMSG'
                if noLogPrefix and text.startswith(noLogPrefix):
                    text = '-= THIS MESSAGE NOT LOGGED =-'
                nick = msg.nick or irc.nick
                if ircmsgs.isAction(msg):
                    action = 'ACTION'
                    text = '{} {}'.format(nick, ircmsgs.unAction(msg))
                    
                sqlite_data = {
                    'channel': channel,
                    'nick': msg.nick,
                    'action': action,
                    'msg': text }
                    
                self.doLog(irc, sqlite_data, channel)

    def doNotice(self, irc, msg):
        (recipients, text) = msg.args
        for channel in recipients.split(','):
            if irc.isChannel(channel):
                sqlite_data = {
                    'channel': channel,
                    'nick': msg.nick,
                    'action': msg.command,
                    'msg': text }
                self.doLog(irc, sqlite_data, channel)

    def doNick(self, irc, msg):
        oldNick = msg.nick
        newNick = msg.args[0]
        for (channel, c) in list(irc.state.channels.items()):
            if newNick in c.users:
                sqlite_data = {
                    'channel': channel,
                    'nick': oldNick,
                    'action': msg.command,
                    'msg': '{} is now known as {}'.format(oldNick, newNick) }
                self.doLog(irc, sqlite_data, channel)
                
    def doJoin(self, irc, msg):
        for channel in msg.args[0].split(','):
            if(self.registryValue('showJoinParts', channel)):
                sqlite_data = {
                    'channel': channel,
                    'nick': msg.nick,
                    'action': 'JOIN',
                    'msg': '{} <{}> has joined {}'.format(msg.nick, msg.prefix, channel) }
                self.doLog(irc, sqlite_data, channel)

    def doKick(self, irc, msg):
        if len(msg.args) == 3:
            (channel, target, kickmsg) = msg.args
        else:
            (channel, target) = msg.args
            kickmsg = ''
        if kickmsg:
            text = '{} was kicked by {} ({})'.format(target, msg.nick, kickmsg)
        else:
            text = '{} was kicked by {}'.format(target, msg.nick)

        sqlite_data = {
                'channel': channel,
                'nick': msg.nick,
                'action': msg.command,
                'msg': text }
        self.doLog(irc, sqlite_data, channel)
            

    def doPart(self, irc, msg):
        if len(msg.args) > 1:
            reason = " ({})".format(msg.args[1])
        else:
            reason = ""
        for channel in msg.args[0].split(','):
            if(self.registryValue('showJoinParts', channel)):
                sqlite_data = {
                    'channel': channel,
                    'nick': msg.nick,
                    'action': msg.command,
                    'msg': '{} <{}> has left {}{}'.format(msg.nick, msg.prefix, channel, reason) }
                self.doLog(irc, sqlite_data, channel)

    def doMode(self, irc, msg):
        channel = msg.args[0]
        if irc.isChannel(channel) and msg.args[1:]:
            sqlite_data = {
                'channel': channel,
                'nick': msg.nick or msg.prefix,
                'action': msg.command,
                'msg': '{} sets mode: {} {}'.format(msg.nick or msg.prefix, msg.args[1],' '.join(msg.args[2:])) }
            self.doLog(irc, sqlite_data, channel)

    def doTopic(self, irc, msg):
        if len(msg.args) == 1:
            return # It's an empty TOPIC just to get the current topic.
        channel = msg.args[0]
        sqlite_data = {
            'channel': channel,
            'nick': msg.nick,
            'action': msg.command,
            'msg': '{} changes topic to "{}"'.format(msg.nick, msg.args[1]) }
        self.doLog(irc, sqlite_data, channel)

    def doQuit(self, irc, msg):
        if len(msg.args) == 1:
            reason = " (%s)" % msg.args[0]
        else:
            reason = ""
        if not isinstance(irc, irclib.Irc):
            irc = irc.getRealIrc()
        for (channel, chan) in list(self.lastStates[irc].channels.items()):
            if(self.registryValue('showJoinParts', channel)):
                if msg.nick in chan.users:
                    sqlite_data = {
                        'channel': channel,
                        'nick': msg.nick,
                        'action': msg.command,
                        'msg': ' {} <{}> has quit IRC{}'.format(msg.nick, msg.prefix, reason) }
                    self.doLog(irc, sqlite_data, channel)

    def outFilter(self, irc, msg):
        # Gotta catch my own messages *somehow* :)
        # Let's try this little trick...
        if msg.command in ('PRIVMSG', 'NOTICE'):
            # Other messages should be sent back to us.
            m = ircmsgs.IrcMsg(msg=msg, prefix=irc.prefix)
            self(irc, m)
        return msg


Class = ChannelLoggerSQLite
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
