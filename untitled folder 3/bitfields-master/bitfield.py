"""
A bit field is a range of binary digits within an
unsigned integer. Bit 0 is the low-order bit,
with value 1 = 2^0. Bit 31 is the high-order bit,
with value 2^31. 

A bitfield object is an aid to encoding and decoding 
instructions by packing and unpacking parts of the 
instruction in different fields within individual 
instruction words. 

Note that we are treating Python integers as if they 
were 32-bit unsigned integers.  They aren't ... Python 
actually uses a variable length signed integer
representation, but we ignore that because we are trying
to simulate a machine-level representation.
Nicholas Fay 951566471
"""

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

WORD_SIZE = 32 


class BitField(object):
    """A BitField object handles insertion and 
    extraction of one field within an integer.
    """
    #    The constructor should take two integers, from_bit and to_bit,
    #    indicating the bounds of the field.  Unlike a Python range, these
    #    are inclusive, e.g., if from_bit=0 and to_bit = 4, then it is a
    #    5 bit field with bits numbered 0, 1, 2, 3, 4.
    #
    #    You might want to precompute some additional values in the constructor
    #    rather than recomputing them each time you insert or extract a value.
    #    I precomputed the field width (used in several places), a mask (for
    #    extracting the bits of interest), the inverse of the mask (for clearing
    #    a field before I insert a new value into it), and a couple of other values
    #    that could be useful to have in sign extension (see the sign_extend
    #    function below).
    #
    #    method insert takes a field value (an int) and a word (an int)
    #    and returns the word with the field value replacing the old contents
    #    of that field of the word.
    #    For example,
    #      if word is   xaa00aa00 and
    #      field_val is x0000000f
    #      and the field is bits 4..7
    #      then insert gives xaa00aaf0
    #
    #   method extract takes a word and returns the value of the field
    #   (which was set in the constructor)
    #
    #   method extract_signed does the same as extract, but then if the
    #   sign bit of the field is 1, it sign-extends the value to form the
    #   appropriate negative integer.  extract_signed could call the function
    #   extract_signed below, but you may prefer to incorporate that logic into
    #   the extract_signed method.
    def __init__(self, from_bit: int, to_bit: int) -> None:
        """Tool for inserting and extracting bits
        from_bit ... to_bit, where 0 is the low-order
        bit and 31 is the high-order bit of an unsigned
        32-bit integer. For example, the low-order 4 bits
        could be represented by from_bit=0, to_bit=3 which is 4 long
        being 0, 1, 2, 3, 4.
        """
        # is from bit greater than or equal to zero but less than 32 bits
        assert 0 <= from_bit < WORD_SIZE
        # is to bit greater than or equal to from bit but less than or equal to 32 bits
        assert from_bit <= to_bit <= WORD_SIZE
        # lower order bits variable
        self.from_bit = from_bit
        # higher order bits variable
        self.to_bit = to_bit
        # a mask for extracting the bits of interest
        self.field_width = 1 + to_bit - from_bit
        # Mask for the field in the low-order bits.
        # the inverse of the field_width mask for clearing a field before insertion of a new value
        # initializes mask variable
        mask = 0
        # makes sure the field width is a greater than or equal to zero
        assert self.field_width >= 0
        for bit in range(self.field_width):
            # shifting to the right by power of the mask
            mask = (mask << 1) + 1
        mask <<= self.from_bit
        # mask variable fully initialized
        self.mask = mask
        # inverse mask for dealing with negatives
        self.mask_inverse = ~mask

    def insert(self, field_value: int, word: int) -> int:
        """Insert value of field into word.
        For example,
          if word is   xaa00aa00 and
          field_val is x0000000f
          and the field is bits 4..7
        then insert gives xaa00aaf0
        This involves using a mask and shifting to the left (or multiplying)
        This is the main function for inserting different place holders into the bit fields. This will give
        the resulting hex character that was created.
        """
        # field value is shifted to the right from the bit its coming from
        position = field_value << self.from_bit
        # the ("position value: " hex(position_value))
        # getting it down to the right size
        # ("clear_value: ", hex(clear_value))
        clear_value = position & self.mask
        # ("clear_char: ", hex(clear_char)
        clear_char = word & self.mask_inverse
        # adds the byte shift and clean word using the or statement (|)
        return clear_char | clear_value

    def extract(self, word: int) -> int:
        """Extract the bitfield and return it in the
        low-order bits.  For example, if we are extracting
        the high-order five bits, the result will be an
        integer between 0 and 31. This requires shifting to the right
        (or dividing).
        """
        # Word with the & operator get shifted to the left back to their original location
        return (word & self.mask) >> self.from_bit

    def extract_signed(self, word: int) -> int:
        """Extract the bitfield and return it in the
        low order bits, sign-extended. This deals with negatives.
        """
        # call to function extract to extract the unsigned bits
        unsigned = self.extract(word)
        # sign_extend if negative
        # returns an integer.
        return sign_extend(unsigned, self.field_width)


# Sign extension is a little bit wacky in Python, because Python
# doesn't really use 32-bit integers ... rather it uses a special
# variable-length bit-string format, which makes *most* logical
# operations work in the extpected way  *most* of the time, but
# with some differences that show up especially for negative
# numbers.  I've written this sign extension function for you so
# that you don't have to spend time plotting a way to make it work.
# You'll probably want to convert it to a method in the BitField
# class.
#
# Examples:
#    Suppose we have a 3 bit field, and the field
#    value is 0b111 (7 decimal).  Since the high
#    bit is 1, we should interpret it as
#    -2^2 + 2^1  + 2^0, or -4 + 3 = -1
#
#    Suppose we hve the same value, decimal 7 or
#    0b0111, but now it's in a 4 bit field.  In thata
#    case we should interpret it as 2^2 + 2^1 + 2^0,
#    or 4 + 2 + 1 = 7, a positive number.
#
#    Sign extension distinguishes these cases by checking
#    the "sign bit", the highest bit in the field.
#
def sign_extend(field: int, width: int) -> int:
    """Interpret field as a signed integer with width bits.
    If the sign bit is zero, it is positive.  If the sign bit
    is negative, the result is sign-extended to be a negative
    integer in Python.
    width must be 2 or greater. field must fit in width bits.
    """
    log.debug("Sign extending {} ({}) in field of {} bits".format(field, bin(field), width))
    assert width > 1
    assert field >= 0 and field < 1 << (width + 1)
    sign_bit = 1 << (width - 1) # will have form 1000... for width of field
    mask = sign_bit - 1         # will have form 0111... for width of field
    if (field & sign_bit):
        # It's negative; sign extend it
        log.debug("Complementing by subtracting 2^{}={}".format(width-1,sign_bit))
        extended = (field & mask) - sign_bit
        log.debug("Should return {} ({})".format(extended, bin(extended)))
        return extended
    else:
        return field

