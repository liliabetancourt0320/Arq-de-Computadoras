module ram_sync (
    output reg [7:0] data_out,
    input [7:0] data_in,
    input [7:0] addr,
    input wr, // Se�al de escritura (1 para escribir, 0 para leer)
    input en, // Se�al de habilitaci�n
    input clk // Se�al de reloj
);

    // Memoria: 256 posiciones de 8 bits
    reg [7:0] memory[0:255];
    
    // Proceso s�ncrono controlado por el flanco de subida del reloj
    always @(posedge clk) begin
        if (en) begin
            if (wr) begin
                // Operaci�n de escritura en el flanco de subida del reloj
                memory[addr] <= data_in;
            end
            // La operaci�n de lectura tambi�n es s�ncrona
            // El dato de la direcci�n 'addr' se carga en 'data_out' en el flanco de subida
            data_out <= memory[addr];
        end
    end
    
endmodule

