# BattleriteBot - Made by Remilia (discord Megumi#0001)

import discord
from discord.ext import commands
import asyncio
import random
import os
from operator import or_
from functools import reduce

import battleritebot.parser as parser
from battleritebot.player import Player
from battleritebot.message import Message
from battleritebot.match import Match
from battleritebot.match_result import MatchResult

_VERSION = "0.1"
_3V3 = 2
_2V2 = 1
_1V1 = 0

print("Started BattleriteBot Version " + _VERSION + "\n")

channels = {}
players = {}
usernameLookup = {}
messages = {}
matches = []
queue1v1 = []
queue2v2 = []
queue3v3 = []

# Load Files

assert(os.path.exists("config"))
assert(os.path.exists("config\\config.txt"))

try:
    config = parser.read("config\\config.txt")
    config["channels"] = list(map(int, config["channels"]))
    config["matchfeed"] = int(config["matchfeed"])
    config["admins"] = list(map(int, config["admins"]))
    for attr in ["token", "prefix","maps_pool","maps_off_pool"]:
        if attr not in config:
            raise KeyError
except (ValueError, KeyError) as e:
    print("Error in Config File!")
    exit(1)

print("Config loaded.")

if not os.path.exists("players"):
    os.mkdir("players")

loaded_players = 0
for playerFile in parser.list("players"):
    try:
        _playerdata = parser.read("players\\" + playerFile)
        _playerdata["ID"] = int(_playerdata["ID"])
        _playerdata["can_submit"] = bool(_playerdata["can_submit"])
        for q in ["1v1", "2v2", "3v3"]:
            _playerdata[q + "_mmr"] = list(map(int, _playerdata[q + "_mmr"]))
            _playerdata[q + "_matches"] = list(map(int, _playerdata[q + "_matches"]))
            _playerdata[q + "_enabled"] = _playerdata[q + "_enabled"] == "True"
        for attr in ["teams", "titles", "current_title"]:
            if attr not in _playerdata:
                raise KeyError
        players[_playerdata["ID"]] = Player(_playerdata)
        usernameLookup[_playerdata["username"]] = _playerdata["ID"]
        loaded_players += 1
    except (ValueError, KeyError) as e:
        print("Error in Player File: " + playerFile)
        
print(str(loaded_players) + " players loaded.")

if not os.path.exists("matches"):
    os.mkdir("matches")

loaded_matches = 0
for matchFile in parser.list("matches"):
    try:
        _matchdata = parser.read("matches\\" + matchFile)
        for attr in ["submit_by"]:
            _matchdata[attr] = int(_matchdata[attr])
        for attr in ["score", "teamA", "teamB"]:
            _matchdata[attr] = list(map(int, _matchdata[attr]))
        for i in range(len(_matchdata["teamA"])):
            _matchdata[str(_matchdata["teamA"][i])] = list(map(int, _matchdata[str(_matchdata["teamA"][i])]))
        for i in range(len(_matchdata["teamB"])):
            _matchdata[str(_matchdata["teamB"][i])] = list(map(int, _matchdata[str(_matchdata["teamB"][i])]))
        result = MatchResult(_matchdata)
        result.set_id(int(matchFile[:-4]))
        for attr in ["time"]:
            if attr not in _matchdata:
                raise KeyError
        matches.append(result)
        loaded_matches += 1
    except (ValueError, KeyError) as e:
        print("Error in Match File: " + matchFile)

print(str(loaded_matches) + " matches loaded.")

print()
print(matches[0])

print("\nConnecting...")

bot = commands.Bot(command_prefix=config["prefix"])
bot.remove_command("help")

# Checks

@bot.check
async def ignore_dms(context):
    return context.guild is not None

@bot.check
async def whitelisted_channel(context):
    return context.channel.id in config["channels"]

async def is_admin(context):
    return context.author.id in config["admins"]

# Helper Functions

def is_player(context):
    return context.author.id in players

def find_players(context, args):
    _IDs = set()
    for mention in context.message.mentions:
        if mention.id in players:
            _IDs.add(mention.id)
    for arg in args:
        if arg in usernameLookup:
            _IDs.add(usernameLookup[arg])
        elif arg.isdigit() and int(arg) in players:
            _IDs.add(int(arg))
    _foundplayers = []
    for player_id in _IDs:
        _foundplayers.append(players[player_id])
    return _foundplayers

def player_has_queue_enabled(player):
    queue_enabled = False
    for queue in player.get_queues():
        if queue == True:
            queue_enabled = True
    return queue_enabled

def leave_queues(player_id):
    if player_id in queue3v3:
        queue3v3.remove(player_id)
    if player_id in queue2v2:
        queue2v2.remove(player_id)
    if player_id in queue1v1:
        queue1v1.remove(player_id)
    
def update_queues(player_id, player_queues, forced = 0):
    leave_queues(player_id)
    if (player_queues[_3V3] == True and forced == 0) or forced == 3:
        queue3v3.append(player_id)
        if len(queue3v3) == 6:
            match_players = []
            for player_id in queue3v3:
                match_players.append(players[player_id])
            for player_id in queue3v3:
                leave_queues(player_id)
            return match_players
    if (player_queues[_2V2] == True and forced == 0) or forced == 2:
        queue2v2.append(player_id)
        if len(queue2v2) == 4:
            match_players = []
            for player_id in queue2v2:
                match_players.append(players[player_id])
            for player_id in queue2v2:
                leave_queues(player_id)
            for player_id in queue2v2:
                leave_queues(player_id)
            return match_players
    if (player_queues[_1V1] == True and forced == 0) or forced == 1:
        queue1v1.append(player_id)
        if len(queue1v1) == 2:
            match_players = []
            for player_id in queue1v1:
                match_players.append(players[player_id])
            for player_id in queue1v1:
                leave_queues(player_id)
            for player_id in queue1v1:
                leave_queues(player_id)
            return match_players
    return []

# Feedback

async def new_player_help(context):
    await context.send(context.message.author.mention + "\nYou must be registered as a player first.\n`!register BattleriteUsername`")

async def player_queue_help(context):
    await context.send(context.message.author.mention + "\nYou must join a queue first.\n`!queuesettings` or `!qs`")

async def incorrect_number_of_args(context, args, maxargs, minargs=0):
    if maxargs == minargs and len(args) != maxargs:
        await context.send(context.message.author.mention + "\nIncorrect number of arguments given (" + str(len(args)) + "). Expected: " + str(maxargs))
        return True
    elif len(args) < minargs:
        await context.send(context.message.author.mention + "\nNot enough arguments given (" + str(len(args)) + "). Expected: " + str(minargs) + "~" + str(maxargs))
        return True
    elif len(args) > maxargs:
        await context.send(context.message.author.mention + "\nToo many arguments given (" + str(len(args)) + "). Expected: " + str(minargs) + "~" + str(maxargs))
        return True
    return False

async def unexpected_args(context):
    await context.send(context.message.author.mention + "\bUnexpected arguments given. Please refer to the syntax listed with the `!help` command.")

async def created_new_player(context, player):
    await context.send(context.message.author.mention + "\nCreated user data for: " + player.get_username() + " (" + str(context.message.author.id) + ")")

async def player_already_exists(context, player):
    await context.send(context.message.author.mention + "\nUser data for: " + player.get_username() + " already exists!")

async def player_not_found(context):
    await context.send(context.message.author.mention + "\nPlayer data not found.")

async def display_queues(context, added_to_queue = False):
    _queue_output = []
    if len(queue3v3) > 0:
        _queue_output.append("3v3 [" + str(len(queue3v3)) + "]: " + ", ".join(map(lambda player_id : players[player_id].username, queue3v3)))
    else:
        _queue_output.append("3v3 [0]") 
    if len(queue2v2) > 0:
        _queue_output.append("2v2 [" + str(len(queue2v2)) + "]: " + ", ".join(map(lambda player_id : players[player_id].username, queue2v2)))
    else:
        _queue_output.append("2v2 [0]") 
    if len(queue1v1) > 0:
        _queue_output.append("1v1 [" + str(len(queue1v1)) + "]: " + ", ".join(map(lambda player_id : players[player_id].username, queue1v1)))
    else:
        _queue_output.append("1v1 [0]")
    if added_to_queue:
        await context.send(context.message.author.mention + " has been added to the queue.\nPlayers in Queue:\n```\n" + "\n".join(_queue_output) + "```")
    else:
        await context.send(context.message.author.mention + "\nPlayers in Queue:\n```\n" + "\n".join(_queue_output) + "```")

# Events

async def get_message(channel, message_id):
    return await channel.fetch_message(message_id)

def is_instanced_channel(channel):
    return channel.id in instances

def is_bot_message(msg):
    return msg.author.id == bot.user.id

def is_bot_event(event):
    return event.user_id == bot.user.id

'''@bot.event
async def on_command_error(context, e):
    pass'''

@bot.event
async def on_ready():
        print("Connected as: " + bot.user.name + " (" + str(bot.user.id) + ")")

        for channel_id in config["channels"]:
            channel = bot.get_channel(channel_id)
            if channel != None and channel_id not in channels:
                channels[channel_id] = channel
                print("Channel: " + channel.guild.name + " #" + channel.name + " (" + str(channel.id) + ")")
        matchfeed = bot.get_channel(config["matchfeed"])
        print("Match Feed: " + matchfeed.guild.name + " #" + matchfeed.name + " (" + str(matchfeed.id) + ")")
        
        print("Ready.")

# Messages

async def send_message(context, message):
    msg = await context.send(message.get_content())
    for reaction in message.get_reactions():
        await msg.add_reaction(reaction)
    message.set_msg(msg)

async def send_match(match):
    msg = await bot.get_channel(config["matchfeed"]).send(match.get_content())
    for reaction in match.get_reactions():
        await msg.add_reaction(reaction)
    match.set_msg(msg)

async def update_message_reacts(message):
    await message.get_msg().clear_reactions()
    for reaction in message.get_reactions():
        await message.get_msg().add_reaction(reaction)
    
async def update_message(message, emoji, member):
    if emoji.name in message.get_reactions():
        if member.id in message.get_users():
            print("Button: " + message.to_button(emoji.name) + " pressed by: " + member.name)
            if message.emoji_pressed(emoji.name, member.id):
                await message.get_msg().edit(content=message.get_content())
                if message.needs_refresh():
                    await update_message_reacts(message)
                    message.set_refresh()

    await message.get_msg().remove_reaction(emoji, member)
    
@bot.event
async def on_raw_reaction_add(event):
    if is_bot_event(event):
        return
    if event.channel_id in channels or event.channel_id == config["matchfeed"]:
        channel = bot.get_channel(event.channel_id)            
        msg = await get_message(channel, event.message_id)
        if not is_bot_message(msg):
            return
        print(str(event.message_id) + " " + str(event.user_id) + " " + event.emoji.name)
        if event.message_id in messages:
            messages[event.message_id].set_msg(msg)
            await update_message(messages[event.message_id], event.emoji, bot.get_user(event.user_id))
            if not messages[event.message_id].is_alive():
                await messages[event.message_id].get_msg().clear_reactions()
                if messages[event.message_id].get_status() == "finish":
                    print("MATCH COMPLETE")
                    result = MatchResult(messages[event.message_id].to_result_data())
                    result.set_id(len(matches)+1)
                    matches.append(result)
                    parser.write_raw("matches\\" + str(result.get_id()) + ".txt", str(result))
                del messages[event.message_id]

async def create_match_pug(match_players_ids):
    match_players = {}
    mentions = []
    for player_id in match_players_ids:
        match_players[player_id] = players[player_id]
        user = bot.get_user(player_id)
        if user != None:
            mentions.append(user.mention)
    match = Match(match_players, mentions)
    match_map = random.choice(config["maps_pool"])
    match.create_pug(match_map)
    return match

# Commands

@bot.command()
async def version(context):
    await context.send("BattleriteBot Version " + str(_VERSION) + "\nRemilia (discord Megumi#0001)")
    
@bot.command()
@commands.check(is_admin)
async def status(context):
    output = []
    for channel_id in channels:
        output.append("[" + channels[channel_id].guild.name + "] " + "#" + channels[channel_id].name + " (" + str(channels[channel_id].id) + ")")
    if len(output) > 0:
        await context.send("```\nChannels:\n" + "\n".join(output) + "```")
    else:
        await context.send("```\nNo Channels initialised.```")

@bot.command()
async def register(context, *args): 
    if await incorrect_number_of_args(context, args, 1, 1):
        return
    if context.message.author.id not in players:
        _playerdata = {"username":args[0], "ID":context.message.author.id}
        players[context.message.author.id] = Player(_playerdata)
        player = players[context.message.author.id]
        await created_new_player(context, player)
        parser.write_raw("players\\" + str(player.get_id()) + ".txt", str(player))
    else:
        await player_already_exists(context, players[context.message.author.id])

@bot.command()
async def profile(context, *args):
    if await incorrect_number_of_args(context, args, 1):
        return
    if len(args) == 0:
        if not is_player(context):
            await new_player_help(context)
            return
        else:
            await context.send("```\n"+str(players[context.message.author.id])+"```")
    else:
        _foundplayers = find_players(context, args)
        if len(_foundplayers) == 1:
            await context.send("```\n"+str(_foundplayers[0])+"```")
        else:
            await player_not_found(context)

@bot.command(aliases = ["q"])
async def queue(context):
    await display_queues(context)

@bot.command(aliases = ["a"])
async def add(context):
    if not is_player(context):
        await new_player_help(context)
        return
    player = players[context.message.author.id]
    if not player_has_queue_enabled(player):
        await player_queue_help(context)
        return
    
    print(player.get_queues())
    match_players = update_queues(player.get_id(), player.get_queues(), int(args[1]))
    if len(match_players) > 0:
        # Match found
        print("MATCH FOUND")
        pass
    else:
        # Display in queue
        print("NO MATCH FOUND")
        await display_queues(context, True)

@bot.command()
@commands.check(is_admin)
async def forceadd(context, *args):
    if await incorrect_number_of_args(context, args, 2):
        return
    if not args[1].isdigit() and (int(args[1]) < 1 or int(args[1]) > 3):
        await unexpected_args()
        return
    _foundplayers = find_players(context, args)
    print(_foundplayers)
    if len(_foundplayers) == 1:
        player = _foundplayers[0]
        match_players = update_queues(player.get_id(), player.get_queues(), int(args[1]))
        if len(match_players) > 0:
            # Match found
            print("MATCH FOUND")
            pass
        else:
            # Display in queue
            print("NO MATCH FOUND")
            await display_queues(context)
    else:
        await player_not_found(context)
    
@bot.command()
async def test(context):
    '''message = Message()
    message.add_user(context.author.id)
    print(message.get_users())
    message.add_page("Page 1")
    message.add_page("Page 2")
    message.add_navigation()
    message.add_button("0")
    message.add_button("9")'''

    match_players = [442841696892485643, 1001]
    match = await create_match_pug(match_players)
    await send_match(match)
    messages[match.get_id()] = match
    

@bot.command()
async def ping(context):
    await context.message.channel.send(str(round(bot.latency*1000)) + "ms")

bot.run(config["token"])
