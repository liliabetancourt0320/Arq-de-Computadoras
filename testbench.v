`timescale 1ns / 1ps

module testbench;
    reg clk;
    reg reset;

    // Instanciar el procesador
    mips_pipeline uut (
        .clk(clk), 
        .reset(reset)
    );

    // Generador de Reloj
    initial begin
        clk = 0;
        forever #5 clk = ~clk; // Periodo de 10ns
    end

    // Pruebas
    initial begin
        // Reset inicial
        reset = 1;
        #10;
        reset = 0;
        
        // Dejar correr el procesador
        #2000; 
        
        $stop;
    end
endmodule
