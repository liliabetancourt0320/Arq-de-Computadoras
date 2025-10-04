module ALU(
	input [31:0] op1,
	input [31:0] op2,
	input [2:0] op_sel,
	output reg [31:0] result
);

always @(*)
begin
	case(op_sel)
		3'b000: result = op1 + op2;
		3'b001: result = op1 - op2;
		3'b010: result = op1 & op2;
		3'b011: result = op1 | op2;
		default: result = 32'hxxxxxxxx;
	endcase
end

endmodule