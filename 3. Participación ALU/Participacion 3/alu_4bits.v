module alu_4bit(
    input [3:0] A,          
    input [3:0] B,          
    input [1:0] op_sel,     
    output reg [3:0] result 
);

//códigos de operación
parameter ADD = 2'b00;
parameter AND = 2'b01;

always @(*) begin
    case(op_sel)
        ADD: result = A + B;    // Suma ari
        AND: result = A & B;    // AND log
        default: result = 4'b0000;
    endcase
end

endmodule
