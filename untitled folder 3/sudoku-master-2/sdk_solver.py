"""
Sudoku solution tactics.  These include the
constraint propogation tactics and (in phase
two) the search-based solver.

Author: Nicholas Fay 951566471
"""

from sdk_board import Board

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def naked_single(board: Board) -> bool:
    """As described in http://www.sadmansoftware.com/sudoku/nakedsingle.php
    Returns True iff some change has been made
    """
    logging.info("Applying naked single tactic")
    changed = False
    for group in board.groups:
        changed = group.naked_single_constrain() or changed
    return changed


def hidden_single(board: Board) -> bool:
    """As described in http://www.sadmansoftware.com/sudoku/hiddensingle.php
    Returns True iff some change has been made
    """
    logging.info("Applying hidden single tactic")
    changed = False
    for group in board.groups:
        changed = group.hidden_single_constrain() or changed
    return changed


def propagate(board: Board):
    """Propagate constraints until we either solve the puzzle,
    show the puzzle as given is unsolvable, or can make no more
    progress by constraint propagation.
    """
    logging.info("Propagating constraints")
    changed = True
    while changed:
        logging.info("Invoking naked single")
        changed = naked_single(board)
        if board.is_solved() or not board.is_consistent():
            return
        changed = hidden_single(board) or changed
        if board.is_solved() or not board.is_consistent():
            return
    return


def solve(board: Board) -> bool:
    """Main solver.  Initially this just invokes constraint
    propagation.  In phase 2 of the project, you will add
    recursive back-tracking search (guess-and-check with recursion)."""
    log.debug("Called solve on board:\n{}".format(board))
    #propogates through the board
    propagate(board)
    #if the board is solved then return True
    if board.is_solved():
        return True
    #if the board is not consistent then return False
    if not board.is_consistent():
        return False
    # There must be at least one tile which is unknown which is represented as '.'
    # and multiple candidate values. Choose one with fewest candidates.
    min_candidates = 999
    best_tile = None
    #for each row on the board with tiles
    for row in board.tiles:
        #for each of those tiles in the row
        for tile in row:
            #if the tile is unknown and the length of the tile canidates is less than min canidates
            if tile.value == '.' and len(tile.candidates) < min_candidates:
                #make the min candidates equal to the length of the candidates for the tile
                min_candidates = len(tile.candidates)
                #the best tile to use is that tile
                best_tile = tile
    tile = best_tile
    #saves the board
    saved = board.as_list()
    for attempt in tile.candidates:
        tile.set_value(attempt)
        #if the board is good return true
        if solve(board):
            return True
        else:
            #Restores old board and trys again
            board.set_tiles(saved)
    return False

"""
#original function before backtracking
def solve(board: Board) -> bool:
    Main solver.  Initially this just invokes constraint
    propagation.  In phase 2 of the project, you will add
    recursive back-tracking search (guess-and-check with recursion).

    log.debug("Called solve on board:\n{}".format(board))
    propagate(board)
    return board.is_solved()
"""

