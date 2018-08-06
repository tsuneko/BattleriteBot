# BattleriteBot - Made by Remilia (discord tsuneko#6551)

import discord
from discord.ext import commands
import asyncio
import random

queue2v2 = []
queue3v3 = []
modes = {
        "2v2": 2, "2": 2, "2s": 2,
        "3v3": 3, "3": 3, "3s": 3,
        "any": 0, "both": 0
        }

def startMatch(mode, playerList):
        playerMentionList = []
        for p in playerList:
                playerMentionList.append(p.mention)
        random.shuffle(playerMentionList)
        if mode == 2:
                team1 = ", ".join(playerMentionList[0:2])
                team2 = ", ".join(playerMentionList[2:4])
        elif mode == 3:
                team1 = ", ".join(playerMentionList[0:3])
                team2 = ", ".join(playerMentionList[3:6])
        return "Team 1: " + team1 + "\n" + "Team 2: " + team2

def displayQueues(playerList2v2, playerList3v3):
        playerNickList2v2 = []
        for p in playerList2v2:
                playerNickList2v2.append(p.display_name)
        strqueue2v2 = "2v2 Queue (" + str(len(playerNickList2v2)) + "/4): [" + ", ".join(playerNickList2v2) + "]"
        playerNickList3v3 = []
        for p in playerList3v3:
                playerNickList3v3.append(p.display_name)
        strqueue3v3 = "3v3 Queue (" + str(len(playerNickList3v3)) + "/6): [" + ", ".join(playerNickList3v3) + "]"
        return strqueue2v2 + "\n" + strqueue3v3

bot = commands.Bot(command_prefix='!')
bot.remove_command("help")
token = "NDc1OTIxNjk3MDY1Nzk1NTg0.DkmExw.n03KeQpAEcAh1QeCnbG_uGorOfo"

@bot.event
async def on_ready():
        print("Connected as: " + bot.user.name + " ID: " + str(bot.user.id))

@bot.command(pass_context = True)
async def add(context, mode : str):
        # Add the player to the specified queue
        added2v2 = False
        added3v3 = False
        mode = mode.lower()
        if not mode in modes:
                return
        else:
                player = context.message.author
                if modes[mode] == 2 and player not in queue2v2:
                        added2v2 = True
                        queue2v2.append(player)
                elif modes[mode] == 3 and player not in queue3v3:
                        added3v3 = True
                        queue3v3.append(player)
                elif modes[mode] == 0:
                        if player not in queue2v2:
                                added2v2 = True
                                queue2v2.append(player)
                        if player not in queue3v3:
                                added3v3 = True
                                queue3v3.append(player)
        # Check if queues are full, if they are then start the match (prioritise 3v3 over 2v2)
        if len(queue3v3) == 6:
                for player in queue3v3:
                        if player in queue2v2:
                                queue2v2.remove(player)
                await bot.say(startMatch(3, queue3v3))
                for i in reversed(range(6)):
                        queue3v3.pop(i)
        elif len(queue2v2) == 4:
                for player in queue2v2:
                        if player in queue3v3:
                                queue3v3.remove(player)
                await bot.say(startMatch(2, queue2v2))
                for i in reversed(range(4)):
                        queue2v2.pop(i)
        else:
                if added2v2 == True:
                        await bot.say(player.mention + " has been added to the 2v2 queue.")
                if added3v3 == True:
                        await bot.say(player.mention + " has been added to the 3v3 queue.")
                if added2v2 == True or added3v3 == True:
                        await bot.say(displayQueues(queue2v2, queue3v3))

@bot.command(pass_context = True)
async def remove(context, mode : str):
        # Remove the player from the specified queue
        removed2v2 = False
        removed3v3 = False
        mode = mode.lower()
        if not mode in modes:
                return
        else:
                player = context.message.author
                if modes[mode] == 2 and player in queue2v2:
                        removed2v2 = True
                        queue2v2.remove(player)
                elif modes[mode] == 3 and player in queue3v3:
                        removed3v3 = True
                        queue3v3.remove(player)
                elif modes[mode] == 0:
                        if player in queue2v2:
                                removed2v2 = True
                                queue2v2.remove(player)
                        if player in queue3v3:
                                removed3v3 = True
                                queue3v3.remove(player)
        if removed2v2 == True:
                await bot.say(player.mention + " has been removed from the 2v2 queue.")
        if removed3v3 == True:
                await bot.say(player.mention + " has been removed from the 3v3 queue.")
        if removed2v2 == True or removed3v3 == True:
                await bot.say(displayQueues(queue2v2, queue3v3))

@bot.command()
async def status():
        # Display the players in queue
        await bot.say(displayQueues(queue2v2, queue3v3))

@bot.command()
async def queue():
        # Display the players in queue
        await bot.say(displayQueues(queue2v2, queue3v3))

@bot.command()
async def help():
        await bot.say("Commands:\n```!add [mode]\n!remove [mode]\n[mode] is one of these: 2v2, 2s, 2, 3v3, 3s, 3, any, both\n!queue\n!status```")

bot.run(token)

