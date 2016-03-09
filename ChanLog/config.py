###
# Copyright (c) 2007, Jochen Ritzel
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

class Logger(registry.OnlySomeStrings):
    validStrings = [ "file", "sqlalchemy" ]

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('ChanLog', True)
    
       
ChanLog = conf.registerPlugin('ChanLog')


## general settings
conf.registerChannelValue(ChanLog, 'noLogPrefix',
    registry.String('[nolog]', """Determines what string a message should be
    prefixed with in order not to be logged.  If you don't want any such
    prefix, just set it to the empty string."""))
    
conf.registerChannelValue(ChanLog, 'stripFormatting',
    registry.Boolean(True, """Determines whether formatting characters (such
    as bolding, color, etc.) are removed when writing the logs to disk."""))

## SA Settings

conf.registerGlobalValue(ChanLog, 'SQLAlchemy',
    registry.Boolean(False, """Log to a databse using SQLAlchemy"""))
conf.registerGlobalValue(ChanLog.SQLAlchemy, 'URI',
    registry.String("", """The URI of your database in the form: scheme://[user[:password]@]host[:port]/database[?parameters]
Examples:
mysql://user:password@host/database
mysql://host/database?debug=1
postgres://user@host/database?debug=&cache=
postgres:///full/path/to/socket/database
postgres://host:5432/database
sqlite:///full/path/to/database
sqlite:/C|/full/path/to/database
sqlite:/:memory:
    """,private=True))


## File log stuff
conf.registerGlobalValue(ChanLog, 'File',
    registry.Boolean(True, """Log to a file"""))
conf.registerGlobalValue(ChanLog.File, 'flushImmediately',
    registry.Boolean(False, """Determines whether channel logfiles will be
    flushed anytime they're written to, rather than being buffered by the
    operating system."""))
conf.registerChannelValue(ChanLog.File, 'timestamp',
    registry.Boolean(True, """Determines whether the logs for this channel are
    timestamped with the timestamp in supybot.log.timestampFormat."""))
conf.registerChannelValue(ChanLog.File, 'rotateLogs',
    registry.Boolean(False, """Determines whether the bot will automatically
    rotate the logs for this channel.  The bot will rotate logs when the
    timestamp for the log changes.  The timestamp is set according to
    the 'filenameTimestamp' configuration variable."""))
conf.registerChannelValue(ChanLog.File, 'filenameTimestamp',
    registry.String('%d-%a-%Y', """Determines how to represent the timestamp
    used for the filename in rotated logs.  When this timestamp changes, the
    old logfiles will be closed and a new one started. The format characters
    for the timestamp are in the time.strftime docs at python.org.  In order
    for your logs to be rotated, you'll also have to enable
    supybot.plugins.ChanLog.rotateLogs."""))

conf.registerGlobalValue(ChanLog.File, 'directories',
    registry.Boolean(True, """Determines whether the bot will partition its
    channel logs into separate directories based on different criteria."""))
conf.registerGlobalValue(ChanLog.File.directories, 'network',
    registry.Boolean(True, """Determines whether the bot will use a network
    directory if using directories."""))
conf.registerGlobalValue(ChanLog.File.directories, 'channel',
    registry.Boolean(True, """Determines whether the bot will use a channel
    directory if using directories."""))
conf.registerGlobalValue(ChanLog.File.directories, 'timestamp',
    registry.Boolean(False, """Determines whether the bot will use a timestamp
    (determined by supybot.plugins.ChanLog.directories.timestamp.format)
    if using directories."""))
conf.registerGlobalValue(ChanLog.File.directories.timestamp, 'format',
    registry.String('%B', """Determines what timestamp format will be used in
    the directory stucture for channel logs if
    supybot.plugins.ChanLog.directories.timestamp is True."""))

