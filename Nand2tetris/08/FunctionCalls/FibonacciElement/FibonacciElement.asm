@256
D=A
@SP
M=D
@RETURN_1
D=A
@SP
A=M
M=D
@SP
M=M+1
@1
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=M
@SP
A=M
M=D
@SP
M=M+1
@3
D=M
@SP
A=M
M=D
@SP
M=M+1
@4
D=M
@SP
A=M
M=D
@SP
M=M+1
@5
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(RETURN_1)
(Main.fibonacci)
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=-1
@END_1
D;JLT
@SP
A=M-1
M=0
(END_1)
@SP
AM=M-1
D=M
@IF_TRUE
D;JNE
@IF_FALSE
0;JMP
(IF_TRUE)
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@13
M=D
@5
D=A
@13
A=M-D
D=M
@14
M=D
@SP
M=M-1
@ARG
A=M
D=A
@15
M=D
@SP
A=M
D=M
@15
A=M
M=D
@1
D=A
@ARG
D=D+M
@SP
M=D
@1
D=A
@13
A=M-D
D=M
@THAT
M=D
@2
D=A
@13
A=M-D
D=M
@THIS
M=D
@3
D=A
@13
A=M-D
D=M
@ARG
M=D
@4
D=A
@13
A=M-D
D=M
@LCL
M=D
@14
A=M
0;JMP
(IF_FALSE)
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
A=A-1
M=M-D
@RETURN_2
D=A
@SP
A=M
M=D
@SP
M=M+1
@1
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=M
@SP
A=M
M=D
@SP
M=M+1
@3
D=M
@SP
A=M
M=D
@SP
M=M+1
@4
D=M
@SP
A=M
M=D
@SP
M=M+1
@6
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(RETURN_2)
@ARG
A=M
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
AM=M-1
D=M
A=A-1
M=M-D
@RETURN_3
D=A
@SP
A=M
M=D
@SP
M=M+1
@1
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=M
@SP
A=M
M=D
@SP
M=M+1
@3
D=M
@SP
A=M
M=D
@SP
M=M+1
@4
D=M
@SP
A=M
M=D
@SP
M=M+1
@6
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(RETURN_3)
@SP
AM=M-1
D=M
A=A-1
M=D+M
@LCL
D=M
@13
M=D
@5
D=A
@13
A=M-D
D=M
@14
M=D
@SP
M=M-1
@ARG
A=M
D=A
@15
M=D
@SP
A=M
D=M
@15
A=M
M=D
@1
D=A
@ARG
D=D+M
@SP
M=D
@1
D=A
@13
A=M-D
D=M
@THAT
M=D
@2
D=A
@13
A=M-D
D=M
@THIS
M=D
@3
D=A
@13
A=M-D
D=M
@ARG
M=D
@4
D=A
@13
A=M-D
D=M
@LCL
M=D
@14
A=M
0;JMP
(Sys.init)
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
@RETURN_4
D=A
@SP
A=M
M=D
@SP
M=M+1
@1
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=M
@SP
A=M
M=D
@SP
M=M+1
@3
D=M
@SP
A=M
M=D
@SP
M=M+1
@4
D=M
@SP
A=M
M=D
@SP
M=M+1
@6
D=A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(RETURN_4)
(WHILE)
@WHILE
0;JMP