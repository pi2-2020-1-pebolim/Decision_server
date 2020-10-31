
class Player:

    def __init__(self, laneID, xPosition, yCenterPosition, movementLimit):
        super().__init__()

        self.laneID = laneID
        
        self.xPosition = xPosition
        self.yCenterPosition = yCenterPosition

        self.yMaxPosition = 0
        self.yMinPosition = 0
        self.set_y_max_min_positions(movementLimit)

    def set_y_max_min_positions(self, movementLimit):
        self.yMaxPosition = self.yCenterPosition + movementLimit
        self.yMinPosition = self.yCenterPosition - movementLimit

    def can_intercept(self, real_y):
        return self.yMinPosition <= real_y <= self.yMaxPosition