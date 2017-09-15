// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
	@R2
	M = 0

	@R1
	D = M
	@i
	M = D

	@R0
	D = M
	@END
	D;JEQ

(LOOP)
	@i
	D = M
	@END
	D;JEQ

	@i
	M = M - 1    // i = i - 1

	@R0
	D = M
	@R2
	M = D + M   // R2 = R2 + R0
	@LOOP
	0;JMP
(END)
@END
0;JMP
