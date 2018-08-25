# BattleriteBot BulkAddFlags Tool - Made by Remilia (discord tsuneko#6551)

import os
from operator import or_
from functools import reduce

tournamentFlags = {
        "0" : "BattleCult Week #1 - 1st",
        "1" : "BattleCult Week #1 - Participated",
        "2" : "BattleCult Week #2 - 1st",
        "3" : "BattleCult Week #2 - Participated",
        "4" : "BattleCult Week #3 - 1st",
        "5" : "BattleCult Week #3 - Participated",
        "6" : "BattleCult Week #3 - Caster",
        "7" : "BattleCult Week #4 - 1st",
        "8" : "BattleCult Week #4 - Participated",
        "9" : "BattleCult Week #4 - Caster",
        "10" : "BattleCult Week #5 - 1st",
        "11" : "BattleCult Week #5 - Participated",
        "12" : "BattleCult Week #5+ - 1st",
        "13" : "BattleCult Week #5+ - Participated",
}

players = {}
for filename in os.listdir("players"):
        p = open("players\\" + filename, "r")
        pUsername = filename[:-4]
        players[pUsername] = {}
        for line in p.readlines():
                tokens = line.split('=')
                players[pUsername][tokens[0]] = tokens[1].rstrip()
        p.close()

filesToUpdate = {}

file = open("flags.txt", "r")
for line in file.readlines():
        flag = line.split(' ')[0]
        username = ' '.join(line.split(' ')[1:]).rstrip()
        if username not in players:
                print("Failed to find: " + username)
                continue

        pTournamentFlags = int(players[username]["tournamentFlags"])
        pFlags = []
        for f in range(len(tournamentFlags)):
                if 2**f & pTournamentFlags:
                        pFlags.append(str(f))
        if flag not in pFlags and flag in tournamentFlags:
                pFlags.append(flag)
        else:
                print("Failed to add flag: " + flag + " to: " + username)
                continue
        if len(pFlags) > 0:
                players[username]["tournamentFlags"] = str(reduce(or_, list(map(lambda x: 2**int(x), pFlags))))
                if username not in filesToUpdate:
                        filesToUpdate[username + ".txt"] = True
                print("Flag: " + flag + " added to: " + username)
file.close()

for filename in filesToUpdate:
        u = open("players\\" + filename, "w")
        pUsername = filename[:-4]
        pDataKeys = ["username","id","elo","rankedMatches","rankedWins","tournamentMatches","tournamentWins","tournamentFlags","permissionsLevel"]
        for key in pDataKeys:
                u.write(key + "=" + players[pUsername][key] + "\n")
        u.close()
