`timescale 1ns/1ps

module BurritoTB;

reg RegWrite;
reg [4:0] Addr_op1;
reg [4:0] Addr_op2;
reg [4:0] Addr_Destino;
reg [2:0] Operacion;

Burrito dut (
	.RegWrite(RegWrite),
	.Addr_op1(Addr_op1),
	.Addr_op2(Addr_op2),
	.Addr_Destino(Addr_Destino),
	.Operacion(Operacion)
);

initial
begin
	RegWrite = 0;
	#10;

	RegWrite = 1;
	Addr_op1 = 1;
	Addr_op2 = 2;
	Addr_Destino = 5;
	Operacion = 3'b000;
	#10;

	Addr_op1 = 3;
	Addr_op2 = 1;
	Addr_Destino = 6;
	Operacion = 3'b001;
	#10;

	Addr_op1 = 5;
	Addr_op2 = 6;
	Addr_Destino = 7;
	Operacion = 3'b010;
	#10;

	RegWrite = 0;
	#10;
	$finish;
end

endmodule
