"""
Sudoku solution tactics.  These include the
constraint propogation tactics and (in phase
two) the search-based solver.

Author: Nicholas Fay nfay@uoregon.edu 951566471
"""

from sdk_board import Board
import sdk_tile
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
    recursive back-tracking search (guess-and-check with recursion).
    """
    #search(partial solution):
    propagate(board)
    #if the board is solved
    if board.is_solved() == True:
        return True
    #if the board is not solved
    if board.is_consistent() != True:
        #allows us to debug the code we have written
        log.debug("Called consistent on board:\n{}".format(board))
        return False

    #This is because there are 9 total values
    #1-9 Therefore the minimum # of candidates must be one as 0 is not an option
    min_canidates = 10
    #The tile option that makes the most sense to solve the problem
    best_tile = None
    for item in board.tiles:
        for tile in item:
            #apply the step to partial solution
            if tile == sdk_tile.UNKNOWN and len(tile.candidates) < min_canidates:
                # the tile with least amount of candidates
                best_tile = tile
                min_candidates = len(tile.candidates) #updates the minimum number of candidates
    #Saves the current board
    tile=best_tile
    board_as_list = board.as_list()
    #goes through each candidates of the tile
    for candidates in tile.candidates:
        #tile has the value of those candidates
        tile.set_value(candidates)
        #If recursive call returns True, return True
        if solve(board):
            return True
        else:
            #Restores board back to normal
            board.set_tiles(board_as_list)
    # All possible next steps have failed Return False
    return False

    #Given starter code...
    #log.debug("Called solve on board:\n{}".format(board))
    #propagate(board)
    #return board.is_solved()


