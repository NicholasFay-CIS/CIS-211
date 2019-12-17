"""
Overall control for 2048 clone 512.  Coordinates
model and view and implements controller
functionality by interpreting keyboard input
"""
import model
import view
import keypress 


def main():
    # Set up model component
    grid = model.Grid()
    # Set up view component
    game_view = view.GameView(600, 600)
    grid_view = view.GridView(game_view, len(grid.tiles))
    grid.add_listener(grid_view)
    # Handle control component responsibility here
    commands = keypress.Command(game_view)
    grid.place_tile()

    # Game continues until there is no empty
    # space for a tile
    while grid.find_empty():
        #grid.place_tile() #original place tile

        cmd = commands.next()
        oldgrid = grid.as_list() #original grid as list of lists
        if cmd == keypress.LEFT:
            grid.left()
        elif cmd == keypress.RIGHT:
            grid.right()
        elif cmd == keypress.UP:
            grid.up()
        elif cmd == keypress.DOWN:
            grid.down()
        else: 
            assert cmd == keypress.UNMAPPED

        #if a move isnt possible and a keypress happens, then a new tile will not be added to the grid
        newgrid = grid.as_list() #new grid with lists of lists
        if oldgrid != newgrid: #if grid does not change, place tile
            grid.place_tile()

    game_view.lose(grid.score())


if __name__ == "__main__":
    main()
