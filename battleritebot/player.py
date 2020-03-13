class Player:
        def __init__(self, data):
                if "username" in data:
                        self.username = data["username"]
                else:
                        self.username = "None"
                if "ID" in data:
                        self.id = data["ID"]
                else:
                        self.id = 0
                if "can_submit" in data:
                        self.can_submit = data["can_submit"]
                else:
                        self.can_submit = True
                self.mmr = []
                for q in ["1v1", "2v2", "3v3"]:
                        if q + "_mmr" in data:
                                self.mmr.append(data[q + "_mmr"])
                        else:
                                self.mmr.append([1500])
                self.matches = []
                for q in ["1v1", "2v2", "3v3"]:
                        if q + "_matches" in data:
                                self.matches.append(data[q + "_matches"])
                        else:
                                self.matches.append([])
                self.queues = []
                for q in ["1v1", "2v2", "3v3"]:
                        if q + "_enabled" in data:
                                self.queues.append(data[q + "_enabled"])
                        else:
                                self.queues.append(False)
                if "teams" in data:
                        self.teams = data["teams"]
                else:
                        self.teams = []
                if "titles" in data:
                        self.titles = data["titles"]
                else:
                        self.titles = []
                if "current_title" in data:
                        self.current_title = data["current_title"]
                else:
                        self.current_title = "None"
        def get_username(self):
                return self.username
        def set_username(self, username):
                self.username = username
        def get_id(self):
                return self.id
        def get_submit(self):
                return self.can_submit
        def set_submit(self, flag):
                self.can_submit = flag
        def get_mmr(self):
                return self.mmr
        def append_mmr(self, queue, num):
                self.mmr[queue].append(num)
        def get_matches(self):
                return self.matches
        def append_match(self, queue, match):
                self.matches[queue].append(match)
        def get_queues(self):
                return self.queues
        def set_queue(self, queue, flag):
                self.queues[queue] = flag
        def get_titles(self, index):
                return self.titles
        def add_title(self, title):
                self.titles.append(title)
        def set_title(self, index):
                self.current_title = self.titles[index]
        def add_team(self, team):
                self.teams.append(team)
        def info(self):
                return self.username
        def __str__(self):
                _mmr = []
                _matches = []
                for i in range(len(self.mmr)):
                        _mmr.append(list(map(str, self.mmr[i])))
                        _matches.append(list(map(str, self.matches[i])))
                _queues = list(map(str, self.queues))
                return "\n".join(["username = " + self.username,
                                  "ID = " + str(self.id),
                                  "can_submit = " + str(self.can_submit),
                                  "1v1_mmr = [" + ",".join(_mmr[0]) + "]",
                                  "1v1_matches = [" + ",".join(_matches[0]) + "]",
                                  "2v2_mmr = [" + ",".join(_mmr[1]) + "]",
                                  "2v2_matches = [" + ",".join(_matches[1]) + "]",
                                  "3v3_mmr = [" + ",".join(_mmr[2]) + "]",
                                  "3v3_matches = [" + ",".join(_matches[2]) + "]",
                                  "1v1_enabled = " + _queues[0],
                                  "2v2_enabled = " + _queues[1],
                                  "3v3_enabled = " + _queues[2],
                                  "teams = [" + ",".join(self.teams) + "]",
                                  "titles = [" + ",".join(self.titles) + "]",
                                  "current_title = " + self.current_title])
                                  
                                  
