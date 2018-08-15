# BattleriteBot - Made by Remilia (discord tsuneko#6551)

import discord
from discord.ext import commands
import asyncio
import random
import os
from operator import or_
from functools import reduce

# Definition of Tournament Flags
tournamentFlags = {
        "1" : "BattleCult Week #1 - 1st",
        "2" : "BattleCult Week #1 - Participated",
        "4" : "BattleCult Week #2 - 1st",
        "8" : "BattleCult Week #2 - Participated",
        "16" : "BattleCult Week #3 - 1st",
        "32" : "BattleCult Week #3 - Participated",
        "64" : "BattleCult Week #3 - Caster",
        "128" : "BattleCult Week #4 - 1st",
        "256" : "BattleCult Week #4 - Participated",
        "512" : "BattleCult Week #4 - Caster"
}

# Definition of Permissions Level
permissionsLevel = {
        "0" : "Regular User",
        "1" : "PUG Admin",
        "2" : "Tourny Admin",
        "3" : "Bot Admin"
}

helpMessage = ("```\n" +
               "Please note that all Usernames must be Case Sensitive\n" +
                "\n-- General Commands --\n" +
                "!add - Adds you to the ranked queue\n" +
                "!remove - Removes you from the ranked queue\n" +
                "!q - Lists the players currently in queue\n" +
                "!top (x) - Lists the top 10 players, starting at x\n" +
                "!rank - Displays your current rank\n" +
                "        !rank [Username] or !rank @DiscordMember can also be used\n" +
                "!stats - Provides some more details on your stats\n" +
                "        !stats [Username] or !stats @DiscordMember can also be used\n" +
                "\n-- Tools --\n" +
                "!name [Username] - Changes your nickname\n" +
                "        also will create a new user file if you don't have one\n" +
                "\n-- Admin --\n" +
                "!record A1,A2,A3,win,B1,B2,B3 - Records a win for the A players\n" +
                "        win can be substituted for wint for Tournament Matches\n" +
                "!cleareQueue - Empties the Queue\n" +
                "!flagIDs - Lists Flag IDs and their definition\n" +
                "!addFlag [Username] flag - Adds a flag to a user\n" +
                "!removeFlag [Username] flag - Removes a flag from a user\n" +
                "```")

#
# Define Containers
#

players = {}
playersLookup = {}
queue = []
tournamentQueue = []
battleriteMaps = ["Blackstone Arena Day", "Blackstone Arena Night", "Mount Araz Day", "Mount Araz Night", "Dragon Garden Day", "Dragon Garden Night"]
        
#
# Player Data Functions
#

def createDefaultPlayerData(discordMember, username = None):
        if username == None:
                f = open("players\\" + discordMember.display_name + ".txt", "w")
                f.write("username=" + discordMember.display_name + "\n")
        else:
                f = open("players\\" + username + ".txt", "w")
                f.write("username=" + username + "\n")
        f.write("id=" + discordMember.id + "\n")
        f.write("elo=1500\n")
        f.write("rankedMatches=0\n")
        f.write("rankedWins=0\n")
        f.write("tournamentMatches=0\n")
        f.write("tournamentWins=0\n")
        f.write("tournamentFlags=0\n")
        f.write("permissionsLevel=0")
        f.close()

def loadPlayerData(pUsername):
        f = open("players\\" + pUsername + ".txt", "r")
        players[pUsername] = {}
        for line in f.readlines():
                tokens = line.split('=')
                players[pUsername][tokens[0]] = tokens[1].rstrip()
        playersLookup[players[pUsername]["id"]] = players[pUsername]["username"]
        f.close()

        
def savePlayerData(pUsername):
        if not pUsername in players:
                return
        f = open("players\\" + pUsername + ".txt", "w")
        pDataKeys = ["username","id","elo","rankedMatches","rankedWins","tournamentMatches","tournamentWins","tournamentFlags","permissionsLevel"]
        for key in pDataKeys:
                f.write(key + "=" + players[pUsername][key] + "\n")
        f.close()

def createLeaderboard(playerData):
        newLeaderboard = {}
        for pUsername in playerData:
                if int(playerData[pUsername]["rankedMatches"]) >= 1:
                        newLeaderboard[pUsername] = int(playerData[pUsername]["elo"])
        return list(reversed(sorted(newLeaderboard.items(), key = lambda x: x[1])))

def calcKFactor(matchesPlayed):
        if matchesPlayed > 100:
                matchesPlayed = 100
        return (100-matchesPlayed)/2.5 + 10

def calcExp(a, b):
        return 1 / (1 + 10 ** ((b - a) / 400))

def calcElo(a, exp, score, k):
        return a + k * (score - exp)

def calcTeamElo(teamA, teamB):
        for i in range(len(teamA)):
                e = int(players[teamA[i]]["elo"])
                k = calcKFactor(int(players[teamA[i]]["rankedMatches"]))
                exp = 0
                for j in range(3):
                     exp = exp + calcExp(e, int(players[teamB[j]]["elo"]))
                players[teamA[i]]["elo"] = str(round(calcElo(e, exp, 3, k)))
        for j in range(len(teamB)):
                e = int(players[teamB[j]]["elo"])
                k = calcKFactor(int(players[teamB[i]]["rankedMatches"]))
                exp = 0
                for i in range(3):
                     exp = exp + calcExp(e, int(players[teamA[i]]["elo"]))
                players[teamB[j]]["elo"] = str(round(calcElo(e, exp, 0, k)))

#
# Parsing Tools
#
        
def getUsername(authorID, args, reqArgs = 0):
        if len(args) == reqArgs:
                if authorID in playersLookup:
                        return playersLookup[authorID]
        else:
                if (reqArgs > 0):
                        argsString = ' '.join(args[:-reqArgs]).rstrip()
                else:
                        argsString = ' '.join(args).rstrip()
                if argsString[2:-1] in playersLookup:
                        return playersLookup[argsString[2:-1]]
                elif argsString[3:-1] in playersLookup:
                        return playersLookup[argsString[3:-1]]
                elif argsString in players:
                        return argsString
                else:
                        return None

def isAdmin(authorID, reqPerms):
        if authorID in playersLookup:
                if int(players[playersLookup[authorID]]["permissionsLevel"]) >= reqPerms:
                       return True
        return False

#
# Create Bot
#

for filename in os.listdir("players"):
        pUsername = filename[:-4]
        loadPlayerData(pUsername)
bot = commands.Bot(command_prefix='!')
bot.remove_command("help")
f = open("token.txt","r")
token = f.readline().rstrip()
f.close()

matchHistoryChannel = []

@bot.event
async def on_ready():
        print("Connected as: " + bot.user.name + " ID: " + str(bot.user.id))
        for discordServer in bot.servers:
                for channel in discordServer.channels:
                        if channel.name == "match-history":
                                matchHistoryChannel.append(channel)

# !help - Usage !help
@bot.command()
async def help():
        await bot.say(helpMessage)

# !perms - Usage !perms
@bot.command(pass_context = True)
async def perms(context):
        if context.message.author.id in playersLookup:
                pUsername = playersLookup[context.message.author.id]
                await bot.say(pUsername + " your permissions level is: " + permissionsLevel[players[pUsername]["permissionsLevel"]])

# !name - Usage !name Username
@bot.command(pass_context = True)
async def name(context, *args):
        pNewUsername = ' '.join(list(args)).rstrip()
        if context.message.author.id in playersLookup:
                pOldUsername = playersLookup[context.message.author.id]
                for pUsername in players:
                        if pUsername.lower() == pNewUsername.lower():
                                return
                pDataKeys = ["username","id","elo","rankedMatches","rankedWins","tournamentMatches","tournamentWins","tournamentFlags","permissionsLevel"]
                players[pNewUsername] = {}
                for key in pDataKeys:
                        players[pNewUsername][key] = players[pOldUsername][key]
                players[pNewUsername]["username"] = pNewUsername
                playersLookup[context.message.author.id] = pNewUsername
                del players[pOldUsername]
                os.remove("players\\" + pOldUsername + ".txt")
                savePlayerData(pNewUsername)
                await bot.change_nickname(context.message.author, pNewUsername)
                await bot.say("Changed: " + pOldUsername +"'s name to: " + pNewUsername)
        else:
                createDefaultPlayerData(context.message.author, pNewUsername)
                await bot.change_nickname(context.message.author, pNewUsername)
                await bot.say("Created new user data for: " + pNewUsername)
                loadPlayerData(pNewUsername)

# !add - Usage !add
@bot.command(pass_context = True)
async def add(context):
        if context.message.author.id not in playersLookup:
                return
        pUsername = playersLookup[context.message.author.id]
        if pUsername in queue:
                return
        if len(queue) < 6:
                queue.append(pUsername)
                await bot.say(pUsername + " has been added to the queue\nQueue (" + str(len(queue))+"/6): `[" + ", ".join(queue) +"]`")
        if len(queue) == 6:
                # Sort Teams
                queueDict = {}
                for p in queue:
                        queueDict[p] = int(players[p]["elo"])
                queueSorted = list(reversed(sorted(queueDict.items(), key = lambda x: x[1])))
                teamA = [queueSorted[0][0], queueSorted[3][0], queueSorted[5][0]] # 1st, 4th, 6th
                teamB = [queueSorted[1][0], queueSorted[2][0], queueSorted[4][0]] # 2nd, 3rd, 5th
                queueMentions = []
                for pUsername in queue:
                        queueMentions.append("<@!" + players[pUsername]["id"] + ">")
                selectedMap = random.choice(battleriteMaps)
                await bot.say("`" + ",".join(teamA) + "`\n**VS**\n`" + ",".join(teamB) + "`\nSuggested Map: **" + selectedMap + "**.\nPlease post a screenshot of the match result.\n" + ' '.join(queueMentions))
                for p in reversed(range(6)):
                        queue.pop(p)

# !remove - Usage !remove
@bot.command(pass_context = True)
async def remove(context):
        if context.message.author.id not in playersLookup:
                return
        pUsername = playersLookup[context.message.author.id]
        if pUsername in queue:
                queue.remove(pUsername)
                await bot.say(pUsername + " has been removed from the queue\nQueue (" + str(len(queue))+"/6): `[" + ", ".join(queue) +"]`")

# !q - Usage !q
@bot.command()
async def q():
        await bot.say("Queue (" + str(len(queue))+"/6): `[" + ", ".join(queue) +"]`")

# !clearQueue - Usage !clearQueue
@bot.command(pass_context = True)
async def clearQueue(context):
        if isAdmin(context.message.author.id, 1) == False or len(queue) == 0:
                return
        for p in reversed(range(len(queue))):
                queue.pop(p)
        await bot.say("Cleared the Queue")
        
        
# !top - Usage !top (x)
@bot.command()
async def top(*args):
        start = 1
        if len(args) > 0:
                args = list(args)
                if args[0].isdigit():
                        start = int(args[0])
        newLeaderboard = createLeaderboard(players)
        displayedLeaderboard = []
        i=1
        actualRank = 1
        displayedRank = 1
        currentScore = newLeaderboard[0][1]
        if start <= len(newLeaderboard): 
                for value in newLeaderboard:
                        if value[1] < currentScore:
                                currentScore = value[1]
                                displayedRank = actualRank
                        actualRank = actualRank + 1
                        if i >= start and i <= start + 9:
                                displayedLeaderboard.append("#"+str(displayedRank)+" ["+str(value[1])+"] - "+value[0])
                        i = i + 1
                await bot.say("```" + "\n".join(displayedLeaderboard).rstrip() + "```")
        else:
                await bot.say("There are no leaderboard entries starting at #" + str(start))

# !giveMeTheWholeLeaderboard
@bot.command()
async def giveMeTheWholeLeaderboard():
        newLeaderboard = createLeaderboard(players)
        displayedLeaderboard = []
        i=1
        actualRank = 1
        displayedRank = 1
        currentScore = newLeaderboard[0][1]
        for value in newLeaderboard:
                if value[1] < currentScore:
                        currentScore = value[1]
                        displayedRank = actualRank
                actualRank = actualRank + 1
                displayedLeaderboard.append("#"+str(displayedRank)+" ["+str(value[1])+"] - "+value[0])
                i = i + 1
        await bot.say("```" + "\n".join(displayedLeaderboard).rstrip() + "```")

# !beepboop
@bot.command()
async def beepboop():
        await bot.say("No.")

# !rank - Usage !rank, !rank Username, !rank @DiscordMember
@bot.command(pass_context = True)
async def rank(context, *args):
        args = list(args)
        pUsername = getUsername(context.message.author.id, args)
        if pUsername == None:
                return
        newLeaderboard = createLeaderboard(players)
        actualRank = 1
        displayedRank = 1
        currentScore = newLeaderboard[0][1]
        for value in newLeaderboard:
                if value[1] < currentScore:
                        currentScore = value[1]
                        displayedRank = actualRank
                if value[0] == pUsername:
                        await bot.say(pUsername + " is ranked #" + str(displayedRank))
                        return
                actualRank = actualRank + 1
        await bot.say(pUsername + " is unranked")

# !stats - Usage: !stats, !stats Username, !stats @DiscordMember
@bot.command(pass_context = True)
async def stats(context, *args):
        args = list(args)
        pUsername = getUsername(context.message.author.id, args)
        if pUsername == None:
                return
        pElo = int(players[pUsername]["elo"])
        pRankedMatches = int(players[pUsername]["rankedMatches"])
        pRankedWins = int(players[pUsername]["rankedWins"])
        pRankedLosses = pRankedMatches - pRankedWins
        if pRankedMatches == 0:
                pRankedWinRatio = 0
        else:
                pRankedWinRatio = round(pRankedWins / pRankedMatches * 100, 2)
        pTournamentMatches = int(players[pUsername]["tournamentMatches"])
        pTournamentWins = int(players[pUsername]["tournamentWins"])
        pTournamentLosses = pTournamentMatches - pTournamentWins
        if pTournamentMatches == 0:
                pTournamentWinRatio = 0
        else:
                pTournamentWinRatio = round(pTournamentWins / pTournamentMatches * 100, 2)
                
        pTournamentFlags = int(players[pUsername]["tournamentFlags"])
        pTournamentResults = []
        pTournamentFlag = 1
        for _ in range(len(tournamentFlags)):
                if pTournamentFlag & pTournamentFlags:
                        pTournamentResults.append(tournamentFlags[str(pTournamentFlag)])
                pTournamentFlag = pTournamentFlag * 2
        pTournamentResultsString = ""
        if len(pTournamentResults) > 0:
                pTournamentResultsString = "\n".join(pTournamentResults) + "\n"

        newLeaderboard = createLeaderboard(players)
        ranked = False
        rankedString = "UNR"
        actualRank = 1
        displayedRank = 1
        currentScore = newLeaderboard[0][1]
        for value in newLeaderboard:
                if value[1] < currentScore:
                        currentScore = value[1]
                        displayedRank = actualRank
                if value[0] == pUsername:
                        ranked = True
                        rankedString = str(displayedRank)
                        break
                actualRank = actualRank + 1
                
        await bot.say(pUsername + "'s Stats:\n```" +
                      "Rank: " + "#" + rankedString + " [" + str(pElo) + "]\n" +
                      "Total Matches Played: " + str(pRankedMatches) + " [" + str(pRankedWins) + "-" + str(pRankedLosses) + "] (" + str(pRankedWinRatio) + "%)\n" +
                      "Matches Played (TNY): " + str(pTournamentMatches) + " [" + str(pTournamentWins) + "-" + str(pTournamentLosses) + "] (" + str(pTournamentWinRatio) + "%)\n" +
                      pTournamentResultsString + "```")

# !record - Usage !record User1|User2|User3|win/wint|User4|User5|User6
@bot.command(pass_context = True)
async def record(context, *args):
        args = ' '.join(list(args)).rstrip().split(',')
        if isAdmin(context.message.author.id, 1) == False:
                return
        if len(args) != 7 or (args[3] != "win" and args[3] != "wint"):
                return
        for i in range(len(args)):
                if i == 3:
                        continue
                if args[i] not in players:
                        await bot.say("```"+args[i] + " is not a valid player"+"```")
                        return
        winners = args[0:3]
        losers = args[4:7]
        matchPlayers = winners+losers
        for pUsername in matchPlayers:
                players[pUsername]["rankedMatches"] = str(int(players[pUsername]["rankedMatches"]) + 1)
                if args[3] == "wint":
                        players[pUsername]["tournamentMatches"] = str(int(players[pUsername]["tournamentMatches"]) + 1)
                if pUsername in winners:
                        players[pUsername]["rankedWins"] = str(int(players[pUsername]["rankedWins"]) + 1)
                        if args[3] == "wint":
                                players[pUsername]["tournamentWins"] = str(int(players[pUsername]["tournamentWins"]) + 1)  
        tournamentString = ""
        if args[3] == "wint":
                tournamentString = "Tournament "
        # Calculate elo
        eloChange = []
        matchPlayersElo = []
        for i in range(len(matchPlayers)):
                eloChange.append(players[matchPlayers[i]]["elo"] + " -> ")
                matchPlayersElo.append(int(players[matchPlayers[i]]["elo"]))
        calcTeamElo(winners,losers)
        for i in range(len(matchPlayers)):
                eloChange[i] = eloChange[i] + players[matchPlayers[i]]["elo"] + " (" + str(int(players[matchPlayers[i]]["elo"]) - matchPlayersElo[i]) + ") - " + matchPlayers[i]
        await bot.say("`" + ", ".join(winners) + "`\n**Win VS**\n`" + ", ".join(losers) + "`\n\n" + tournamentString + "Match Recorded. Elo Changes:\n```" + "\n".join(eloChange).rstrip() + "```")
        for p in matchPlayers:
                savePlayerData(p)
        for channel in matchHistoryChannel:
                await bot.send_message(channel, "```" + context.message.content + "```")

# !sortTeams - Usage !sortTeams @DiscordRole role
@bot.command(pass_context = True)
async def sortTeams(context, role : discord.Role):
        if context.message.author.id in playersLookup:
                if int(players[playersLookup[context.message.author.id]]["permissionsLevel"]) < 2:
                       return
        tournamentPlayers = {}
        for discordMember in context.message.author.server.members:
                if role in discordMember.roles:
                        if discordMember.id in playersLookup:
                                pUsername = playersLookup[discordMember.id]
                                tournamentPlayers[pUsername] = players[pUsername]["elo"]
        if len(tournamentPlayers) %3 != 0:
                await bot.say("The amount of " + role.name + " players must be divisible by 3. Currently: " + str(len(tournamentPlayers)))
                return
        tournamentPlayersSorted = list(reversed(sorted(tournamentPlayers.items(), key = lambda x: x[1])))
        tournamentTeamCount = len(tournamentPlayersSorted)//3
        tournamentDiv1 = []
        for i in range(tournamentTeamCount):
                tournamentDiv1.append(tournamentPlayersSorted[i][0])
        random.shuffle(tournamentDiv1)
        tournamentDiv2 = []
        for i in range(tournamentTeamCount,tournamentTeamCount*2):
                tournamentDiv2.append(tournamentPlayersSorted[i][0])
        random.shuffle(tournamentDiv2)
        tournamentDiv3 = []
        for i in range(tournamentTeamCount*2,tournamentTeamCount*3):
                tournamentDiv3.append(tournamentPlayersSorted[i][0])
        random.shuffle(tournamentDiv3)
        tournamentTeams = []
        for i in range(tournamentTeamCount):
                tournamentTeams.append("Team #" + str(i+1) + ": `" + tournamentDiv1[i] + "," + tournamentDiv2[i] + "," + tournamentDiv3[i] + "`")
        await bot.say("Tournament Teams:\n" + "\n".join(tournamentTeams) + "\n" + role.mention)

# !flagIDs - Usage: !flagIDs
@bot.command(pass_context = True)
async def flagIDs(context):
        if context.message.author.id in playersLookup:
                if int(players[playersLookup[context.message.author.id]]["permissionsLevel"]) < 2:
                       return
        f = 1
        flags = []
        for _ in range(len(tournamentFlags)):
                flags.append("#" + str(f) + " - " + tournamentFlags[str(f)])
                f = f * 2
        await bot.say("Flag IDs:\n```" + "\n".join(flags) + "```")

# !addFlag - Usage: !addFlag flag, !addFlag Username flag, !addFlag @DiscordMember flag
@bot.command(pass_context = True)
async def addFlag(context, *args):
        args = list(args)
        pUsername = getUsername(context.message.author.id, args, 1)
        if pUsername == None or isAdmin(context.message.author.id, 2) == False:
                return
        pTournamentFlags = int(players[pUsername]["tournamentFlags"])
        fFlag = args[-1]
        pFlags = []
        pFlag = 1
        for _ in range(len(tournamentFlags)):
                if pFlag & pTournamentFlags:
                        pFlags.append(str(pFlag))
                pFlag = pFlag * 2
        if fFlag not in pFlags and fFlag in tournamentFlags:
                pFlags.append(fFlag)
        else:
                return
        if len(pFlags) > 0:
                players[pUsername]["tournamentFlags"] = str(reduce(or_, list(map(int, pFlags))))
                savePlayerData(pUsername)
        await bot.say("Added Flag: [" + tournamentFlags[fFlag] + "] to " + pUsername)

# !removeFlag - Usage: !removeFlag flag, !removeFlag, Username flag, !removeFlag @DiscordMember flag
@bot.command(pass_context = True)
async def removeFlag(context, *args):
        args = list(args)
        pUsername = getUsername(context.message.author.id, args, 1)
        if pUsername == None or isAdmin(context.message.author.id, 2) == False:
                return
        pTournamentFlags = int(players[pUsername]["tournamentFlags"])
        fFlag = args[-1]
        pFlags = []
        pFlag = 1
        for _ in range(len(tournamentFlags)):
                if pFlag & pTournamentFlags:
                        pFlags.append(str(pFlag))
                pFlag = pFlag * 2
        if fFlag in pFlags:
                pFlags.remove(fFlag)
        else:
                return
        if len(pFlags) > 0:
                players[pUsername]["tournamentFlags"] = str(reduce(or_, list(map(int, pFlags))))
        else:
                players[pUsername]["tournamentFlags"] = "0"
        savePlayerData(pUsername)
        await bot.say("Removed Flag: [" + tournamentFlags[fFlag] + "] from " + pUsername)

# !setPerms - Usage: !setPerms Username level, !setPerms @DiscordMember level
@bot.command(pass_context = True)
async def setPerms(context, *args):
        args = list(args)
        pUsername = getUsername(context.message.author.id, args, 1)
        if isAdmin(context.message.author.id, 3) == False or pUsername == playersLookup[context.message.author.id] or level not in permissionsLevel:
                return
        players[pUsername]["permissionsLevel"] = str(level)
        savePlayerData(pUsername)
        await bot.say("Set " + pUsername + "'s permissions level to: " + permissionsLevel[level])
        
# !resetAllUsers - Usage: !resetAllUsers
@bot.command(pass_context = True)
async def resetAllUsers(context):
        if isAdmin(context.message.author.id, 3) == False:
                return
        for discordMember in context.message.server.members:
                createDefaultPlayerData(discordMember)
                loadPlayerData(discordMember.display_name)
        players[playersLookup[context.message.author.id]]["permissionsLevel"] = "3"
        savePlayerData(playersLookup[context.message.author.id])
        await bot.say("Beep Boop! Nuked the Player Data")

#
# Run Bot
#

bot.run(token)
