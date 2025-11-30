// Sumador simple
module Adder(
    input [31:0] a, b,
    output [31:0] out
);
    assign out = a + b;
endmodule

// MULTIPLEXOR 2 a 1 (32 bits y 5 bits)
module Mux2to1_32bit(
    input [31:0] in0, in1,
    input sel,
    output [31:0] out
);
    assign out = (sel) ? in1 : in0;
endmodule

module Mux2to1_5bit(
    input [4:0] in0, in1,
    input sel,
    output [4:0] out
);
    assign out = (sel) ? in1 : in0;
endmodule


// PC
module ProgramCounter(
    input clk, reset,
    input [31:0] pc_in,
    output reg [31:0] pc_out
);
    always @(posedge clk or posedge reset) begin
        if (reset) pc_out <= 0;
        else pc_out <= pc_in;
    end
endmodule

// INSTRUCTION MEMORY (Con carga de archivo)
module InstructionMemory(
    input [31:0] address,
    output [31:0] instruction
);
    reg [31:0] memory [0:255];
    integer i; 

    initial begin
        // 1. Limpiamos TODA la memoria con ceros primero
        for (i=0; i<256; i=i+1) memory[i] = 32'd0;

        // 2. Cargamos tu programa (¡Verifica que la ruta sea correcta!)
        // Usa barras normales / no invertidas \
        $readmemb("C:/Users/lenovo/Downloads/instrucciones.mem", memory); 
    end

    // Lectura segura
    assign instruction = memory[address >> 2];
endmodule

// Banco de Registros
module RegisterFile(
    input clk, reg_write,
    input [4:0] read_reg1, read_reg2, write_reg,
    input [31:0] write_data,
    output [31:0] read_data1, read_data2
);
    reg [31:0] registers [0:31];
    integer i;

    initial begin
        for (i=0; i<32; i=i+1) registers[i] = 0; // Inicializar en 0
    end

    // Lectura asíncrona
    assign read_data1 = (read_reg1 == 0) ? 0 : registers[read_reg1];
    assign read_data2 = (read_reg2 == 0) ? 0 : registers[read_reg2];

    // Escritura síncrona (Write Back stage)
    always @(posedge clk) begin
        if (reg_write && write_reg != 0)
            registers[write_reg] <= write_data;
    end
endmodule

module SignExtend(
    input [15:0] in,
    output [31:0] out
);
    assign out = {{16{in[15]}}, in}; // Repite el bit de signo 16 veces
endmodule

module ShiftLeft2(
    input [31:0] in,
    output [31:0] out
);
    assign out = in << 2;
endmodule

// ALU y ALU CONTROL
module ALUControl(
    input [5:0] funct,
    input [1:0] alu_op,
    output reg [3:0] alu_control_out
);
    always @(*) begin
        case(alu_op)
            2'b00: alu_control_out = 4'b0010; // LW/SW/ADDI -> ADD
            2'b01: alu_control_out = 4'b0110; // BEQ -> SUB
            2'b10: begin // R-Type
                case(funct)
                    6'b100000: alu_control_out = 4'b0010; // ADD
                    6'b100010: alu_control_out = 4'b0110; // SUB
                    6'b100100: alu_control_out = 4'b0000; // AND
                    6'b100101: alu_control_out = 4'b0001; // OR
                    6'b101010: alu_control_out = 4'b0111; // SLT
                    default:   alu_control_out = 4'b0000;
                endcase
            end
            // EL PARCHE ESTÁ AQUÍ:
            2'b11: alu_control_out = 4'b0000; // Forzamos operación AND para el código 11 (ANDI)
            
            default: alu_control_out = 4'b0000;
        endcase
    end
endmodule

module ALU(
    input [31:0] a, b,
    input [3:0] control,
    output reg [31:0] result,
    output zero
);
    always @(*) begin
        case(control)
            4'b0000: result = a & b;       // AND
            4'b0001: result = a | b;       // OR
            4'b0010: result = a + b;       // ADD
            4'b0110: result = a - b;       // SUB
            4'b0111: result = (a < b) ? 1 : 0; // SLT
            default: result = 0;
        endcase
    end
    assign zero = (result == 0);
endmodule

// DATA MEMORY
module DataMemory(
    input clk, mem_write, mem_read,
    input [31:0] address, write_data,
    output [31:0] read_data
);
    reg [31:0] memory [0:255];
    integer k;
    
    initial begin
    for (k=0; k<256; k=k+1) memory[k] = 0;
    
    // --- DATOS DE PRUEBA PARA TU FILTRO ---
    // N = 5 (Tu programa lee 5 datos)
    memory[0] = 32'd10;  // < 50 (Se ignora)
    memory[1] = 32'd60;  // > 50, par (Se ignora)
    memory[2] = 32'd55;  // > 50, impar (¡Se debe SUMAR!)
    memory[3] = 32'd100; // > 50, par (Se ignora)
    memory[4] = 32'd73;  // > 50, impar (¡Se debe SUMAR!)
    // Resultado esperado en acumulador: 55 + 73 = 128
end

    assign read_data = (mem_read) ? memory[address >> 2] : 0;

    always @(posedge clk) begin
        if (mem_write)
            memory[address >> 2] <= write_data;
    end
endmodule

// CONTROL UNIT
module ControlUnit(
    input [5:0] opcode,
    output reg reg_dst, branch, mem_read, mem_to_reg, 
    output reg [1:0] alu_op, 
    output reg mem_write, alu_src, reg_write, jump
);
    always @(*) begin
        // Valores por defecto (importante para evitar latches)
        {reg_dst, branch, mem_read, mem_to_reg, alu_op, mem_write, alu_src, reg_write, jump} = 0;

        case(opcode)
            6'b000000: begin // R-Type
                reg_dst = 1; reg_write = 1; alu_op = 2'b10;
            end
            6'b100011: begin // LW
                alu_src = 1; mem_to_reg = 1; reg_write = 1; mem_read = 1; alu_op = 2'b00;
            end
            6'b101011: begin // SW
                alu_src = 1; mem_write = 1; alu_op = 2'b00;
            end
            6'b000100: begin // BEQ
                branch = 1; alu_op = 2'b01;
            end
            6'b001000: begin // ADDI
                alu_src = 1; reg_write = 1; alu_op = 2'b00; // ADDI usa suma (00)
            end
            6'b001100: begin // ANDI
                alu_src = 1; reg_write = 1; alu_op = 2'b11; // Usamos 11 para ANDI
            end
            // Las demás (ORI, XORI) no funcionarán bien, pero tu programa no las usa.
            6'b000010: jump = 1; // JUMP
        endcase
    end
endmodule