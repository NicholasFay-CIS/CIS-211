"""
Temp testing new pattern
Nicholas Fay
951566471: nfay@uoregon.edu
"""

from instr_format import Instruction
import memory
import argparse

from typing import Union, List
from enum import Enum, auto

import sys
import io
import re
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Configuration constants
ERROR_LIMIT = 5    # Abandon assembly if we exceed this


# Exceptions raised by this module
class SyntaxError(Exception):
    pass

###
# The whole instruction line is encoded as a single
# regex with capture names for the parts we might want. We can see
# a dict containing the captured fields, we can determine
# which optional parts are present (e.g., there could be
# label without an instruction or an instruction without
# a label).
###


# To simplify client code, we want to return a dict with
# the right fields even if the line is syntactically incorrect.
DICT_NO_MATCH = { 'label': None, 'opcode': None, 'predicate': None,
                      'target': None, 'src1': None, 'src2': None,
                      'offset': None, 'comment': None }


###
# Although the DM2018S instruction set is simple, a source
# line can still come in several forms.  Each form (even comments)
# can start with a label.
###

class AsmSrcKind(Enum):
    """Distinguish which kind of assembly language instruction
    we have matched.  Each element of the enum corresponds to
    one of the regular expressions below.
    """
    # Blank or just a comment, optionally
    # with a label
    COMMENT = auto()
    # Fully specified  (all addresses resolved)
    FULL = auto()
    # A data location, not an instruction
    DATA = auto()
    SYM = auto()


# Lines that contain only a comment (and possibly a label).
# This includes blank lines and labels on a line by themselves.
#
ASM_COMMENT_PAT = re.compile(r"""
   # Optional label
   (
     (?P<label> [a-zA-Z]\w*):
   )?
   \s*
   # Optional comment follows # or ;
   (
     (?P<comment>[\#;].*)
   )?
   \s*$
   """, re.VERBOSE)

# Instructions with fully specified fields. We can generate
# code directly from these.  In the transformation phase we
# pass these through unchanged, just keeping track of how much
# room they require in the final object code.
ASM_FULL_PAT = re.compile(r"""
   # Optional label
   (
     (?P<label> [a-zA-Z]\w*):
   )?
   # The instruction proper
   \s*
    (?P<opcode>    [a-zA-Z]+)           # Opcode
    (/ (?P<predicate> [a-zA-Z]+) )?   # Predicate (optional)
    \s+
    (?P<target>    r[0-9]+),            # Target register
    (?P<src1>      r[0-9]+),            # Source register 1
    (?P<src2>      r[0-9]+)             # Source register 2
    (\[ (?P<offset>[-]?[0-9]+) \])?     # Offset (optional)
   # Optional comment follows # or ;
   (
     \s*
     (?P<comment>[\#;].*)
   )?
   \s*$
   """, re.VERBOSE)

# Defaults for values that ASM_FULL_PAT makes optional
INSTR_DEFAULTS = [ ('predicate', 'ALWAYS'), ('offset', '0') ]

# A data word in memory; not a DM2018W instruction
#
ASM_DATA_PAT = re.compile(r"""
   # Optional label
   (
     (?P<label> [a-zA-Z]\w*):
   )?
   # The instruction proper
   \s*
    (?P<opcode>    DATA)           # Opcode
   # Optional data value
   \s*
   (?P<value>  (0x[a-fA-F0-9]+)
             | ([0-9]+))?
    # Optional comment follows # or ;
   (
     \s*
     (?P<comment>[\#;].*)
   )?
   \s*$
   """, re.VERBOSE)

ASM_SYM_PAT = re.compile(r"""
   # Optional label
   (
     (?P<label> [a-zA-Z]\w*):
   )?
   # The instruction proper
   \s*
    (?P<opcode>   (JUMP) | (STORE) | (LOAD))         # Opcode
    (/ (?P<predicate> [a-zA-Z]+) )?   # Predicate (optional)
    \s+
    ((?P<target>    r[0-9]+),)?            # Target register
    (?P<symbol>     [a-zA-Z]\w*)          #looking through alphabet
   # Optional comment follows # or ;
   (
     \s*
     (?P<comment>[\#;].*)
   )?
   \s*$
   """, re.VERBOSE)

# This is a tuple of possible matching algorithms
PATTERNS = [(ASM_FULL_PAT, AsmSrcKind.FULL),
            (ASM_DATA_PAT, AsmSrcKind.DATA),
            (ASM_COMMENT_PAT, AsmSrcKind.COMMENT),
            (ASM_SYM_PAT, AsmSrcKind.SYM)
            ]


def parse_line(line: str) -> dict:
    """Parse one line of assembly code.
    Returns a dict containing the matched fields,
    some of which may be empty.  Raises SyntaxError
    if the line does not match assembly language
    syntax. Sets the 'kind' field to indicate
    which of the patterns was matched.
    """
    log.debug("\nParsing assembler line: '{}'".format(line))
    # Try each kind of pattern in the list of tuples
    for pattern, kind in PATTERNS:
        # if the pattern is fully matched
        match = pattern.fullmatch(line)
        # if match is True
        if match:
            # matches dictionary
            fields = match.groupdict()
            fields["kind"] = kind
            log.debug("Extracted fields {}".format(fields))
            # returns the extracted fields
            return fields
    raise SyntaxError("Assembler syntax error in {}".format(line))


def resolve_labels(lines: List[str]) -> tuple:
    """
    First Pass
    Build table - dictionary that maps labels to addresses
    Go through each line
    if the line has a label, then put the label and its corresponding address in the dict
    if it is not a comment-type line (use regex to figure this out), then increment our address
    The Tuple that is returned will include a count for the number of syntax errors, key errors, and exceptions.
    """
    # error counter
    error_count = 0
    # variable to represent the symbol table
    symbol_table = {}
    # variable for the address counter
    address_count = 0
    # iterates through the assembly code
    for lnum in range(len(lines)):
        line = lines[lnum]
        # tells the user what line is being processed
        log.debug("Processing line {}: {}".format(lnum, line))
        try:
            fields = parse_line(line)
            # any kind of line
            if fields["label"]:
                dic = fields["label"]
                if dic in symbol_table:
                    # detects duplicates and adds to the error count
                    print("Duplication error {} on line {}".format(dic, lnum))
                    error_count += 1
                else:
                    symbol_table[dic] = address_count
            # if it is a comment
            if fields["kind"] != AsmSrcKind.COMMENT:
                address_count += 1
        # error counter: Syntax error
        except SyntaxError as e:
            error_count += 1
            print("Syntax error in line {}: {}".format(lnum, line))
        # error counter: Unknown word/ character
        except KeyError as e:
            error_count += 1
            print("Unknown word in line {}: {}".format(lnum, e))
        # error counter: notices exceptions that are encountered
        except Exception as e:
            error_count += 1
            print("Exception encountered in line {}: {}".format(lnum, e))
        # If the error count is greater than the error limit
        if error_count > ERROR_LIMIT:
            print("Too many errors; abandoning")
            sys.exit(1)
    # returns tuple of dictionary and integer
    return tuple((symbol_table, error_count))


def test_match(s: str) -> None:
    """This tests to see if the opcode is matched or not. It will print if the opcode has been matched or not"""
    match = ASM_SYM_PAT.match(s)
    # If there is a match
    if match:
        print("Matched {}, \nfields {}".format(s, match.groupdict()))
    else:
        print("Didn't match {}".format(s))


def transform_instructions(lines: List[str], symbolic_table: dict) -> None:
    """
    Second Pass
    going through all the lines again
    in order to calculate the "pc-relative-address" for resolving - need to know:
    where we are in our program (i.e. another address counter will show up here)
    """
    # address counter
    address_count = 0
    # iterates through the opcode
    for lnum in range(len(lines)):
        line = lines[lnum]
        # call to parse line to get needed dictionary
        field = parse_line(line)
        if field["kind"] == AsmSrcKind.SYM:
            lines[lnum] = build_resolved(symbolic_table, field, address_count)
        # if it is not a comment, increment the address counter
        if field["kind"] != AsmSrcKind.COMMENT:
            address_count += 1


def build_resolved(symbolic_table: dict, fields: dict, address_counter: int) -> str:
    """
    used by transform_instructions function
    take a dictionary of fields -> correctly formatted string
    use the .format method a lot here
    will need several cases, one for each load, store, jump
    """
    # creates variable for op code
    op = fields["opcode"]
    predicate = fields["predicate"]
    # if predicate exists: which it should
    if predicate:
        predicate = "/{}".format(predicate)
    else:
        # predicate is empty or null
        predicate = ""
    # creates variable for target
    target = fields["target"] or "r0"
    # If there is a label
    if fields["label"] == None:
        # if label is null
        label = ""
    else:
        # if label is not null
        label = "{}: ".format(fields["label"])
    # creates a variable for symbol
    symbol = fields["symbol"]
    # If symbol isnt in table, raise undefined error
    if symbol not in symbolic_table:
        raise SyntaxError("Use of undefined label: {}".format(symbol))
    relative = symbolic_table[symbol] - address_counter
    # If the opcode is Store or load
    if op == "STORE" or op == "LOAD":
        operand = fields["target"]
        return "{} {} {},r0,r15[{}]".format(label, op, target, relative)
    # If the opcode is a jump
    elif op == "JUMP":
        return "{}  ADD{} r15,r0,r15[{}]".format(label, predicate, relative)
    else:
        # Hopefully the code isnt reading false
        assert False, "should not reach this point"


def cli() -> object:
    """Get arguments from command line"""
    parser = argparse.ArgumentParser(description="Duck Machine Assembler (pass 2)")
    parser.add_argument("sourcefile", type=argparse.FileType('r'),
                            nargs="?", default=sys.stdin,
                            help="Duck Machine assembly code file")
    parser.add_argument("outfile", type=argparse.FileType('w'),
                            nargs="?", default=sys.stdout,
                            help="Object file output")
    args = parser.parse_args()
    return args


def main():
    """"Assemble a Duck Machine program"""
    # call to get arguments from the command line
    args = cli()
    # reads the lines from the sourcefile
    lines = args.sourcefile.readlines()
    # tuple is used to symbol table and error counter
    symbol_table, error_count = resolve_labels(lines)
    # If there are no errors, then we can make the dasm file we want.
    if error_count == 0:
        # increments the address counter and refers back to assembly instructional code
        # call to transform_instructions
        transform_instructions(lines, symbol_table)
        for line in lines:
            # prints onto the object file being created
            print(line.strip(), file=args.outfile)

# this calls the main function
if __name__ == "__main__":
    main()

