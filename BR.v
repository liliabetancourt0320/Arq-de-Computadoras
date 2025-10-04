module BR(
    input clk,
    input [4:0] AR1,
    input [4:0] AR2,
    input [4:0] AWrite,
    input [31:0] DataIn,
    input RegWrite,
    output [31:0] DR1,
    output [31:0] DR2
);

reg [31:0] Banco[0:31];

// Precarga de valores desde el archivo externo, como lo pide el profesor.
initial
begin
    $readmemb("Datos.txt", Banco);
end

// La lectura es instantánea.
assign DR1 = Banco[AR1];
assign DR2 = Banco[AR2];

// La escritura solo ocurre en el pulso del reloj para evitar errores.
always @(posedge clk)
begin
    if (RegWrite)
    begin
        Banco[AWrite] <= DataIn;
    end
end

endmodule

