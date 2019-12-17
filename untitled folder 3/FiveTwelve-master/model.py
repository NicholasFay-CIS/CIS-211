"""
The game state and logic (model component) of 512, 
a game based on 2048 with a few changes. 
This is the 'model' part of the model-view-controller
construction plan.  It must NOT depend on any
particular view component, but it produces event 
notifications to trigger view updates.

Nicholas Fay 951566471
Problems attempted for extra credit:
problem 1: Completed. Code not commented out program still ran test results okay.
Problem 2: Completed. Code not commented out program still ran test results okay.
Problem 3: Completed. Code not commented out program still ran test results okay.
Problem 4: Completed. Commented out the code as it gave some errors. The code is still there. It is in the slide function at the bottom.
"""

import random
from enum import Enum
from typing import List, Tuple, Optional

# Configuration constants
GRID_SIZE = 4

# --- Interface for 'View' objects to connect and listen


class EventKind(Enum):
    """All the kinds of events that we may notify listeners of"""
    tile_created = 1
    tile_updated = 2
    tile_removed = 3


class GameEvent(object):
    """An event that may need to be depicted
    """
    def __init__(self, kind: EventKind,  tile: "Tile"):
        self.kind = kind
        self.tile = tile

    def __repr__(self):
        return "GameEvent({}, {})".format(self.kind, self.tile)


class GameListener(object):
    """Abstract base class for objects that listen to
    game events in a model-view-controller pattern.
    Each listener must implement a 'notify' method.
    """
    def notify(self, event: GameEvent):
        raise NotImplementedError("Game Listener classes must implement 'notify'")

# -------------------------------------------


class GameElement(object):
    """Base class for game elements, especially to support
    depiction through Model-View-Controller.
    """

    def __init__(self):
        """Each game element can have zero or more listeners.
        Listeners are view components that react to notifications.
        """
        self._listeners = []

    def add_listener(self, listener: GameListener):
        self._listeners.append(listener)

    def notify_all(self, event: GameEvent):
        """Instead of handling graphics in the model component,
        we notify view components of each significant event and let
        the view component decide how to adjust the graphical view.
        When additional information must be packaged with an event,
        it goes in the optional 'data' parameter.
        """
        for listener in self._listeners:
            listener.notify(event)


class Grid(GameElement):
    """The game grid."""

    def __init__(self):
        super().__init__()
        self.rows = GRID_SIZE
        self.cols = GRID_SIZE
        # Initialize tiles as a matrix of "None" (empty)
        self.tiles = []
        #self._score = 0
        for row in range(self.rows):
            columns = []
            for col in range(self.cols):
                columns.append(None)
            self.tiles.append(columns)

    def __str__(self):
        """String representation like list of lists"""
        rep = []
        for row in self.tiles:
            labels = [str(x) for x in row]
            rep.append("[{}]".format(",".join(labels)))
        return "[{}]".format(",".join(rep))

    def in_bounds(self, row: int, col: int) -> bool:
        """True if (row,col) are valid row and column of grid"""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def as_list(self) -> List[List[int]]:
        """Grid as a list of lists of numbers; for serialization
        and especially for testing. 0 represents an empty tile.
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

    def set_tiles(self, rep: List[List[int]]):
        """Set tiles to a saved configuration, which must
        have the correct dimensions (e.g., 4 rows of 4 columns
        if grid size is 4). 0 represents an empty tile.
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
                    self.notify_all(GameEvent(EventKind.tile_created, tile))
            self.tiles.append(row_tiles)

    def score(self) -> int:
        """The score is the total value of all tiles.
        Note this differs from 2048 scoring rule.
        """
        sum = 0
        for row in self.tiles:
            for col in row:
                if col:
                    sum += col.value
        return sum

    # Game logic
    def find_empty(self) -> Optional[Tuple[int, int]]:
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
        assert spot is not None
        row, col = spot
        rand = random.random() #random val either 0 or 1
        if rand <= .1: #10% probability of a 4
            tile = Tile(self, row, col, 4)
        else:
            tile = Tile(self, row, col) #else leave the value at 2
        #tile = Tile(self, row, col) #part given in original code
        self.tiles[row][col] = tile
        self.notify_all(GameEvent(EventKind.tile_created, tile))

    # Game moves for the left, right, up, down Keypresses
    def left(self) -> None:
        """
        Slide tiles to the left, allows tiles to cascade to the left.
        The side affect is the shifting of tiles
        Self -> None.
        """
        # This is the movement vector for moving left
        movement_v = [-1, 0]
        # for each row in tiles list
        for row in self.tiles:
            #for each column in that row
            for col in row:
                if col:
                    col.slide(movement_v) #slides and updates the tile

    def right(self) -> None:
        """
        Slide tiles to the right, this involves the tiles cascading to the right.
        The side affect is the shifting of tiles
        Self -> None
        """
        movement_v = [1, 0]
        # 0, 1 is the movement vector for moving right
        for row in self.tiles:
            #use reversed so they can cascade to the left. It is the opposite of left (logic). If there is no reversed then the execution will not be accurate.
            for col in reversed(row):
                if col:
                    col.slide(movement_v) #slides and updates the tile

    def up(self) -> None:
        """
        Slide tiles up, as well as cascading up and cascading up.
        The side affect is the shifting of tiles
        Self -> None
        """
        # -1, 0 is the movement vector for this movement. This means that when this action is called the tiles should slide to the x point -1 and y point 0
        movement_v = [0, -1]
        #row is the rows being manipulated. Loop initiates.
        for row in self.tiles:
            for col in row:
                if col:
                    col.slide(movement_v) #slides and updates the tile

    def down(self) -> None:
        """
        Slide tiles down, allows tiles to cascade down.
        The side affect is the shifting of tiles
        Self -> None
        """
        # 1, 0 is the movement vector for moving down
        movement_v = [0, 1]
        #reversed allows the tiles to cascade. It is the reverse of up (logic). If this wasnt put in one may get errors or failurs in results.
        for row in reversed(self.tiles):
            for col in row:
                if col:
                    col.slide(movement_v) #slides and updates the tile


class Tile(GameElement):
    """A slidy numbered thing."""

    def __init__(self, grid: Grid, row: int, col: int, value=2):
        super().__init__()
        self.grid = grid
        self.row = row
        self.col = col
        self.value = value


    def __repr__(self):
        """Not like constructor --- more useful for debugging"""
        return "Tile({}) at {},{}".format(self.value, self.row, self.col)

    def __str__(self):
        return str(self.value)

    def slide(self, movement_vector: Tuple[int, int]):
        """Slide the tile in given direction
        Note we must update grid as well as
        tile.
        """
        dx, dy = movement_vector
        row, col = self.row, self.col
        while True:
            trial_x = row + dy
            trial_y = col + dx
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
                #break this is for EC #4
            else:
                # Reached tile with a different value
                break

    def move(self, grid, row, col):
        """Update position"""
        self.grid.tiles[self.row][self.col] = None
        self.row = row
        self.col = col
        self.grid.tiles[row][col] = self
        self.notify_all(GameEvent(EventKind.tile_updated, self))

    def merge(self, other):
        """This tile absorbs other tile"""
        self.value = self.value + other.value
        other.remove()
        self.notify_all(GameEvent(EventKind.tile_updated, self))

    def remove(self):
        self.notify_all(GameEvent(EventKind.tile_removed, self))

