# Lovingly crafted by robots
# 2018-06-05 10:23:59.211807 from awl/count_match.awl
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
   SUB  r2,r2,r3
	SUB  r0,r2,r0 
	JUMP/Z elsepart_9
	JUMP endloop_7
elsepart_9: 
	LOAD r1,count_2
	LOAD r2,const1_10  # Const 1
   ADD  r1,r1,r2
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
const1_10:  DATA 1
