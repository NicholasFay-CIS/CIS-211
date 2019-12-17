# Lovingly crafted by robots
# 2018-06-05 08:18:19.563413 from awl/count_match.awl
#
	LOAD r1,r0,r0[510]
	STORE  r1,watch_1
	LOAD r1,const0_3  # Const 0
	STORE  r1,count_2
	LOAD r1,r0,r0[510]
	STORE  r1,observe_4
loop_5:  #While loop
	LOAD r2,observe_4
	SUB  r0,r2,r0 
	JUMP/Z endloop_6
	LOAD r2,watch_1
	LOAD r3,observe_4
SUB, r2, r2, r3
	SUB  r0, r2, r0 
	JUMP/Z elsepart_8
	JUMP endif_7
elsepart_8: 
	LOAD r1,count_2
	LOAD r2,const1_9  # Const 1
ADD, r1, r1, r2
	STORE  r1,count_2
	LOAD r1,r0,r0[510]
	STORE  r1,observe_4
	JUMP loop_5
endloop_6: 
	LOAD r1,count_2
	STORE  r1,r0,r0[511]
	HALT  r0,r0,r0
watch_1: DATA 0 #watch
count_2: DATA 0 #count
observe_4: DATA 0 #observe
const0_3:  DATA 0
const1_9:  DATA 1


self.left.gen(context, target)  # step one generate left operand using the same target register
        right_operand = context.alloc_reg()  # Allocate a single register for the right operand
        self.right.gen(context, right_operand)  # generates code for the right operand using the newly allocated register (newly allocated register is the right operand
        op__code = self._opcode()  # get the operation code with _opcode function
        context.add_line("{},{},{},{}".format(op__code, target, target, right_operand))  # generates the instruction using the opcode, target, target right
        context.free_reg(right_operand)  # free the allocated register (which in this instance is for the right operand
        return  # returns None
