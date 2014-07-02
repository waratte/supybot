###
# Copyright (c) 2014, Wekeden
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

# Standard modules
import random
import time
import os
import re
import commands

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Cobe')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

# Additional supybot modules
import supybot.ircmsgs as ircmsgs
import supybot.conf as conf

# Custom modules imported    
try:
    from cobe.brain import Brain
except ImportError:
    raise callbacks.Error, 'You need to install cobe for this plugin to work!'
try:
    import chardet
except ImportError:
    raise callbacks.Error, 'You need to install chardet for this plugin to work!'
    
class Cobe(callbacks.Plugin):
    """
    Cobe is frontend to the cobe markov-chain bot for Limnoria/supybot. Use "list Cobe" to list possible
    commands and "help Cobe <command>" to read their docs.
    """
    threaded = True
    brains = {}
    brainDirectories = {}
    
    def __init__(self, irc):
        self.__parent = super(Cobe, self)
        self.__parent.__init__(irc)
        
    def _doCommand(self, channel):
        """Internal method for accessing a cobe brain."""
        
        dataDirectory = conf.supybot.directories.data
        dataDirectory = dataDirectory.dirize(channel.lower() + "/cobe.brain")
        
        return 'cobe --brain %s' % dataDirectory
        
    def _decodeIRCMessage(self, raw, preferred_encs = ["UTF-8", "CP1252", "ISO-8859-1"]):
        """Internal method for decoding IRC messages."""

        changed = False
        for enc in preferred_encs:
            try:
                res = raw.decode(enc)
                changed = True
                break
            except:
                pass
        if not changed:
            try:
                enc = chardet.detect(raw)['encoding']
                res = raw.decode(enc)
            except:
                res = raw.decode(enc, 'ignore')
                
        return res

    def _cleanText(self, text):
        """Internal method for cleaning text of imperfections."""
        
        text = self._decodeIRCMessage(text)         # Decode the string.
        text = ircutils.stripFormatting(text)       # Strip IRC formatting from the string.
        text = text.strip()                         # Strip whitespace from beginning and the end of the string.
        text = text[0].upper() + text[1:]           # Capitalize first letter of the string.
        text = utils.str.normalizeWhitespace(text)  # Normalize the whitespace in the string.
        
        return text
        
    def _learn(self, irc, channel, text, probability):
        """Internal method for learning phrases."""
        
        if not channel: # Did the user enter in a channel? If not, set the currect channel
        
            channel = msg.args[0]
            
        if not irc.isChannel(channel): # Are we in a channel?
            if self.brainDirectories.has_key(channel) and os.path.exists(self.brainDirectories[channel]):
                # Does this channel have a directory for the brain file stored and does this file exist?
                
                text = self._cleanText(text)
                
                if text and len(text) > 1 and not text.isspace():
            
                    self.brains[channel].learn(text)
                    
                self._reply(irc, channel, text)
                    
            else: # Nope, let's make it!
            
                brainDirectory = conf.supybot.directories.data
                self.brainDirectories[channel] = brainDirectory.dirize(channel.lower() + "/cobe.brain")
                
                commands.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
                
                self.brains[channel] = Brain(self.brainDirectories[channel])
                
                text = self._cleanText(text)
                
                if text and len(text) > 1 and not text.isspace():
            
                    self.brains[channel].learn(text)
                    
                    self._reply(irc, channel, text)
                
        else: # We are in a channel!
            if self.brainDirectories.has_key(channel) and os.path.exists(self.brainDirectories[channel]):
                # Does this channel have a directory for the brain file stored and does this file exist?
                
                text = self._cleanText(text)
                
                if text and len(text) > 1 and not text.isspace():
            
                    self.brains[channel].learn(text)
                    
                    if random.randint(0, 10000) < probability: 
                        # Precision up into the 0.01%!
                        
                        self._reply(irc, channel, text)
                    
            else: # Nope, let's make it!
            
                brainDirectory = conf.supybot.directories.data
                self.brainDirectories[channel] = brainDirectory.dirize(channel.lower() + "/cobe.brain")
                
                commands.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
                
                self.brains[channel] = Brain(self.brainDirectories[channel])
                
                text = self._cleanText(text)
                
                if text and len(text) > 1 and not text.isspace():
            
                    self.brains[channel].learn(text)
                    
                    if random.randint(0, 10000) < probability: 
                        # Precision up into the 0.01%!
                        
                        self._reply(irc, channel, text)
            
    def _reply(self, irc, channel, text):
        """Send a respone to text"""
        
        self.log.info("Attempting to respond in %s with message: %s" % channel, text)
        response = self.brains[channel].reply(text).encode('utf-8')
        # delay the response here so we look real?
        if self.registryValue('responseDelay', channel):
            self.log.info("Delayed the response in %s." % channel)
            delayseconds = time.time() + random.randint(2, 5)
            schedule.addEvent((irc.queueMsg(ircmsgs.privmsg(channel, response))), delayseconds)
        else:
            irc.queueMsg(ircmsgs.privmsg(channel, response))
            
    def doPrivmsg(self, irc, msg):
        channel = msg.args[0].lower()
        text = msg.args[1].strip()
        # if txt.startswith(conf.supybot.reply.whenAddressedBy.chars()):
        if (not ircmsgs.isCtcp(msg) 
           or not ircmsgs.isAction(msg) 
           or irc.isChannel(channel)
           or not re.match(self.registryValue('ignoreRegex'), text)):
            # Only reacts to message in a channel, while ignoring CTCP, actions, and matching regex

            if self.registryValue('stripUrls'): # strip URLs 
                text = re.sub(r'(http[^\s]*)', '', text)
            
            if re.match( irc.nick, text, re.I): 
                # Were we addressed in the channel?
                
                probability = self.registryValue('probabilityWhenAddressed', channel)
                
            else: 
                # Okay, we were not addressed, but what's the probability we should reply?
                
                probability = self.registryValue('probability', channel)

            if self.registryValue('stripNicks'):
                removenicks = '|'.join(item + '\W.*?\s' for item in irc.state.channels[channel].users)
                text = re.sub(r'' + removenicks + '', 'MAGIC_NICK', text)
            
            self._learn(irc, channel, text, probability) # Now we can pass this to our learn function!
            
    def _makeSizePretty(self, size):
        """Internal command for making the size pretty!"""
        suffixes = [("Bytes",2**10), ("Kibibytes",2**20), ("Mebibytes",2**30), ("Gibibytes",2**40), ("Tebibytes",2**50)]
        for suf, lim in suffixes:
            if size > lim:
                continue
            else:
                return round(size/float(lim/2**10),2).__str__()+suf
            
    def size(self, irc, msg, args, channel):
        """[<channel>]
        
        Prints the size of the brain on disk. If <channel> is not given, then the current channel is used.
        """

        if not channel: # Did the user enter in a channel? If not, set the currect channel
            channel = msg.args[0]

        if not irc.isChannel(channel): # Are we in a channel?
            if os.path.exists(self.brainDirectories[channel]):
                # Does this channel have a brain file?
                
                size = float(os.path.getsize(self.brainDirectories[channel]))
                irc.reply("The brain file for channel {0} is {1}.".format(channel, self._makeMakePretty(size)))
                
            else: # Nope, raise error msg!
                irc.error(_("I am missing a brainfile in {0}!".format(channel)), Raise=True)
                
        elif os.path.exists(self.brainDirectories[channel]): # We are in a channel! Does the brain file exist?
        
            size = float(os.path.getsize(self.brainDirectories[channel]))
            irc.reply("The brain file for channel {0} is {1}.".format(channel, self._makeMakePretty(size)))
            
        else:
            
            irc.error(_("I am missing a brainfile in {0}!".format(channel)), Raise=True)

    size = wrap(size, [additional('channel')])
    
    def learn(self, irc, msg, args, channel, text):
        """[<channel>] <text>

        Teaches the bot <text>. If the channel is not given, the current channel is used.
        """
        if not channel: # Did the user enter in a channel? If not, set the current channel
            channel = msg.args[0]

        if not irc.isChannel(msg.args[0]) and irc.isChannel(channel): 
            # Are we in a channel and is the channel supplied a channel?
            if not self.brainDirectories.has_key(channel):
                # If this dictionary does not have the channel, let's make it!
                brainDirectory = conf.supybot.directories.data
                self.brainDirectories[channel] = brainDirectory.dirize(channel.lower() + "/cobe.brain")
            
            if os.path.exists(self.brainDirectories[channel]):
                # Does this channel have a brain file?
                
                if not self.brains.has_key(channel):
                    # Making sure the key-value was set
                    self.brains[channel] = Brain(self.brainDirectories[channel])
                    
                text = self._cleanText(text)
                if text and len(text) > 1 and not text.isspace():
            
                    irc.reply("Learning text: {0}".format(text))
                    self.brains[channel].learn(text)
                    
                else:
        
                    irc.error(_("No text to learn!"), Raise=True)
                    
            else: 
                # Nope, create one!
            
                self.log.info("Non-existent brainfile in {0}!".format(channel))
                self.log.info("Creating a brainfile now in {1}".format(self.brainDirectories[channel]))
                
                commands.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
                self.brains[channel] = Brain(self.brainDirectories[channel]) # Setting key-value, just to make sure
                
                text = self._cleanText(text)
                if text and len(text) > 1 and not text.isspace():
            
                    irc.reply("Learning text: {0}".format(text))
                    self.brains[channel].learn(text)
                
                
        elif os.path.exists(self.brainDirectories[channel]) and irc.isChannel(channel): 
            # We are in a channel! Does the brain file exist and is this a channel?
    
            text = self._cleanText(text)
            if text and len(text) > 1 and not text.isspace():
        
                irc.reply("Learning text: {0}".format(text))
                self.brains[channel].learn(text)
        
            else:
        
                irc.error(_("No text to learn!"), Raise=True)
                
        else:
            irc.error(_("Improper channel given!"), Raise=True)
            
    learn = wrap(learn, [('checkCapability', 'admin'), additional('channel'), 'text'])

    def reply(self, irc, msg, args, text):
        """[<channel>] <text>

        Replies to <text>. If the channel is not given, the current channel is used.
        """
        if not channel: # Did the user enter in a channel? If not, set the current channel
            channel = msg.args[0]

        if not irc.isChannel(msg.args[0]) and irc.isChannel(channel): 
            # Are we in a channel and is the channel supplied a channel?
            if not self.brainDirectories.has_key(channel):
                # If this dictionary does not have the channel, let's make it!
                brainDirectory = conf.supybot.directories.data
                self.brainDirectories[channel] = brainDirectory.dirize(channel.lower() + "/cobe.brain")
            
            if os.path.exists(self.brainDirectories[channel]):
                # Does this channel have a brain file?
                
                if not self.brains.has_key(channel):
                    # Making sure the key-value was set
                    self.brains[channel] = Brain(self.brainDirectories[channel])
                    
		text = self._cleanText(text)
		if text and len(text) > 1 and not text.isspace():
	
			response = brains[channel].reply(text).encode('utf-8')
			irc.reply(response)

                else:
        
                    irc.error(_("No text to reply to!"), Raise=True)
                    
            else: 
                # Nope, create one!
            
                self.log.info("Non-existent brainfile in {0}!".format(channel))
                self.log.info("Creating a brainfile now in {1}".format(self.brainDirectories[channel]))
                
                commands.getoutput('{0} {1}'.format(self._doCommand(channel), 'init'))
                self.brains[channel] = Brain(self.brainDirectories[channel]) # Setting key-value, just to make sure
                
		text = self._cleanText(text)
		if text and len(text) > 1 and not text.isspace():
	
			response = brains[channel].reply(text).encode('utf-8')
			irc.reply(response)
                
        elif os.path.exists(self.brainDirectories[channel]) and irc.isChannel(channel): 
            # We are in a channel! Does the brain file exist and is this a channel?
    
		text = self._cleanText(text)
		if text and len(text) > 1 and not text.isspace():
	
			response = brains[channel].reply(text).encode('utf-8')
			irc.reply(response)

	        else:
	      		irc.error(_("No text to reply to!"), Raise=True)
                
        else:
            irc.error(_("Improper channel given!"), Raise=True)
            
    reply = wrap(reply, [('checkCapability', 'admin'), additional('channel'), 'text'])
    
Class = Cobe


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: