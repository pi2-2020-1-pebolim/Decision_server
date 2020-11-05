from model.player import Player

class Field:

    def __init__(self, lanes, dimensions, resolution, event_controller):
        
        super().__init__()
        self.event_controller = event_controller
        
        [self.real_width, self.real_height] = dimensions
        
        self.players = []
        self.players_in_lane = {}

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

        self.roi_dimensions = None
        self.roi_scale = None

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
                
                y_position_adjust_list = None
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
            self.players_in_lane[lane['laneID']] = lane_players
        
        self.lanes_real_x_positions = lanes_x_positions
        self.players = players

    def _calculate_ROI_scale(self):

        if self.roi_scale is not None:
            return

        roi_x, roi_y, roi_end_x, roi_end_y = self.event_controller.image_controller.ROI

        widht = roi_end_x - roi_x
        height = roi_end_y - roi_y

        self.roi_dimensions = (widht, height)
        self.roi_scale = self.real_width / widht
        
        
    def to_real(self, x, y):
        self._calculate_ROI_scale()
        return (
            (x) * self.roi_scale,
            (y) * self.roi_scale
        )

    def to_pixel(self, x, y):        
        self._calculate_ROI_scale()
        return (
            x / self.roi_scale,
            (self.real_height - y) / self.roi_scale
        )

    def to_pixel_int(self, x, y):
        pixel_tuple = self.to_pixel(x, y)
        return (int(pixel_tuple[0]), int(pixel_tuple[1]))