class Player:
    def __init__(self, first_name, last_name, gamertag, primary_role, secondary_role, **ratings):
        self.first_name = first_name
        self.last_name = last_name
        self.gamertag = gamertag
        self.primary_role = primary_role
        self.secondary_role = secondary_role
        self.ratings = ratings

    @property
    def overall_rating(self):
        return sum(self.ratings.values()) / len(self.ratings)

    def __str__(self):
        return f"{self.gamertag} ({self.first_name} {self.last_name}) - {self.primary_role}"
