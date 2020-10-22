
class Field:

    def __init__(self):
        super().__init__()
        self.height = 0
        self.width = 0
        self.players = []
        
    def scale_value =

    def set_field_dimensions(self, dimensions):
        [self.width, self.height] = dimensions

    def set_position_players(self, lanesInfo):
        for lane in lanesInfo:
            position_players = []
            if lane['playerCount'] == 1:
                position_players.append(self.height / 2)
            elif lane['playerCount'] % 2 == 0:
                for i in range(lane['playerCount'] / 2):
                    position_players.append(self.height / 2)
            else:
                pass

        