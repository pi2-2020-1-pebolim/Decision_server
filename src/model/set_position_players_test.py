from field import Field

lanes = [
    {
        "laneID": 0,
        "xPosition": 12,
        "playerCount": 1,
        "playerDistance": 0,
        "movementLimit": 4,
    },
    {
        "laneID": 1, 
        "xPosition": 24,
        "playerCount": 2,
        "playerDistance": 10,
        "movementLimit": 10,
    },
    {
        "laneID": 2, 
        "xPosition": 36,
        "playerCount": 5,
        "playerDistance": 8,
        "movementLimit": 5,
    },
    {
        "laneID": 3, 
        "xPosition": 60,
        "playerCount": 3,
        "playerDistance": 10,
        "movementLimit": 8,
    },
]

new_field = Field()
new_field.set_field_dimensions([150, 70])

new_field.set_lanes_players_positions(lanes)

print(new_field.lanes_x_positions)

for index, player in enumerate(new_field.players):
    print(f"\nJogador: {index + 1}\nID Haste: {player.laneID}\nX: {player.xPosition}\nY central: {player.yCenterPosition}\nY máximo: {player.yMaxPosition}\nY mínimo: {player.yMinPosition}")