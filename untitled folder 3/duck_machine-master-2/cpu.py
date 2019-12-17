"""
Duck Machine model DM2018S CPU
Nicholas Fay
"""

from instr_format import Instruction, OpCode, CondFlag, decode
from memory import Memory
from register import Register, ZeroRegister
from alu import ALU
from mvc import MVCEvent, MVCListenable

from typing import List, Tuple

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class CPUStep(MVCEvent):
    """CPU is beginning step with PC at a given address"""
    def __init__(self, subject: "CPU", pc_addr: int, instr_word: int, instr: Instruction)-> None:
        self.subject = subject
        self.pc_addr = pc_addr
        self.instr_word = instr_word
        self.instr = instr

# Create a class CPU, subclassing MVCListenable.
# It should have 16 registers (a list of Register objects),
# and the first of them should be the special ZeroRegister
# object that is always zero regardless of what is stored.
# It should have a CondFlag with the current condition.
# It should have a boolean "Halted" flag, and execution of
# the "run" method should halt with the Halted flag is True
# (set by the HALT instruction). The CPU does not contain
# the memory, but has a connection to a Memory object
# (specifically a MemoryMappedIO object).
# See the project web page for more guidance.


class CPU(MVCListenable):
    """Duck Machine central processing unit (CPU)
    has 16 registers (including r0 that always holds zero
    and r15 that holds the program counter), a few
    flag registers (condition codes, halted state),
    and some logic for sequencing execution.  The CPU
    does not contain the main memory but has a bus connecting
    it to a separate memory.
    """

    def __init__(self, memory):
        """Initializes the CPU class."""
        super().__init__()  # Call to super class
        self.memory = memory  # Not part of CPU; what we really have is a connection
        self.registers = [ZeroRegister(), Register(), Register(), Register(), Register(), Register(), Register(),
                          Register(), Register(), Register(), Register(), Register(), Register(), Register(), Register(), Register()]
        # establishes boolean condflag
        self.condition = CondFlag.ALWAYS
        # sets halt to be false
        self.halted = False
        # call to alu
        self.alu = ALU()
        # Convenient aliases
        self.pc = self.registers[15]

    def step(self) -> None:
        """This is the main function for the program. This deals with the main functionality of
        the assembly code. It has refereneces to memory and instr_format in order to affectivly carry out its operations."""
        log.debug("Step at PC={}".format(self.pc.get()))

        # Fetches instruction address and instruction word
        instr_addr = self.pc.get()
        instr_word = self.memory.get(instr_addr)
        # Decodes the instruction word we just fetched
        instr = decode(instr_word)
        log.debug("Instruction: {}".format(instr))
        # Display the CPU state when we have decoded the instruction,
        # before we have executed it
        self.notify_all(CPUStep(self, instr_addr, instr_word, instr))
        # Execute
        predicate = instr.cond
        if predicate & self.condition:
            log.debug("Predicate passed")
            op_code = instr.op
            # setting the target, right and left variables
            target = self.registers[instr.reg_target]
            left = self.registers[instr.reg_src1].get()
            # the right register is dealing with the offset value
            right = self.registers[instr.reg_src2].get() + instr.offset
            # Step program counter after forming operands but before
            # storing execution result
            self.pc.put(self.pc.get() + 1)
            # Now a store into PC will overwrite the stepped value
            result, cc = self.alu.exec(op_code, left, right)
            self.condition = cc
            # Load and store are special
            # for if the op code is Load
            if op_code == OpCode.LOAD:
                mem_val = self.memory.get(result)
                target.put(mem_val)
            # if the op code reads a Store
            elif op_code == OpCode.STORE:
                self.memory.put(result, target.get())
            # if the op code reads a Halt
            elif op_code == OpCode.HALT:
                self.halted = True
            else:
                target.put(result)
        else:
            # The program counter still moves forward, with no
            # other computation
            log.debug("Predicated instruction will not execute")
            self.pc.put(self.pc.get() + 1)

    def run(self, from_address=0, single_step=False) -> None:
        """This deals with the run time and the halting of the program.
        takes in no parameters as they are already established"""
        self.halted = False
        # from MemoryIO
        self.pc.put(from_address)
        # step counter
        step_count = 0
        # while not a Halt
        while not self.halted:
            if single_step:
                input("Step {}; press enter".format(step_count))
            # call to step function
            self.step()
            # adds to the step counter each step
            step_count += 1


