from model.player import Player

class Field:

    def __init__(self, lanes, dimensions, resolution):
        
        super().__init__()
        
        [self.real_width, self.real_height] = dimensions
        
        self.players = []

        self.lanes_real_x_positions = []
        self.scaled_x_positions = []
        
        self.img_height = 0
        self.img_width = 0
        
        self.set_image_resolution(resolution)

        # scale represents the relation between the cm and pixel
        # measurements
        # Xcm / scale == Xpixel
        # Xpixel * scale == Xcm
        self.image_scale = self.real_width / self.img_width

        self.set_lanes_players_positions(lanes)


    def set_image_resolution(self, resolution):
        self.img_width = resolution['Item1']
        self.img_height = resolution['Item2']

    def set_lanes_players_positions(self, lanes):
        lanes_x_positions = []
        players = []
        lane_center_y_position = self.real_height / 2
        
        for lane in lanes:
            lanes_x_positions.append(lane['xPosition'])
            lane_players = []

            for player_index in range(lane['playerCount']):

                if lane['playerCount'] % 2 == 0:
                    y_position_adjust_list = [0.5, -0.5, 1.5, -1.5]
                
                elif lane['playerCount'] % 2 == 1:
                    y_position_adjust_list = [0, 1, -1, 2, -2]
                
                else:
                    pass
                
                y_center_position = lane_center_y_position + y_position_adjust_list[player_index] * lane['playerDistance']

                new_player = Player(
                    lane['laneID'],
                    lane['xPosition'],
                    y_center_position,
                    lane['movementLimit']
                )
                
                lane_players.append(new_player)

            players.extend(lane_players)
        
        self.lanes_real_x_positions = lanes_x_positions
        self.players = players

    def to_real(self, x):
        return x * self.image_scale

    def to_pixel(self, x):
        return x / self.image_scale