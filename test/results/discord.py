# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import discord


__tests__ = (
{
    "#url"     : "https://discord.com/channels/302094807046684672/1306705919916249098",
    "#category": ("", "discord", "channel"),
    "#class"   : discord.DiscordChannelExtractor,
#    # access token & access to minecraft server required for this test (REMEMBER TO REMOVE TOKEN BEFORE COMMITTING)
#    "#range"   : "1-2",
#    "#count"   : 2,
#    "#options" : {"token": ""},
#
#    "#server"       : "MINECRAFT",
#    "#server_id"    : "302094807046684672",
#    "#server_files" : list,
#    "#owner_id"     : "827254075857829920",
#    "#channel"      : str,
#    "#channel_id"   : str,
#    "#channel_type" : 11,
#    "#channel_topic": str,
#    "#parent"       : "challenges",
#    "#parent_id"    : "1306705919916249098",
#    "#parent_type"  : 15,
#    "#is_thread"    : True,
#
#    "author"      : str,
#    "author_id"   : str,
#    "author_files": list,
#    "message"     : str,
#    "message_id"  : str,
#    "type"        : str,
#    "date"        : "type:datetime",
#    "files"       : list,
#    "filename"    : str,
#    "extension"   : str,
#    "num"         : int,
},

{
    "#url"     : "https://discord.com/channels/302094807046684672/1306705919916249098/threads/1306706528786583623",
    "#category": ("", "discord", "channel"),
    "#class"   : discord.DiscordChannelExtractor,
},

{
    "#url"     : "https://discord.com/channels/302094807046684672",
    "#category": ("", "discord", "server"),
    "#class"   : discord.DiscordServerExtractor,
},

{
    "#url"     : "https://discord.com/channels/@me/302094807046684672",
    "#category": ("", "discord", "direct-messages"),
    "#class"   : discord.DiscordDirectMessagesExtractor,
},

)
