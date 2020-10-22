
class Player:

    def __init__(self, laneID, xPosition):
        super().__init__()
        self.laneID = laneID
        self.xPosition = xPosition
        self.yCenterPosition = 0
        self.yMaxPosition = 0
        self.yMinPosition = 0

    def set_y_center_position(self, yCenterPosition):
        self.yCenterPosition = yCenterPosition

    def set_y_max_min_positions(self, movementLimit):
        self.yMaxPosition = self.yCenterPosition + movementLimit
        self.yMinPosition = self.yCenterPosition - movementLimit

    def get_y_max_positions(self):
        return self.yMaxPosition
    
    def get_y_min_positions(self):
        return self.yMinPosition
 
    