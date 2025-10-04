//1.definir modulo.
module HA (input A, input B, output S, output AS);
//2def. cables ,regs e instancias
//3. definir logica del modulo.
assign S = A ^ B;//xor
assign AS = A& B;
endmodule