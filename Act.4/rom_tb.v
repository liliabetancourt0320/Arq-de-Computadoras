module rom_tb;

    // Entradas para el módulo ROM
    reg [7:0] direccion;
    wire [7:0] dato_s;

    // Instancia del módulo ROM que se va a probar
    rom uut (
        .direccion(direccion),
        .dato_s(dato_s)
    );

    initial begin
        // Inicialización de la señal de dirección
        direccion = 8'd0;

        // --- CASOS DE PRUEBA ---

        // Caso 1: Leer la dirección 0
        #10 direccion = 8'd0;

        // Caso 2: Leer la dirección 3
        #10 direccion = 8'd3;

        // Caso 3: Leer la dirección 5
        #10 direccion = 8'd5;

        // Caso 4: Leer la dirección 8
        #10 direccion = 8'd8;

        // Caso 5: Leer la dirección 10
        #10 direccion = 8'd10;

        // Caso 6: Probar una dirección fuera de rango (debería devolver 'x')
        #10 direccion = 8'd15;

	// Finalizar la simulación
        #10 $finish;

    end

endmodule

