
class Scoreboard:
    def __init__(self):
        self.scores = {}
    def ensure_team(self, team):
        if team not in self.scores:
            self.scores[team] = 0
    def add(self, team, points):
        self.ensure_team(team)
        self.scores[team] += points
    def get(self, team):
        return self.scores.get(team, 0)
    def snapshot(self):
        return dict(self.scores)
