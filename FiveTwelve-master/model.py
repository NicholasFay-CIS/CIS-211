"""
The game state and logic (model component) of 512,
a game based on 2048 with a few changes.
This is the 'model' part of the model-view-controller
construction plan.  It must NOT depend on any
particular view component, but it produces event
notifications to trigger view updates.
Author: Nicholas D. Fay, nfay@uoregon.edu
"""

import random

# Configuration constants
GRID_SIZE = 4


class Game_Element(object):
    """Base class for game elements, especially to support
    depiction through Model-View-Controller.
    """

    def __init__(self):
        """Each game element can have zero or more listeners.
        Listeners are view components that react to notificatons.
        """
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def notify(self, event, data={}):
        """Instead of handling graphics in the model component,
        we notify view components of each significant event and let
        the view component decide how to adjust the graphical view.
        When additional information must be packaged with an event,
        it goes in the optional 'data' parameter.
        """
        for listener in self.listeners:
            listener.notify(event, self, data)


class Grid(Game_Element):
    """The game grid."""

    def __init__(self):
        super().__init__()
        self.rows = GRID_SIZE
        self.cols = GRID_SIZE
        # Initialize tiles as a matrix of "None" (empty)
        self.tiles = []
        for row in range(self.rows):
            columns = []
            for col in range(self.cols):
                columns.append(None)
            self.tiles.append(columns)

    def __str__(self):
        rep = []
        for row in self.tiles:
            labels = [str(x) for x in row]
            rep.append("[{}]".format(",".join(labels)))
        return "[{}]".format(",".join(rep))

    def in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def as_list(self):
        """Grid as a list of lists of numbers; for serialization
        and especially for testing.
        """
        rep = []
        for row in self.tiles:
            value_list = []
            for tile in row:
                if tile is None:
                    value_list.append(0)
                else:
                    value_list.append(tile.value)
            rep.append(value_list)
        return rep

    def set_tiles(self, rep):
        """Set tiles to a saved configuration, which must
        have the correct dimensions (e.g., 4 rows of 4 columns
        if grid size is 4).
        """
        self.tiles = []
        for row in range(self.rows):
            row_tiles = []
            for col in range(self.cols):
                if rep[row][col] == 0:
                    row_tiles.append(None)
                else:
                    val = rep[row][col]
                    tile = Tile(self, row, col, value=val)
                    row_tiles.append(tile)
                    self.notify("New", data={"tile": tile})
            self.tiles.append(row_tiles)

    def score(self):
        """The score is the total value of all tiles"""
        sum = 0
        for row in self.tiles:
            for col in row:
                if col:
                    sum += col.value
        return sum

    # Game logic
    def find_empty(self):
        """Find an empty cell (where we can drop a new tile).
        Returns a row,col pair or None to indicate there are no
        empty spots in the grid.
        """
        candidates = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.tiles[row][col] is None:
                    pos = (row, col)
                    candidates.append(pos)
        if candidates == []:
            return None
        return random.choice(candidates)

    def place_tile(self):
        """Place a new tile somewhere on the grid.
        New value is always 2.
        (Note:  In the original 2048, there is a 10%
        chance of the new tile being 4.)
        """
        spot = self.find_empty()
        assert(spot)
        row, col = spot
        tile = Tile(self, row, col)
        self.tiles[row][col] = tile
        self.notify("New", data={"tile": tile})

    # Game moves.  Calls the "slide" method on each tile in the
    # grid, with the correct motion vector, and in the correct
    # order.  See game rules in README for more about the order
    # in which tiles must slide.

    def left(self):
        """Slide tiles to the left. Allows tiles to cascade to the left."""
        #[0,-1] is the movement vector for moving down spaces
        movement_vector = [0,-1]
        #aisle refering to the rows being manipulated. Loop initiates.
        for aisle in self.tiles:
            for column in aisle:
                if column:
                    column.slide(self, movement_vector)

    def right(self):
        """Slide tiles to the right. Allows tiles to cascade to the right."""
        #[0,1] is the movement vector for moving down spaces
        movement_vector = [0,1]
        #aisle refering to the rows being manipulated. Loop initiates.
        for aisle in self.tiles:
            #used reversed in order for the rows to be able to cascade left
            for column in reversed(aisle):
                if column:
                    column.slide(self, movement_vector)


    def up(self):
        """Slide tiles up. Allows tiles to cascade up."""
        #[-1,0] is the movement vector for moving up spaces
        movement_vector = [-1,0]
        #aisle refering to the rows being manipulated. Loop initiates.
        for aisle in self.tiles:
            for column in aisle:
                if column:
                    column.slide(self, movement_vector)


    def down(self):
        """Slide tiles down. Allows tiles to cascade down."""
        #[1,0] is the movement vector for moving down spaces
        movement_vector = [1,0]
        #used reversed to have tiles cascade down
        #aisle refering to the rows being manipulated. loop initiates
        for aisle in reversed(self.tiles):
            for column in aisle:
                if column:
                    column.slide(self, movement_vector)


class Tile(Game_Element):
    """A slidy numbered thing."""

    def __init__(self, grid, row, col, value=2):
        super().__init__()
        self.grid = grid
        self.row = row
        self.col = col
        self.value = value

    def slide(self, grid, movement_vector):
        """Slide the tile in given direction
        Note we must update grid as well as
        tile. Movement vector should be a
        pair (dx, dy) where each of dx, dy is
        -1, 0, or 1.  For example, left is (-1, 0).
        """
        dx, dy = movement_vector
        row, col = self.row, self.col
        while True:
            trial_x = row + dx
            trial_y = col + dy
            if not self.grid.in_bounds(trial_x, trial_y):
                # Reached edge of board
                break
            if not self.grid.tiles[trial_x][trial_y]:
                # Slide over empty space
                row, col = trial_x, trial_y
                self.move(self.grid, row, col)
            elif self.grid.tiles[trial_x][trial_y].value == self.value:
                # Matching tile, merge and continue
                row, col = trial_x, trial_y
                self.merge(self.grid.tiles[trial_x][trial_y])
                self.move(self.grid, row, col)
            else:
                # Reached tile with a different value
                break

    def move(self, grid, row, col):
        """Update position"""
        self.grid.tiles[self.row][self.col] = None
        self.row = row
        self.col = col
        self.grid.tiles[row][col] = self
        self.notify("Update")

    def merge(self, other):
        """Let this tile be the sum of it and another"""
        self.value = self.value + other.value
        other.remove()
        self.notify("Update")

    def remove(self):
        self.notify("Remove")

    def __str__(self):
        return str(self.value)
