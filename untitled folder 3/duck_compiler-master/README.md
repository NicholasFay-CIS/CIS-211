# Duck Compiler

This project is a compiler (and an interpreter) for Awl, the Awkward Waterfowl Language or the Adequate Waterfowl Language or something, but definitely not the Aquatic Waterfowl Language because that would be redundant.  

## Recycled code

Out of a sense of environmental responsibility, this compiler is constructed largely from post-consumer waste code, primarily from the Calculator project. However, many parts had to be melted down and recast, and almost every part required at least some small modification. 

## Lost features

Awl has most of the features of our calculator, but it lost one big one:   It no longer works with floating point numbers.  That's because we bought the cheap version of the DM2018S chip, with no floating point coprocessor.  So, it works with integers only. 

## New language features

The first thing you'll notice is that Awl is not postfix.  It is possible to make a postfix language syntax that can be readable with loops, sequencing, and other control structures  (PostScript is one such language), but it requires some tricks that I didn't want to implement.  So instead, Awl is a more conventional language with algebraic notation.  It still requires spaces between tokens. 

Aside from syntax, there are several small additions: 

* A block of code may be a sequence of statements. 
```
x = 5 ; y = 6 ;
```
Notice that assignment statements (but only assignment statements) are terminated with a semicolon. 

* while loops are written like this: 

```
while x do
    fact = fact * x ;
    x = x - 1 ;
od
```

The condition can be any expression.  0 is interpreted as False, and any non-zero value is True.  The block between `do` and `od` is executed as long as the condition (`x` in the example) evaluates to a non-zero value. 

* if/then/else/fi, with an optional else part.  The condition after the `if` is like the condition in the `while` loop, just an expression that evaluates to 0 for False or anything else for True.  In practice that means it is very hard to test for anything but equality.  Here's a program that does use an if/then/else to test for equality: 

```
# In this program, the first input is a value to "watch for"
# in a sequence.  In the rest of the sequence, we count
# occurrences of that value.  The sequence ends with 0.
# We print the count of occurrences of that value.
#
watch = in ;
count = 0 ;
observe = in ;
while observe do
    if watch - observe then
        # do nothing
    else
        count = count + 1 ;
    fi
    observe = in ;
od
out = count ;
```

* printing and reading are done through the special variables `in` and `out`, as in the programs above. 

There is both an interpreter (which uses the `eval` methods of Expr nodes) and a compiler (which uses the `gen` methods).  The interpreter is complete (I think!) and can be used to check out test programs.  The compiler is what you will complete. 

## How to proceed

The only file you should need to change (and the file you will turn in) is expr.py.   I have provided code generation methods for some classes, but you need to provide it for BinOp and its subclasses, and for If.  

Recall that in the symbolic calculator project we factored out most of the 'eval' functionality from PLUS, MINUS, etc. into BinOp, delegating just the `_apply` method to the concrete subclasses.  You must do something similar here:  The concrete subclasses (Plus, Minus, etc) should have an `_opcode` method that returns the DM2018S opcode for the instruction they generate. Write one 'gen' method in BinOp and inherit it in the concrete subclasses.  Do not write a 'gen' method in each concrete subclass of BinOp. 
