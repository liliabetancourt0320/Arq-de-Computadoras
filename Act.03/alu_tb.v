module alu_tb;

    reg [7:0] A;
    reg [7:0] B;
    reg [2:0] op_code;
    wire [7:0] result;
    wire zero_flag;
    wire carry_flag;

    alu dut (
        .A(A),
        .B(B),
        .op_code(op_code),
        .result(result),
        .zero_flag(zero_flag),
        .carry_flag(carry_flag)
    );

    initial begin
        $dumpfile("alu.vcd"); // Archivo de volcado para ver las formas de onda 
        $dumpvars(0, alu_tb);

        // Prueba de Suma (10 + 5 = 15)
        A = 8'd10;
        B = 8'd5;
        op_code = 3'b000;
        #10;

        // Prueba de Resta (20 - 7 = 13)
        A = 8'd20;
        B = 8'd7;
        op_code = 3'b001;
        #10;

        // Prueba de AND (5 & 3 = 1) 
        A = 8'd5;
        B = 8'd3;
        op_code = 3'b010;
        #10;

        // Prueba de OR (5 | 3 = 7)
        A = 8'd5;
        B = 8'd3;
        op_code = 3'b011;
        #10;

        // Prueba de XOR (5 ^ 3 = 6)
        A = 8'd5;
        B = 8'd3;
        op_code = 3'b100;
        #10;

        // Prueba de Igualdad (12 == 12)
        A = 8'd12;
        B = 8'd12;
        op_code = 3'b101;
        #10;

        // Prueba de Mayor que (15 > 8)
        A = 8'd15;
        B = 8'd8;
        op_code = 3'b110;
        #10;

        // Prueba de Desplazamiento (4 << 1 = 8)
        A = 8'd4; 
        B = 8'd0; // B no se usa 
        op_code = 3'b111;
        #10;

        $finish; 
    end
endmodule
