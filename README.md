Limnoria Mumble
================

This is a mumble server interface for supybot/limnoria. It can mirror text conversations from
the mumble server and tell you when people on mumble come and go.


How to use:
-----------

This plugin connects to a Mumble server (murmur) via ZeroC Ice and monitors its
status as well provides the ability to send messaged directly to channels/users
on the Mumble server.

Refer to http://mumble.sourceforge.net/Ice how configure murmur to use Ice.

You may need to modify Mumble/plugin.py at the top, the path to Murmur.ice

Then:
!load Mumble
!config plugins.mumble.announceChannels #yourmumbleircchannel
!config plugins.mumble.mumbleSecret yoursecret 
!config plugins.mumble.serverIp 127.0.0.1
!config plugins.mumble.serverPort 6502

then !reload Mumble


