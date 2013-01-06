###
# Copyright (c) 2005, Jeremiah Fincher
# Copyright (c) 2009, James McCoy
# Copyright (c) 2013, Alexander Minges
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

import supybot.conf as conf
import supybot.registry as registry
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('ChannelLoggerSQLite')

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('ChannelLoggerSQLite', True)

ChannelLoggerSQLite = conf.registerPlugin('ChannelLoggerSQLite')

conf.registerChannelValue(ChannelLoggerSQLite, 'enable',
    registry.Boolean(True, """Determines whether logging is enabled."""))
conf.registerGlobalValue(ChannelLoggerSQLite, 'flushImmediately',
    registry.Boolean(False, """Determines whether channel logfiles will be
    flushed anytime they're written to, rather than being buffered by the
    operating system."""))
conf.registerChannelValue(ChannelLoggerSQLite, 'showJoinParts',
    registry.Boolean(True, """Determines wether joins and parts are logged"""))
conf.registerChannelValue(ChannelLoggerSQLite, 'stripFormatting',
    registry.Boolean(True, """Determines whether formatting characters (such
    as bolding, color, etc.) are removed when writing the logs to disk."""))
conf.registerChannelValue(ChannelLoggerSQLite, 'noLogPrefix',
    registry.String('[nolog]', """Determines what string a message should be
    prefixed with in order not to be logged.  If you don't want any such
    prefix, just set it to the empty string."""))

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
