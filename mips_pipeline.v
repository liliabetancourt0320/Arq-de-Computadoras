`timescale 1ns / 1ps

module mips_pipeline(
    input clk, reset
);
    // --- CABLES DE FORWARDING (ADELANTAMIENTO) ---
    // Son necesarios para resolver riesgos de datos (Data Hazards)
    reg [1:0] ForwardA, ForwardB;
    reg [31:0] alu_in1_forwarded, alu_in2_forwarded_temp;
    
    // Declaraciones WB para usar en Forwarding
    reg [31:0] mem_wb_read_data, mem_wb_alu_result;
    reg [4:0]  mem_wb_write_reg;
    reg mem_wb_reg_write, mem_wb_mem_to_reg;
    wire [31:0] wb_final_data;

    // --- ETAPA 1: IF (Instruction Fetch) ---
    wire [31:0] pc_current, pc_next, pc_plus4, instr;
    
    // Lógica de Salto y Branch
    wire pcsrc; // Se define más adelante (en MEM)
    
    ProgramCounter PC(
        .clk(clk), .reset(reset), .pc_in(pc_next), .pc_out(pc_current)
    );
    Adder PC_Adder(
        .a(pc_current), .b(32'd4), .out(pc_plus4)
    );
    InstructionMemory IM(
        .address(pc_current), .instruction(instr)
    );

    // --- BUFFER IF/ID ---
    reg [31:0] if_id_pc_plus4, if_id_instr;
    
    always @(posedge clk or posedge reset) begin
        if(reset) begin
            if_id_pc_plus4 <= 0;
            if_id_instr <= 0;
        end 
        // FLUSHING: Si hay un branch tomado (pcsrc), borramos la instrucción (NOP)
        else if (pcsrc) begin
            if_id_pc_plus4 <= 0;
            if_id_instr <= 0; 
        end
        else begin
            if_id_pc_plus4 <= pc_plus4;
            if_id_instr <= instr;
        end
    end

    // --- ETAPA 2: ID (Instruction Decode) ---
    wire [31:0] read_data1, read_data2, sign_ext_imm;
    wire [4:0]  rs = if_id_instr[25:21];
    wire [4:0]  rt = if_id_instr[20:16];
    wire [4:0]  rd = if_id_instr[15:11];

    wire ctrl_reg_dst, ctrl_branch, ctrl_mem_read, ctrl_mem_to_reg;
    wire [1:0] ctrl_alu_op;
    wire ctrl_mem_write, ctrl_alu_src, ctrl_reg_write, ctrl_jump;

    ControlUnit Ctrl(
        .opcode(if_id_instr[31:26]),
        .reg_dst(ctrl_reg_dst), .branch(ctrl_branch), .mem_read(ctrl_mem_read),
        .mem_to_reg(ctrl_mem_to_reg), .alu_op(ctrl_alu_op),
        .mem_write(ctrl_mem_write), .alu_src(ctrl_alu_src), .reg_write(ctrl_reg_write),
        .jump(ctrl_jump)
    );

    RegisterFile RF(
        .clk(clk), 
        .reg_write(mem_wb_reg_write), 
        .read_reg1(rs), .read_reg2(rt),
        .write_reg(mem_wb_write_reg), 
        .write_data(wb_final_data),   
        .read_data1(read_data1), .read_data2(read_data2)
    );
    SignExtend SE(.in(if_id_instr[15:0]), .out(sign_ext_imm));

    wire [31:0] jump_address = {if_id_pc_plus4[31:28], if_id_instr[25:0], 2'b00};

    // --- BUFFER ID/EX ---
    reg [31:0] id_ex_pc_plus4, id_ex_read_data1, id_ex_read_data2, id_ex_sign_ext;
    reg [4:0]  id_ex_rs, id_ex_rt, id_ex_rd;
    reg id_ex_reg_dst, id_ex_alu_src, id_ex_mem_to_reg, id_ex_reg_write, id_ex_mem_read, id_ex_mem_write, id_ex_branch;
    reg [1:0] id_ex_alu_op;

    always @(posedge clk or posedge reset) begin
        // FLUSHING: Si hay branch (pcsrc), limpiamos señales de control para convertir en NOP
        if(reset || pcsrc) begin
            id_ex_reg_write <= 0; id_ex_mem_write <= 0; id_ex_branch <= 0;
            id_ex_mem_read <= 0; id_ex_reg_dst <= 0; id_ex_alu_src <= 0;
            id_ex_mem_to_reg <= 0; id_ex_alu_op <= 0;
            // Datos
            id_ex_pc_plus4 <= 0; id_ex_read_data1 <= 0; id_ex_read_data2 <= 0;
            id_ex_sign_ext <= 0; id_ex_rs <= 0; id_ex_rt <= 0; id_ex_rd <= 0;
        end else begin
            id_ex_pc_plus4 <= if_id_pc_plus4;
            id_ex_read_data1 <= read_data1;
            id_ex_read_data2 <= read_data2;
            id_ex_sign_ext <= sign_ext_imm;
            id_ex_rs <= rs; id_ex_rt <= rt; id_ex_rd <= rd;
            
            // Control Signals
            id_ex_reg_dst <= ctrl_reg_dst; id_ex_alu_src <= ctrl_alu_src;
            id_ex_mem_to_reg <= ctrl_mem_to_reg; id_ex_reg_write <= ctrl_reg_write;
            id_ex_mem_read <= ctrl_mem_read; id_ex_mem_write <= ctrl_mem_write;
            id_ex_branch <= ctrl_branch; id_ex_alu_op <= ctrl_alu_op;
        end
    end

    // --- ETAPA 3: EX (Execute) ---
    
    // 1. FORWARDING UNIT LOGIC (Adelantamiento)
    // Detecta si la instrucción anterior modificó un registro que necesitamos ahora
    reg [31:0] ex_mem_alu_result; // Declaración previa para usarla aquí
    reg ex_mem_reg_write;
    reg [4:0] ex_mem_write_reg;

    always @(*) begin
        ForwardA = 2'b00;
        ForwardB = 2'b00;

        // Adelantamiento desde etapa EX/MEM
        if (ex_mem_reg_write && (ex_mem_write_reg != 0) && (ex_mem_write_reg == id_ex_rs))
            ForwardA = 2'b10;
        if (ex_mem_reg_write && (ex_mem_write_reg != 0) && (ex_mem_write_reg == id_ex_rt))
            ForwardB = 2'b10;

        // Adelantamiento desde etapa MEM/WB
        if (mem_wb_reg_write && (mem_wb_write_reg != 0) && (mem_wb_write_reg == id_ex_rs) && 
            !(ex_mem_reg_write && (ex_mem_write_reg != 0) && (ex_mem_write_reg == id_ex_rs)))
            ForwardA = 2'b01;

        if (mem_wb_reg_write && (mem_wb_write_reg != 0) && (mem_wb_write_reg == id_ex_rt) && 
            !(ex_mem_reg_write && (ex_mem_write_reg != 0) && (ex_mem_write_reg == id_ex_rt)))
            ForwardB = 2'b01;
    end

    // 2. MUXES DE ADELANTAMIENTO
    always @(*) begin
        case(ForwardA)
            2'b00: alu_in1_forwarded = id_ex_read_data1;
            2'b10: alu_in1_forwarded = ex_mem_alu_result;
            2'b01: alu_in1_forwarded = wb_final_data;
            default: alu_in1_forwarded = id_ex_read_data1;
        endcase

        case(ForwardB)
            2'b00: alu_in2_forwarded_temp = id_ex_read_data2;
            2'b10: alu_in2_forwarded_temp = ex_mem_alu_result;
            2'b01: alu_in2_forwarded_temp = wb_final_data;
            default: alu_in2_forwarded_temp = id_ex_read_data2;
        endcase
    end

    wire [31:0] alu_in2, alu_result;
    wire [31:0] branch_target_addr;
    wire [4:0]  write_reg_addr;
    wire zero_flag;
    wire [3:0] alu_ctrl_signal;
    wire [31:0] shift_imm_out;

    ShiftLeft2 SL2(.in(id_ex_sign_ext), .out(shift_imm_out));
    Adder BranchAdder(.a(id_ex_pc_plus4), .b(shift_imm_out), .out(branch_target_addr));

    // Mux ALU Source (Inmediato o Registro Adelantado)
    Mux2to1_32bit ALUSrcMux(.in0(alu_in2_forwarded_temp), .in1(id_ex_sign_ext), .sel(id_ex_alu_src), .out(alu_in2));
    
    // Mux Destino (rt vs rd)
    Mux2to1_5bit RegDstMux(.in0(id_ex_rt), .in1(id_ex_rd), .sel(id_ex_reg_dst), .out(write_reg_addr));

    ALUControl ALU_Ctrl_Unit(.funct(id_ex_sign_ext[5:0]), .alu_op(id_ex_alu_op), .alu_control_out(alu_ctrl_signal));
    
    // ALU Principal usa la entrada adelantada (alu_in1_forwarded)
    ALU MainALU(.a(alu_in1_forwarded), .b(alu_in2), .control(alu_ctrl_signal), .result(alu_result), .zero(zero_flag));

    // --- BUFFER EX/MEM ---
    reg [31:0] ex_mem_branch_target, ex_mem_write_data;
    // (ex_mem_alu_result, ex_mem_write_reg y ex_mem_reg_write ya declarados arriba para forwarding)
    reg ex_mem_zero, ex_mem_branch, ex_mem_mem_read, ex_mem_mem_write, ex_mem_mem_to_reg;

    always @(posedge clk or posedge reset) begin
        if(reset || pcsrc) begin // Flush en branch
             ex_mem_mem_write <= 0; ex_mem_reg_write <= 0; ex_mem_branch <= 0;
             ex_mem_mem_read <= 0; ex_mem_mem_to_reg <= 0;
        end else begin
            ex_mem_branch_target <= branch_target_addr;
            ex_mem_alu_result <= alu_result;
            ex_mem_write_data <= alu_in2_forwarded_temp; // Guardamos el dato correcto para SW
            ex_mem_write_reg <= write_reg_addr;
            ex_mem_zero <= zero_flag;
            
            ex_mem_branch <= id_ex_branch; ex_mem_mem_read <= id_ex_mem_read;
            ex_mem_mem_write <= id_ex_mem_write; ex_mem_reg_write <= id_ex_reg_write;
            ex_mem_mem_to_reg <= id_ex_mem_to_reg;
        end
    end

    // --- ETAPA 4: MEM (Memory) ---
    wire [31:0] mem_read_data;
    assign pcsrc = ex_mem_branch & ex_mem_zero; 

    DataMemory DM(
        .clk(clk), .mem_write(ex_mem_mem_write), .mem_read(ex_mem_mem_read),
        .address(ex_mem_alu_result), .write_data(ex_mem_write_data),
        .read_data(mem_read_data)
    );

    wire [31:0] pc_branch_choice;
    Mux2to1_32bit BranchMux(.in0(pc_plus4), .in1(ex_mem_branch_target), .sel(pcsrc), .out(pc_branch_choice));
    
    assign pc_next = (ctrl_jump) ? jump_address : pc_branch_choice;

    // --- BUFFER MEM/WB ---
    always @(posedge clk or posedge reset) begin
        if(reset) begin
            mem_wb_reg_write <= 0;
        end else begin
            mem_wb_read_data <= mem_read_data;
            mem_wb_alu_result <= ex_mem_alu_result;
            mem_wb_write_reg <= ex_mem_write_reg;
            
            mem_wb_reg_write <= ex_mem_reg_write;
            mem_wb_mem_to_reg <= ex_mem_mem_to_reg;
        end
    end

    // --- ETAPA 5: WB (Write Back) ---
    Mux2to1_32bit WBMux(
        .in0(mem_wb_alu_result), .in1(mem_wb_read_data),
        .sel(mem_wb_mem_to_reg),
        .out(wb_final_data)
    );

endmodule