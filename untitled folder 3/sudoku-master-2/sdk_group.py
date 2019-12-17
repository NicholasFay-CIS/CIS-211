"""
A "group" is a collection of 9 Sudoku tiles, which
may form a row, a column, or a block (aka 'region'
or 'box').

Constraint propagation are localized here.

Nicholas Fay 951566471
"""

from typing import List

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
        self.tiles: List[sdk_tile.Tile] = []

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
        """
        A group is consistent if it has no duplicates,
        every tile has at least one candidate, and
        every value has a place to go. Returns a Boolean value.
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
            # chance to sets
            can_place = can_place | tile.candidates
        if can_place != set(sdk_tile.CHOICES):
            log.debug("Group {}, no place for {}"
                      .format(self, set(sdk_tile.CHOICES) - can_place))
        return can_place == set(sdk_tile.CHOICES)

    def duplicates(self) -> List[str]:
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
        """A choice can be used at most once in the group.
        For each choice that has already been used in the group,
        eliminate that choice as a candidate in all the
        UNKNOWN tiles in the group.
        """
        self.attend()
        changed = False
        # Which values have already been used?
        #  then value X can't be a candidate for any unknown
        #  tile in the group
        used_items = set()  # a set to contain used values
        for tile in self.tiles:  # for each tile being iterated through
            if tile.value != sdk_tile.UNKNOWN:  # if tile value is not empty
                used_items.add(tile.value)  # add it to the used set
        for tile in self.tiles:  # another iteration for if the tile is unknown
            if tile.value == sdk_tile.UNKNOWN:
                changed = tile.eliminate(used_items) or changed  # eliminates the used numbers already used
        self.unattend()
        return changed

    def hidden_single_constrain(self) -> bool:
        """Each choice must be used in the group.
        For each choice that has not already been used
        in the group, if there is exactly one tile in the
        group for which it is a candidate, then that
        tile must hold that choice.  Note this depends
        on narrowing of candidates by naked_single. Hidden
        single can only work in combination with naked single.
        """
        self.attend()
        changed = False
        for integer in sdk_tile.CHOICES:
            # This value has to go somewhere
            tile_tobe = None
            # iterates through the tiles
            for tile in self.tiles:
                if tile.value == integer:
                    # doesnt need to do anything be because it has somewhere to go
                    break
                if tile.could_be(integer):
                    # The first place we have found, that value can go
                    if tile_tobe is None:
                        tile_tobe = tile
                    else:
                        # there is another place for it to associate to
                        break
            else:
                # couldnt find a place to go so this is what happens next
                if tile_tobe:
                    tile_tobe.set_value(integer)
                    changed = True
                    # Otherwise it is inconsistent
        self.unattend()
        return changed


