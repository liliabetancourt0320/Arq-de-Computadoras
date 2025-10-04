module rom_tb;

    // Entradas para el m�dulo ROM
    reg [7:0] direccion;
    wire [7:0] dato_s;

    // Instancia del m�dulo ROM que se va a probar
    rom uut (
        .direccion(direccion),
        .dato_s(dato_s)
    );

    initial begin
        // Inicializaci�n de la se�al de direcci�n
        direccion = 8'd0;

        // --- CASOS DE PRUEBA ---

        // Caso 1: Leer la direcci�n 0
        #10 direccion = 8'd0;

        // Caso 2: Leer la direcci�n 3
        #10 direccion = 8'd3;

        // Caso 3: Leer la direcci�n 5
        #10 direccion = 8'd5;

        // Caso 4: Leer la direcci�n 8
        #10 direccion = 8'd8;

        // Caso 5: Leer la direcci�n 10
        #10 direccion = 8'd10;

        // Caso 6: Probar una direcci�n fuera de rango (deber�a devolver 'x')
        #10 direccion = 8'd15;

	// Finalizar la simulaci�n
        #10 $finish;

    end

endmodule

