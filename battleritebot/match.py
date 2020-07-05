from battleritebot.player import Player
from battleritebot.message import Message
from matchmaking_strategies import MatchmakingStrategy
from datetime import datetime

buttonsLookup = {
    "Left": "\U00002b05", #u"2b05",
    "Right":"\U000027A1", #"➡",
    "Up": "\U00002B06", #"⬆",
    "Down": "\U00002B07", #"⬇",
    "Confirm": "\U00002705", #"✅",
    "Decline": "\U0000274C", #"❌"
}
for i in range(26):
    buttonsLookup[chr(ord("A") + i)] = chr(int("0x0001" + str(hex(int("0xf1e6", 16) + i))[2:],16))
for i in range(10):
    buttonsLookup[chr(ord("0") + i)] = chr(ord("0") + i) + "\U000020E3"

emojiLookup = {}
for button in buttonsLookup:
    emojiLookup[buttonsLookup[button]] = button

class Match(Message):
    def __init__(self, match_players, mentions = [], buttons = []):
        self.players = match_players
        self.mentions = mentions
        super().__init__(list(match_players.keys()), buttons, prefix = "", suffix = "")
        self.match_format = len(match_players.keys()) // 2
        self.match_format_string = str(self.match_format) + "v" + str(self.match_format)
        self.status = "init"

    def create_pug(self, match_map, matchmaking_strategy : MatchmakingStrategy):
        self.map = match_map
        if self.match_format == 3:
            self.ws = 5
        else:
            self.ws = 3

        self.scoreA = None
        self.scoreB = None
        self.submitting = 0
        
        # Team selection process
        self.teamA = []
        self.teamB = []

        matchmaking_strategy.assign_teams(self)

        print(self.teamA)
        print(self.teamB)

        self.set_buttons(["A", "B", "Decline"])
        self.status = "match"
        self.update_match_page()

    def update_match_page(self):
        button_string = ""
        self.clear_buttons()
        if self.submitting == 0:
            if self.scoreA != None and self.scoreB != None and self.scoreA != self.scoreB and (self.scoreA == self.ws or self.scoreB == self.ws):
                button_string = "Press [A] or [B] to update scores. Press [✅] to confirm score as " + str(self.scoreA) + ":" + str(self.scoreB) + " Press [❌] to cancel match."
                self.set_buttons(["A","B","Confirm","Decline"])
            else:    
                button_string = "Press [A] or [B] to update scores. Press [❌] to cancel match."
                self.set_buttons(["A","B","Decline"])
        elif self.submitting == 1:
            button_string = "Press the number corresponding to Team A's score."
            for i in range(self.ws,-1,-1):
                self.add_button(str(i))
        elif self.submitting == 2:
            button_string = "Press the number corresponding to Team B's score."
            for i in range(self.ws,-1,-1):
                self.add_button(str(i))
        teams_string = "{0:30}{1}\n".format("Team A" + (" - " + str(self.scoreA) if self.scoreA != None else ""), "Team B" + (" - " + str(self.scoreB) if self.scoreB != None else ""))
        for i in range(self.match_format):
            teams_string += "{0:30}{1}\n".format("[" + str(self.teamA[i][2]) + "] " + self.teamA[i][1], "[" + str(self.teamB[i][2]) + "] " + self.teamB[i][1])
        self.set_page(" ".join(self.mentions) + "\nFormat: " + str(self.match_format_string) + " | Map: " + self.map + " | Win Score: " + str(self.ws) + "\n```\n" + teams_string + "```\n" + button_string, 0)

    def cancel_page(self, user_id):
        self.clear_buttons()
        self.set_page(" ".join(self.mentions) + "\nMatch Cancelled by: `" + self.players[user_id].username +"`\nPlease rejoin the queue with `!add`", 0)

    def finish_page(self):
        self.clear_buttons()
        self.set_page(" ".join(self.mentions) + "\nScore " + str(self.scoreA) + ":" + str(self.scoreB) + " Submitted by: `" + self.players[self.submit_by].username + "`\nPlease rejoin the queue with `!add`", 0)

    def emoji_pressed(self, emoji, user_id):
        button = emojiLookup[emoji]
        if self.status == "match":
            if button == "Decline":
                self.cancel_page(user_id)
                self.status = "cancel"
                self.alive = False
                return True
            elif button == "A":
                self.status = "submitA"
                self.submitting = 1
                self.update_match_page()
                return True
            elif button == "B":
                self.status = "submitB"
                self.submitting = 2
                self.update_match_page()
                return True
            elif button == "Confirm":
                self.status = "finish"
                self.clear_buttons()
                self.submit_by = user_id
                self.finish_page()
                self.alive = False
                return True
        elif self.status == "submitA":
            if button.isdigit() and int(button) >= 0 and int(button) <= self.ws:
                self.scoreA = int(button)
                self.submitting = 0
                self.status = "match"
                self.update_match_page()
                return True
        elif self.status == "submitB":
            if button.isdigit() and int(button) >= 0 and int(button) <= self.ws:
                self.scoreB = int(button)
                self.submitting = 0
                self.status = "match"
                self.update_match_page()
                return True

    def create_premade(self, map_pool, champ_bans = False):
        pass

    def to_result_data(self):
        if self.status == "finish":
            data = {}
            data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data["submit_by"] = self.submit_by
            data["score"] = [self.scoreA, self.scoreB]
            data["teamA"] = []
            data["teamB"] = []
            for i in range(self.match_format):
                data["teamA"].append(self.teamA[i][0])
                data["teamB"].append(self.teamB[i][0])
            for i in range(self.match_format):
                data[str(self.teamA[i][0])] = [self.teamA[i][2], self.teamA[i][3]]
                data[str(self.teamB[i][0])] = [self.teamB[i][2], self.teamB[i][3]]
            return data
        return None

    
