from datetime import datetime

class MatchResult():
    def __init__(self, data):
        self.id = -1
        self.time = data["time"]
        self.submit_by = data["submit_by"]
        self.score = data["score"]
        self.teamA = data["teamA"]
        self.teamB = data["teamB"]
        self.mmr = {}
        for i in range(len(self.teamA)):
            self.mmr[self.teamA[i]] = data[str(self.teamA[i])]
            self.mmr[self.teamB[i]] = data[str(self.teamB[i])]
    def set_id(self, id):
        self.id = id
    def get_id(self):
        return self.id
    def __str__(self):
        output_string = ["time = " + self.time,
                         "submit_by = " + str(self.submit_by),
                         "score = [" + str(self.score[0]) + "," + str(self.score[1]) + "]",
                         "teamA = [" + ",".join(list(map(str,self.teamA))) + "]",
                         "teamB = [" + ",".join(list(map(str,self.teamB))) + "]"]
        for i in range(len(self.teamA)):
            output_string.append(str(self.teamA[i]) + " = [" + ",".join(list(map(str,self.mmr[self.teamA[i]]))) + "]")
        for i in range(len(self.teamB)):
            output_string.append(str(self.teamB[i]) + " = [" + ",".join(list(map(str,self.mmr[self.teamB[i]]))) + "]")
        return "\n".join(output_string)
