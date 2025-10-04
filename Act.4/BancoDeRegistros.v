module BancoDeRegistros(

    input [4:0] RR1,
    input [4:0] RR2,
    input [4:0] WriteRg,
    input [31:0] WriteData,
    input RegWrite,

    output reg [31:0] RD1,
    output reg [31:0] RD2
);

reg [31:0] Banco [0:31];

initial
begin
	$readmemb("Data.txt", Banco);
end

always @*
begin
    if(RegWrite)
    begin
     Banco[WriteRg] = WriteData;
    end

    RD1 = Banco[RR1];
    RD2 = Banco[RR2];
end

endmodule