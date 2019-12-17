"""
A Sudoku board holds a 9x9 matrix of tiles.
Each row and column and also 9 3x3 sub-blocks
are treated as a group of 9 (sometimes called
a 'nonet'); when solved, each group must contain
exactly one occurence of each of the 9 symbols
on the board.

Nicholas Fay 951566471
"""

from typing import List

from events import Event, Listener
from sdk_tile import Tile
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
        self.tiles: List[List[Tile]] = []
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

    def _build_row_groups(self) -> None:
        """This function adds a group for each row. This is dealing with the 9x9 functionality.
        This returns None but has a side affect on the board
        """
        # Range 9 because it is 9x9
        for row in range(9):
            # use range of 9 because 9 rows and 9 columns of spaces in the game
            row_group = Group("Row {}".format(row))
            # for tiles 1-9 (since its is 9x9)
            for tile in range(9):
                # the row dict then adds that tile
                row_group.add(self.tiles[row][tile])
            self.groups.append(row_group)

    def _build_column_groups(self) -> None:
        """Add a group for each column"""
        for col_index in range(9):
            col_group = Group("Column {}".format(col_index))
            for row_index in range(9):
                col_group.add(self.tiles[row_index][col_index])
            self.groups.append(col_group)

    def _build_block_groups(self) -> None:
        """Add a group for each 3x3 block. This is for building the different 3x3 sectors that are being sifted through
        This returns None but has a side affect on the board.
        """
        # range of 3 b/c it is a 3x3 block
        for row in range(3):
            # Length of the rows is 3 blocks for both column and rows
            for column in range(3):
                # format the block group to two arguments of rows and columns
                block_group = Group("Block {}, {}"
                                    .format(row, column))
                # the base is equivelant to the length of the row times 3(3x3)
                row_base = 3 * row
                column_base = 3 * column
                # for shifting the rows to the next block
                for row_change in range(3):
                    # for shifting the rows to the next block
                    for column_change in range(3):
                        tile_for_the_row = row_change + row_base
                        tile_for_the_column = column_base + column_change
                        block_group.add(self.tiles[tile_for_the_row][tile_for_the_column])
                # adds the group of blocks
                self.groups.append(block_group)

    def set_tiles(self, tile_values: List[str]):
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
        """All the constraints are satisfied, so far. Determines if it is consistent. Returns a Boolean"""
        for group in self.groups:
            if not group.is_consistent():
                log.debug("Inconsistent group {}".format(group))
                return False
        return True

    def duplicates(self) -> List[str]:
        """A list of duplicates found in groups"""
        reports = []
        for group in self.groups:
            reports = reports + group.duplicates()
        return reports

    def is_solved(self) -> bool:
        """
        This determines if the game has been solved or not. It also looks to see
        if there is an inconsistentcy occuring. Returns a boolean
        """
        if not self.is_consistent():
            return False
        for row in self.tiles:
            for tile in row:
                if tile.value == '.':
                    return False
        return True

    def __str__(self) -> str:
        return "\n".join(self.as_list())
