module alu(
    input [7:0] A,
    input [7:0] B,
    input [2:0] op_code,
    output reg [7:0] result,
    output reg zero_flag,
    output reg carry_flag
);

    wire [8:0] sum_result;
    assign sum_result = A + B;

    // Complemento a dos
    wire [7:0] b_comp2;
    assign b_comp2 = ~B + 1;
    wire [8:0] sub_result;
    assign sub_result = A + b_comp2;

    always @(*) begin
        result = 8'b0;
        zero_flag = 1'b0; //establecer un valor por defecto al inicio
        carry_flag = 1'b0; // the same

        case(op_code)
            // Suma: A + B
            3'b000: begin
                result = sum_result[7:0];
                carry_flag = sum_result[8];
                zero_flag = (result == 8'b0);
            end

            // Resta: A - B
            3'b001: begin
                result = sub_result[7:0];
                carry_flag = sub_result[8];
                zero_flag = (result == 8'b0);
            end

            // AND: A & B
            3'b010: begin
                result = A & B;
                zero_flag = (result == 8'b0);
            end

            // OR: A | B
            3'b011: begin
                result = A | B;
                zero_flag = (result == 8'b0);
            end

            // XOR: A ^ B
            3'b100: begin
                result = A ^ B;
                zero_flag = (result == 8'b0);
            end

            // Comparación (Igual): A == B
            3'b101: begin
                result = (A == B) ? 8'b1 : 8'b0;
                zero_flag = (result == 8'b0);
            end

            // Comparación: A > B
            3'b110: begin
                result = (sub_result[8]) ? 8'b1 : 8'b0;
                zero_flag = (result == 8'b0);
            end

            // Desplazamiento: A << 1
            3'b111: begin
                result = A << 1;
                zero_flag = (result == 8'b0);
            end

            default: begin
                result = 8'bX; // Valor por defecto en caso de un op_code no válido
                zero_flag = 1'bX;
                carry_flag = 1'bX;
            end
        endcase
    end
endmodule
