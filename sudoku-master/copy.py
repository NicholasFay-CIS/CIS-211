"""
A "group" is a collection of 9 Sudoku tiles, which
may form a row, a column, or a block (aka 'region'
or 'box').

Constraint propagation are localized here.
Author: Nicholas Fay, nfay@uoregon.edu 951566471
Worked with: Remy Reese
"""
import typing
from typing import Sequence

import sdk_tile

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Group(object):
    """A group of 9 Sudoku tiles"""

    def __init__(self, title: str):
        """Intially empty.  The title is just for debugging."""
        self.title = title
        self.tiles:Sequence[sdk_tile.Tile] = []

    def add(self, tile: sdk_tile.Tile):
        """Add a tile to this group"""
        assert len(self.tiles) < 9
        self.tiles.append(tile)

    def __str__(self):
        """Represent as string of values"""
        values = []
        for tile in self.tiles:
            values.append(tile.value)
        return self.title + " " + "".join(values)

    def attend(self):
        """Announce that we are working on these tiles.  A view component
        may make this visible.
        """
        for tile in self.tiles:
            tile.attend()

    def unattend(self):
        """Announce that we are done working on these tiles for now"""
        for tile in self.tiles:
            tile.unattend()

    def is_complete(self) -> bool:
        """A group is complete if all of its tiles hold a
        value (not the wild-card symbol UNKNOWN)
        """
        for tile in self.tiles:
            if tile.value == sdk_tile.UNKNOWN:
                return False
        return True

    def is_consistent(self) -> bool:
        """A group is consistent if it has no duplicates,
        every tile has at least one candidate, and
        every value has a place to go.
        """
        can_place = set()
        used = set()
        for tile in self.tiles:
            # At least one candidate?
            if len(tile.candidates) == 0:
                log.debug("No candidates for tile {},{}:{}"
                          .format(tile.row, tile.col, tile.value))
                return False
            # Duplicate checking
            if tile.value in used:
                # Duplicate!
                log.debug("Tile {},{}:{} is a duplicate"
                          .format(tile.row, tile.col, tile.value))
                return False
            elif tile.value != sdk_tile.UNKNOWN:
                used.add(tile.value)
            # A place for every tile?
            #chance to sets
            can_place = can_place | tile.candidates
        if can_place != set(sdk_tile.CHOICES):
            log.debug("Group {}, no place for {}"
                      .format(self, set(sdk_tile.CHOICES) - can_place))
        return can_place == set(sdk_tile.CHOICES)

    def duplicates(self) -> Sequence[str]:
        """One line report per duplicate found"""
        reports = []
        used = set()
        for tile in self.tiles:
            if tile.value == sdk_tile.UNKNOWN:
                continue
            elif tile.value in used:
                reports.append("Duplicate in {}: {}, value {}"
                               .format(self.title, self, tile.value))
        return reports

    # ---------------------------------
    # Constraint propagation in a group
    # ----------------------------------
    def naked_single_constrain(self) -> bool:
        """A choice can be used at most once in the group."""
        self.attend()
        changed = False
        # Which values have already been used?
        #  then value X can't be a candidate for any unknown
        #  tile in the group
        used_items = set() #a set to contain used values
        for tile in self.tiles: #for each tile being iterated through
            if tile.value != sdk_tile.UNKNOWN: #if tile value is not empty
                used_items.add(tile.value) #add it to the used set
        for tile in self.tiles: #another iteration for if the tile is unknown
            if tile.value == sdk_tile.UNKNOWN:
                tile.eliminate(used_items) #eliminates the used numbers already used
                if tile.eliminate(used_items) == True:
                    changed = True
        self.unattend()
        return changed

    def hidden_single_constrain(self) -> bool:
        """Each choice must be used in the group"""
        #   group that can hold value X, then that tile
        #   must hold value X
        self.attend()
        changed = False
        x = 0
        for integer in sdk_tile.CHOICES:
            TiletoBe = None
            for tile in self.tiles:
                if tile.value == integer:
                    break
                if tile.could_be(integer):
                    #stores this value
                    if TiletoBe == None:
                        break
                    else:
                        TiletoBe = tile
                        changed = True
            if tile != None:
                tile.set_value(integer)
                changed = True
        self.unattend()
        return changed


#from sdk_group.py to

"""
Sudoku Tile objects hold both a current
value and constraints on possible values.
Each tile may belong to more than one group
(nonet), and be constrained by selected values
of other tiles in any of its groups.

Author: Nicholas Fay, nfay@uoregon.edu 951566471
Worked with: Remy Reese
"""
import typing
from typing import Set, Sequence

# MVC listener interface definition
from events import Event, Listener

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Some globals that could be used to customize the
# board, e.g., using symbols other than '0'..'9' for
# tiles.
CHOICES = ['1', '2', '3', '4', '5',
           '6', '7', '8', '9']
UNKNOWN = '.'

# -------------------------------
# Interface for listeners
#  (Notes on design decision at end of this file)
# -------------------------------


class TileEvent(Event):
    """Abstract base class for things that happen
    to tiles. We always indicate the tile.  Concrete
    subclasses indicate the nature of the event.
    """

    def __init__(self, tile: 'Tile'):
        self.tile = tile
        # Note 'Tile' type is a forward reference;

    def __str__(self):
        """Printed representation includes name of concrete subclass"""
        return "{}[{},{}]:{}/{}".format(
            type(self).__name__, self.row, self.col,
            self.value, self.candidates)

# A subclass for each kind of event


class TileChanged(TileEvent):
    """Something has changed, either value or candidates"""
    pass


class TileGuessed(TileEvent):
    """This value change is a guess by the back-track solver"""
    pass


class TileAttend(TileEvent):
    """This tile currently participating in constraint propagation"""
    pass


class TileUnattend(TileEvent):
    """Done with this tile for now"""
    pass


class TileListener(Listener):
    def notify(self, event: TileEvent):
        raise NotImplementedError(
            "TileListener subclass needs to override notify(TileEvent)")

# ------------------------------
#  Tile class
# ------------------------------


class Tile(object):
    """One tile on the Sudoku grid.
    Public attributes (read-only): value, which will be either
    UNKNOWN or an element of CHOICES; candidates, which will
    be a set drawn from CHOICES.  If value is an element of
    CHOICES,then candidates will be the singleton containing
    value.  If candidates is empty, then no tile value can
    be consistent with other tile values in the grid.

    value and candidates are public read-only attributes; change them
    only through the access methods set_value and eliminate.
    """

    def __init__(self, row: int, col: int, value=UNKNOWN):
        assert value == UNKNOWN or value in CHOICES
        self.row = row
        self.col = col
        self.listeners = []
        self.set_value(value)

    def add_listener(self, listener: TileListener):
        """Listener will be notified of changes"""
        self.listeners.append(listener)

    def notify_all(self, event: TileChanged):
        """Notify each MVC listener that something has happened"""
        for listener in self.listeners:
            listener.notify(event)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return "Tile({},{},'{}')".format(self.row, self.col, self.value)

    def set_value(self, value, guess=False):
        if value in CHOICES:
            self.value = value
            self.candidates = set([value])
        else:
            self.value = UNKNOWN
            self.candidates = set(CHOICES)
        if guess:
            self.notify_all(TileGuessed(self))
        else:
            self.notify_all(TileChanged(self))

    def could_be(self, value: str) -> bool:
        """Could this tile take the value
        return value in self.candidates
        """
        return value in self.candidates

    def eliminate(self, choices: Set[str]) -> bool:
        """Eliminate the choices from candidates for
        this tile.  May result in either setting the
        value of this tile (if only one candidate remains)
        or making this tile inconsistent. Triggers a
        Changed event if there is any change.
        Returns True iff value is changed
        """
        # Careful! If you want to compare the value
        # of candidates before and after the operation,
        # you'll need to make a *copy* of the set, because
        # sets are mutable!

        #creates a copy list of candidates
        past_candidates = self.candidates.copy()

        #this eliminates the choices from candidates for the tile.
        self.candidates -= choices

        #if the candidate is the same as one before it it returns false
        if past_candidates == self.candidates:
            return False

        #if only one candidate then copys data and pops off last value
        if len(self.candidates) == 1:
            #pop off last value because you dont want to alter the original.
            # You want the only value in the list that is created
            self.value = self.candidates.copy().pop()
            #Relays the message of the tile change
            self.notify_all(TileChanged(self))
            return True

        #if length = 0
        elif len(self.candidates) == 0:
            # updates tile returns true
            self.notify_all(TileChanged(self))
            return True

        else:
            #updates tile returns true
            self.notify_all(TileChanged(self))
            return True


    def attend(self):
        """This tile is currently an object of attention"""
        self.notify_all(TileAttend(self))

    def unattend(self):
        """Done attending to this tile"""
        self.notify_all(TileUnattend(self))

# Design notes:
#    We want different kinds of tile events to guide
# view components in what to display (without putting
# those view design decisions here). I have chosen to
# create different TileEvent subclasses to indicate
# the event types.
#
# An alternative would be to pass a data value to indicate
# the event type. We could define symbolic constants
# to reduce the chance of hard-to-debug typographical errors,
# and we could use a Python Enum class to define those
# symbolic constants.  Enums do not act like other classes in
# Python, so I am reluctant to introduce them in this project.
#
# Using subclasses as I have here is almost like defining an
# Enum.  An advantage is that we could, if we needed to,
# add additional fields in a subclass for a particular event
# type.  A disadvantage is that we need to use the isinstance()
# method (usually in the view component) to determine which
# event type it is.


"""
A Sudoku board holds a 9x9 matrix of tiles.
Each row and column and also 9 3x3 sub-blocks
are treated as a group of 9 (sometimes called
a 'nonet'); when solved, each group must contain
exactly one occurence of each of the 9 symbols
on the board.
Author: Nicholas Fay, nfay@uoregon.edu 951566471
Worked with: Remy Reese
"""

import typing
from typing import Sequence, Set, List

from events import Event, Listener
from sdk_tile import Tile, CHOICES, UNKNOWN
from sdk_group import Group

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# -------------------------------
# Interface for listeners
# -------------------------------


class BoardEvent(Event):
    """Abstract base class for things that happen
    to tiles. We always indicate the tile.  Concrete
    subclasses indicate the nature of the event.
    """

    def __init__(self):
        pass


class BoardListener(Listener):
    def notify(self, event: BoardEvent):
        raise NotImplementedError(
            "BoardListener subclass needs to override notify(BoardEvent)")

# ------------------------------
#  Board class
# ------------------------------


class Board(object):
    """A board has a matrix of tiles indexed 0..9, 0..9"""

    def __init__(self):
        """The empty board"""
        # Row/Column structure: Each row contains columns
        self.tiles: Sequence[sdk_tile.Tile] = []
        for row in range(9):
            cols = []
            for col in range(9):
                cols.append(Tile(row, col))
            self.tiles.append(cols)
        self._form_groups()

    def _form_groups(self):
        """Build a group for each row, column, and block """
        self.groups = []
        self._build_row_groups()
        self._build_column_groups()
        self._build_block_groups()

    def _build_row_groups(self):
        """Add a group for each row"""
        #Range 9 because it is 9x9
        for row in range(9):
            #use range of 9 because 9 rows and 9 columns of spaces in the game
            row_group = Group("Row {}".format(row))
            #for tiles 1-9 (since its is 9x9)
            for tile in range(9):
                #the row dict then adds that tile
                row_group.add(self.tiles[row][tile])
            self.groups.append(row_group)


    def _build_column_groups(self):
        """Add a group for each column"""
        for col_index in range(9):
            col_group = Group("Column {}".format(col_index))
            for row_index in range(9):
                col_group.add(self.tiles[row_index][col_index])
            self.groups.append(col_group)

    def _build_block_groups(self):
        """Add a group for each 3x3 block"""
        #range of 3 b/c it is a 3x3 block
        for row in range(3):
            #Length of the rows is 3 blocks for both column and rows
            for column in range(3):
                #format the block group to two arguments of rows and columns
                block_group = Group("Block {}, {}"
                                    .format(row, column))
                #the base is equivelant to the length of the row times 3(3x3)
                row_base = 3*row
                column_base = 3*column
                #for shifting the rows to the next block
                for row_change in range(3):
                    #for shifting the rows to the next block
                    for column_change in range(3):
                        tile_for_the_row = row_change + row_base
                        tile_for_the_column = column_base + column_change
                        block_group.add(self.tiles[tile_for_the_row][tile_for_the_column])
                #adds the group of blocks
                self.groups.append(block_group)



    def set_tiles(self, tile_values: Sequence[Sequence[str]]):
        """Set the tile values a list of lists or a list of strings"""
        for row_num in range(9):
            for col_num in range(9):
                tile = self.tiles[row_num][col_num]
                tile.set_value(tile_values[row_num][col_num])

    def as_list(self) -> List[str]:
        """Get tile values in a format for printing or for
        saving and later restoring with set_tiles
        """
        rep = []
        for row in self.tiles:
            row_rep = []
            for tile in row:
                row_rep.append(str(tile))
            rep.append("".join(row_rep))
        return rep

    def is_consistent(self) -> bool:
        """All the constraints are satisfied, so far"""
        for group in self.groups:
            if not group.is_consistent():
                log.debug("Inconsistent group {}".format(group))
                return False
        return True

    def duplicates(self) -> Sequence[str]:
        """A list of duplicates found in groups"""
        reports = []
        for group in self.groups:
            reports = reports + group.duplicates()
        return reports

    def is_solved(self) -> bool:
        """Are we there yet?
        This determines if the game has been solved or not
        """
        for groups in self.groups:
            if not groups.is_complete():
                log.debug("Is not solved {}".format(groups))
                return False
        return True

    def __str__(self) -> str:
        return "\n".join(self.as_list())