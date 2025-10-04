module ram_sync_tb;

    // Señales
    reg [7:0] data_in;
    reg [7:0] addr;
    reg wr;
    reg en;
    reg clk;
    wire [7:0] data_out;

    // Instancia de la RAM Síncrona
    ram_sync uut (
        .data_out(data_out),
        .data_in(data_in),
        .addr(addr),
        .wr(wr),
        .en(en),
        .clk(clk)
    );

    // Generador de reloj (periodo de 10 unidades de tiempo)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Proceso de simulación
    initial begin
        
        // Inicializar señales
        en = 0;
        wr = 0;
        addr = 8'd0;
        data_in = 8'd0;

        // Esperar un ciclo de reloj y habilitar el chip
        @(posedge clk);
        en = 1;

        // --- CASOS DE PRUEBA ---

        // Caso 1: Escribir el valor 25 en la dirección 5
        @(posedge clk);
        wr = 1;
        addr = 8'd5;
        data_in = 8'd25;
       
        // Caso 2: Escribir el valor 150 en la dirección 20
        @(posedge clk);
        addr = 8'd20;
        data_in = 8'd150;
       
        // Caso 3: Leer el valor de la dirección 5
        @(posedge clk);
        wr = 0; // Cambiar a modo lectura
        addr = 8'd5;
        // La lectura se reflejará en el siguiente ciclo
        @(posedge clk);
      
        // Caso 4: Escribir el valor 77 en la dirección 33
        @(posedge clk);
        wr = 1; // Modo escritura
        addr = 8'd33;
        data_in = 8'd77;
      
        // Caso 5: Leer el valor de la dirección 20
        @(posedge clk);
        wr = 0; // Modo lectura
        addr = 8'd20;
        @(posedge clk);
       
        // Caso 6: Leer el valor de la dirección 33
        @(posedge clk);
        addr = 8'd33;
        @(posedge clk);
       
        // Finalizar simulación
        #20 $finish;
    end

endmodule

