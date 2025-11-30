import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

REGISTERS_ENCODE = {
    "$zero": 0,
    "$0": 0,
    "$at": 1,
    "$1": 1,
    "$v0": 2,
    "$2": 2,
    "$v1": 3,
    "$3": 3,
    "$a0": 4,
    "$4": 4,
    "$a1": 5,
    "$5": 5,
    "$a2": 6,
    "$6": 6,
    "$a3": 7,
    "$7": 7,
    "$t0": 8,
    "$8": 8,
    "$t1": 9,
    "$9": 9,
    "$t2": 10,
    "$10": 10,
    "$t3": 11,
    "$11": 11,
    "$t4": 12,
    "$12": 12,
    "$t5": 13,
    "$13": 13,
    "$t6": 14,
    "$14": 14,
    "$t7": 15,
    "$15": 15,
    "$s0": 16,
    "$16": 16,
    "$s1": 17,
    "$17": 17,
    "$s2": 18,
    "$18": 18,
    "$s3": 19,
    "$19": 19,
    "$s4": 20,
    "$20": 20,
    "$s5": 21,
    "$21": 21,
    "$s6": 22,
    "$22": 22,
    "$s7": 23,
    "$23": 23,
    "$t8": 24,
    "$24": 24,
    "$t9": 25,
    "$25": 25,
    "$k0": 26,
    "$26": 26,
    "$k1": 27,
    "$27": 27,
    "$gp": 28,
    "$28": 28,
    "$sp": 29,
    "$29": 29,
    "$fp": 30,
    "$30": 30,
    "$ra": 31,
    "$31": 31,
}

REGISTERS_DECODE = {
    0: "$zero",
    1: "$at",
    2: "$v0",
    3: "$v1",
    4: "$a0",
    5: "$a1",
    6: "$a2",
    7: "$a3",
    8: "$t0",
    9: "$t1",
    10: "$t2",
    11: "$t3",
    12: "$t4",
    13: "$t5",
    14: "$t6",
    15: "$t7",
    16: "$s0",
    17: "$s1",
    18: "$s2",
    19: "$s3",
    20: "$s4",
    21: "$s5",
    22: "$s6",
    23: "$s7",
    24: "$t8",
    25: "$t9",
    26: "$k0",
    27: "$k1",
    28: "$gp",
    29: "$sp",
    30: "$fp",
    31: "$ra",
}

INSTRUCTION_DB_ENCODE = {
    "add": {"type": "R", "opcode": "000000", "funct": "100000"},
    "sub": {"type": "R", "opcode": "000000", "funct": "100010"},
    "and": {"type": "R", "opcode": "000000", "funct": "100100"},
    "or": {"type": "R", "opcode": "000000", "funct": "100101"},
    "slt": {"type": "R", "opcode": "000000", "funct": "101010"},
    "nor": {"type": "R", "opcode": "000000", "funct": "100111"},
    "xor": {"type": "R", "opcode": "000000", "funct": "100110"},
    "addi": {"type": "I_IMM", "opcode": "001000"},
    "andi": {"type": "I_IMM", "opcode": "001100"},
    "ori": {"type": "I_IMM", "opcode": "001101"},
    "xori": {"type": "I_IMM", "opcode": "001110"},
    "slti": {"type": "I_IMM", "opcode": "001010"},
    "lw": {"type": "I_MEM", "opcode": "100011"},
    "sw": {"type": "I_MEM", "opcode": "101011"},
    "beq": {"type": "I_BRANCH", "opcode": "000100"},
    "bne": {"type": "I_BRANCH", "opcode": "000101"},
    "j": {"type": "J", "opcode": "000010"},
    "jal": {"type": "J", "opcode": "000011"},
    "jr": {"type": "R_JUMP", "opcode": "000000", "funct": "001000"},
}

INSTRUCTION_DB_DECODE = {
    "000000": {
        "100000": {"name": "add", "type": "R"},
        "100001": {"name": "addu", "type": "R"},
        "100010": {"name": "sub", "type": "R"},
        "100011": {"name": "subu", "type": "R"},
        "100100": {"name": "and", "type": "R"},
        "100101": {"name": "or", "type": "R"},
        "100110": {"name": "xor", "type": "R"},
        "100111": {"name": "nor", "type": "R"},
        "101010": {"name": "slt", "type": "R"},
        "101011": {"name": "sltu", "type": "R"},
        "000000": {"name": "sll", "type": "R_SHIFT"},
        "000010": {"name": "srl", "type": "R_SHIFT"},
        "000011": {"name": "sra", "type": "R_SHIFT"},
        "000100": {"name": "sllv", "type": "R"},
        "000110": {"name": "srlv", "type": "R"},
        "000111": {"name": "srav", "type": "R"},
        "001000": {"name": "jr", "type": "R_JUMP"},
        "001001": {"name": "jalr", "type": "R_JUMP"},
        "001100": {"name": "syscall", "type": "R_SYSCALL"},
        "001101": {"name": "break", "type": "R_BREAK"},
        "000001": {"name": "custom_op", "type": "R"},
    },
    "001000": {"name": "addi", "type": "I_IMM"},
    "001001": {"name": "addiu", "type": "I_IMM"},
    "001100": {"name": "andi", "type": "I_IMM"},
    "001101": {"name": "ori", "type": "I_IMM"},
    "001110": {"name": "xori", "type": "I_IMM"},
    "001010": {"name": "slti", "type": "I_IMM"},
    "001011": {"name": "sltiu", "type": "I_IMM"},
    "100011": {"name": "lw", "type": "I_MEM"},
    "101011": {"name": "sw", "type": "I_MEM"},
    "100000": {"name": "lb", "type": "I_MEM"},
    "100100": {"name": "lbu", "type": "I_MEM"},
    "101000": {"name": "sb", "type": "I_MEM"},
    "001111": {"name": "lui", "type": "I_LUI"},
    "000100": {"name": "beq", "type": "I_BRANCH"},
    "000101": {"name": "bne", "type": "I_BRANCH"},
    "000110": {"name": "blez", "type": "I_BRANCH"},
    "000111": {"name": "bgtz", "type": "I_BRANCH"},
    "000010": {"name": "j", "type": "J"},
    "000011": {"name": "jal", "type": "J"},
}


def to_bin(val, bits):
    try:
        val = int(val)
    except ValueError:
        raise ValueError(f"se esperaba un numero, recibi: {val}")

    if bits == 16:
        if val < -32768 or val > 65535:
            raise ValueError(f"valor {val} fuera de rango para 16 bits")

    if val < 0:
        val = (1 << bits) + val

    mask = (1 << bits) - 1
    return format(val & mask, f"0{bits}b")


def clean_lines(raw_lines):
    cleaned = []
    for line in raw_lines:
        line = line.split("#")[0].strip()
        if not line:
            continue

        if ":" in line:
            parts = line.split(":")
            label = parts[0].strip()
            instruction = parts[1].strip()
            cleaned.append({"type": "label", "content": label})
            if instruction:
                cleaned.append({"type": "instr", "content": instruction})
        else:
            cleaned.append({"type": "instr", "content": line})
    return cleaned


def first_pass(cleaned_lines):
    labels = {}
    instr_count = 0
    for item in cleaned_lines:
        if item["type"] == "label":
            if item["content"] in labels:
                raise ValueError(f"etiqueta duplicada: '{item['content']}'")
            labels[item["content"]] = instr_count
        else:
            instr_count += 1
    return labels


def assemble(cleaned_lines, labels):
    binary_lines = []
    pc = 0
    logs = []

    for item in cleaned_lines:
        if item["type"] == "label":
            continue

        line = item["content"]
        parts = line.replace(",", " ").replace("(", " ").replace(")", " ").split()
        if not parts:
            continue

        instr_name = parts[0].lower()

        try:
            if instr_name not in INSTRUCTION_DB_ENCODE:
                raise ValueError(f"instruccion no reconocida: '{instr_name}'")

            info = INSTRUCTION_DB_ENCODE[instr_name]
            fmt = info["type"]
            opcode = info["opcode"]
            bin_instr = ""

            if fmt == "R":
                if len(parts) != 4:
                    raise ValueError(f"argumentos incorrectos para {instr_name}")
                rd = REGISTERS_ENCODE[parts[1]]
                rs = REGISTERS_ENCODE[parts[2]]
                rt = REGISTERS_ENCODE[parts[3]]
                funct = info["funct"]
                bin_instr = (
                    f"{opcode}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(rd, 5)}00000{funct}"
                )

            elif fmt == "R_JUMP":
                if len(parts) != 2:
                    raise ValueError(f"argumentos incorrectos para {instr_name}")
                rs = REGISTERS_ENCODE[parts[1]]
                funct = info["funct"]
                bin_instr = f"{opcode}{to_bin(rs, 5)}000000000000000{funct}"

            elif fmt == "I_IMM":
                if len(parts) != 4:
                    raise ValueError(f"argumentos incorrectos para {instr_name}")
                rt = REGISTERS_ENCODE[parts[1]]
                rs = REGISTERS_ENCODE[parts[2]]
                imm = int(parts[3])
                bin_instr = f"{opcode}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(imm, 16)}"

            elif fmt == "I_MEM":
                if len(parts) != 4:
                    raise ValueError(f"sintaxis incorrecta para memoria")
                rt = REGISTERS_ENCODE[parts[1]]
                offset = int(parts[2])
                rs = REGISTERS_ENCODE[parts[3]]
                bin_instr = (
                    f"{opcode}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(offset, 16)}"
                )

            elif fmt == "I_BRANCH":
                if len(parts) != 4:
                    raise ValueError(f"faltan operandos para el salto")
                rs = REGISTERS_ENCODE[parts[1]]
                rt = REGISTERS_ENCODE[parts[2]]
                target = parts[3]

                if target in labels:
                    offset = labels[target] - (pc + 1)
                else:
                    offset = int(target)

                bin_instr = (
                    f"{opcode}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(offset, 16)}"
                )

            elif fmt == "J":
                if len(parts) != 2:
                    raise ValueError(f"argumentos incorrectos para salto J")
                target = parts[1]
                if target in labels:
                    idx = labels[target]
                else:
                    try:
                        addr = int(target, 0)
                        idx = addr // 4
                    except ValueError:
                        raise ValueError(f"direccion no valida: {target}")

                bin_instr = f"{opcode}{to_bin(idx, 26)}"

            binary_lines.append(bin_instr)
            hex_val = f"0x{int(bin_instr, 2):08X}"
            logs.append(f"PC[{pc * 4:02X}] {line:<24} -> {bin_instr} | {hex_val}")
            pc += 1

        except Exception as e:
            return None, f"error en linea '{line}': {str(e)}"

    return binary_lines, logs


def bin_to_signed(val, bits):
    if val >= (1 << (bits - 1)):
        return val - (1 << bits)
    return val


def decode_instruction(binary_str):
    if len(binary_str) != 32:
        raise ValueError(f"instruccion debe tener 32 bits, tiene {len(binary_str)}")

    opcode = binary_str[0:6]
    rs = binary_str[6:11]
    rt = binary_str[11:16]
    rd = binary_str[16:21]
    shamt = binary_str[21:26]
    funct = binary_str[26:32]
    immediate = binary_str[16:32]
    address = binary_str[6:32]

    rs_num = int(rs, 2)
    rt_num = int(rt, 2)
    rd_num = int(rd, 2)
    shamt_num = int(shamt, 2)
    immediate_num = int(immediate, 2)
    address_num = int(address, 2)

    if opcode == "000000":
        if funct in INSTRUCTION_DB_DECODE["000000"]:
            instr_info = INSTRUCTION_DB_DECODE["000000"][funct]
            instr_name = instr_info["name"]
            instr_type = instr_info["type"]

            if instr_type == "R_SHIFT":
                return f"{instr_name} {REGISTERS_DECODE[rd_num]}, {REGISTERS_DECODE[rt_num]}, {shamt_num}"
            elif instr_type == "R_JUMP":
                return f"{instr_name} {REGISTERS_DECODE[rs_num]}"
            elif instr_type == "R_SYSCALL" or instr_type == "R_BREAK":
                return f"{instr_name}"
            else:
                return f"{instr_name} {REGISTERS_DECODE[rd_num]}, {REGISTERS_DECODE[rs_num]}, {REGISTERS_DECODE[rt_num]}"
        else:
            return f"# Instruccion R no reconocida: funct={funct}"

    elif opcode in INSTRUCTION_DB_DECODE:
        instr_info = INSTRUCTION_DB_DECODE[opcode]
        instr_name = instr_info["name"]
        instr_type = instr_info["type"]

        if instr_type == "I_MEM":
            imm_signed = bin_to_signed(immediate_num, 16)
            return f"{instr_name} {REGISTERS_DECODE[rt_num]}, {imm_signed}({REGISTERS_DECODE[rs_num]})"

        elif instr_type == "I_BRANCH":
            imm_signed = bin_to_signed(immediate_num, 16)
            if instr_name in ["blez", "bgtz"]:
                return f"{instr_name} {REGISTERS_DECODE[rs_num]}, {imm_signed}"
            else:
                return f"{instr_name} {REGISTERS_DECODE[rs_num]}, {REGISTERS_DECODE[rt_num]}, {imm_signed}"

        elif instr_type == "I_LUI":
            return f"{instr_name} {REGISTERS_DECODE[rt_num]}, {immediate_num}"

        elif instr_type == "I_IMM":
            imm_signed = bin_to_signed(immediate_num, 16)
            return f"{instr_name} {REGISTERS_DECODE[rt_num]}, {REGISTERS_DECODE[rs_num]}, {imm_signed}"

        elif instr_type == "J":
            target_address = address_num * 4
            return f"{instr_name} 0x{target_address:08X}"

    else:
        return f"# Opcode no reconocido: {opcode}"


def parse_decode_input(input_text, input_format):
    instructions = []
    lines = input_text.splitlines()
    if not lines:
        return instructions

    if len(lines) == 1 and len(input_text.strip()) > 32:
        long_line = (
            input_text.strip().replace(" ", "").replace("\n", "").replace("\t", "")
        )
        if all(c in "01" for c in long_line) and len(long_line) % 32 == 0:
            lines = [long_line[i : i + 32] for i in range(0, len(long_line), 32)]
            input_format = "BIN"
        elif (
            all(c in "0123456789ABCDEFabcdef" for c in long_line.replace("0x", ""))
            and len(long_line.replace("0x", "")) % 8 == 0
        ):
            clean_hex = long_line.replace("0x", "").upper()
            lines = [clean_hex[i : i + 8] for i in range(0, len(clean_hex), 8)]
            input_format = "HEX"

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            binary_str = ""
            if input_format == "HEX":
                clean_line = (
                    line.split("#")[0]
                    .strip()
                    .replace("0x", "")
                    .replace(" ", "")
                    .upper()
                )
                if not clean_line:
                    continue
                if len(clean_line) > 8:
                    clean_line = clean_line[:8]
                else:
                    clean_line = clean_line.zfill(8)
                try:
                    int(clean_line, 16)
                    binary_str = bin(int(clean_line, 16))[2:].zfill(32)
                except ValueError:
                    raise ValueError(f"Hex invalido: '{line}'")
            else:
                clean_line = line.split("#")[0].strip().replace(" ", "")
                if not clean_line:
                    continue
                if not all(c in "01" for c in clean_line):
                    clean_hex = clean_line.replace("0x", "").upper()
                    if (
                        all(c in "0123456789ABCDEF" for c in clean_hex)
                        and len(clean_hex) <= 8
                    ):
                        binary_str = bin(int(clean_hex, 16))[2:].zfill(32)
                    else:
                        raise ValueError(f"Binario invalido: '{line}'")
                else:
                    binary_str = clean_line.zfill(32)[:32]

            assembly_line = decode_instruction(binary_str)
            instructions.append(
                {
                    "original": line,
                    "assembly": assembly_line,
                    "binary": binary_str,
                    "hex": format(int(binary_str, 2), "08X"),
                }
            )
        except Exception as e:
            instructions.append(
                {
                    "original": line,
                    "assembly": f"# ERROR: {str(e)}",
                    "binary": "0" * 32,
                    "hex": "00000000",
                }
            )
    return instructions


def load_binary_file(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        instructions = []
        for i in range(0, len(data), 4):
            if i + 4 <= len(data):
                instruction_bytes = data[i : i + 4]
                instruction_int = int.from_bytes(instruction_bytes, byteorder="big")
                instructions.append(format(instruction_int, "032b"))
        return instructions
    except Exception as e:
        raise ValueError(f"Error al cargar binario: {str(e)}")


class MipsHybridGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MIPS32 - Codificador/Decodificador")
        self.root.geometry("1000x700")

        self.mode = tk.StringVar(value="ENCODE")
        self.output_format = tk.StringVar(value="BIN")
        self.decode_input_format = tk.StringVar(value="HEX")
        self.decode_output_format = tk.StringVar(value="BOTH")

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        toolbar = tk.Frame(main_frame, bg="#eee", bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        tk.Label(toolbar, text="Modo:", bg="#eee").pack(side=tk.LEFT, padx=(10, 5))
        tk.Radiobutton(
            toolbar,
            text="Codificar (Assembly → Binario)",
            variable=self.mode,
            value="ENCODE",
            command=self.switch_mode,
            bg="#eee",
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            toolbar,
            text="Decodificar (Binario → Assembly)",
            variable=self.mode,
            value="DECODE",
            command=self.switch_mode,
            bg="#eee",
        ).pack(side=tk.LEFT)

        tk.Button(toolbar, text="Abrir archivo", command=self.load_file).pack(
            side=tk.LEFT, padx=10, pady=5
        )
        tk.Button(
            toolbar, text="Convertir", command=self.convert, bg="#4CAF50", fg="white"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(
            toolbar,
            text="Guardar resultado",
            command=self.save_file,
            bg="#2196F3",
            fg="white",
        ).pack(side=tk.LEFT, padx=5, pady=5)

        config_frame = tk.Frame(main_frame, bg="#f0f0f0", bd=1, relief=tk.SUNKEN)
        config_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        self.encode_config = tk.Frame(config_frame, bg="#f0f0f0")
        self.encode_config.pack(side=tk.TOP, fill=tk.X)
        tk.Label(self.encode_config, text="Formato salida:", bg="#f0f0f0").pack(
            side=tk.LEFT, padx=(10, 5)
        )
        tk.Radiobutton(
            self.encode_config,
            text="Binario",
            variable=self.output_format,
            value="BIN",
            bg="#f0f0f0",
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            self.encode_config,
            text="Hexadecimal",
            variable=self.output_format,
            value="HEX",
            bg="#f0f0f0",
        ).pack(side=tk.LEFT)

        self.decode_config = tk.Frame(config_frame, bg="#f0f0f0")
        self.decode_config.pack(side=tk.TOP, fill=tk.X)
        tk.Label(self.decode_config, text="Entrada:", bg="#f0f0f0").pack(
            side=tk.LEFT, padx=(10, 5)
        )
        tk.Radiobutton(
            self.decode_config,
            text="Hexadecimal",
            variable=self.decode_input_format,
            value="HEX",
            bg="#f0f0f0",
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            self.decode_config,
            text="Binario",
            variable=self.decode_input_format,
            value="BIN",
            bg="#f0f0f0",
        ).pack(side=tk.LEFT)

        tk.Label(self.decode_config, text="Salida:", bg="#f0f0f0").pack(
            side=tk.LEFT, padx=(20, 5)
        )
        tk.Radiobutton(
            self.decode_config,
            text="Original + Assembly",
            variable=self.decode_output_format,
            value="BOTH",
            bg="#f0f0f0",
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            self.decode_config,
            text="Solo Assembly",
            variable=self.decode_output_format,
            value="ASSEMBLY_ONLY",
            bg="#f0f0f0",
        ).pack(side=tk.LEFT)

        paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        self.frame_in = tk.LabelFrame(paned, text="Entrada")
        self.txt_input = scrolledtext.ScrolledText(
            self.frame_in, width=45, font=("Consolas", 10), undo=True
        )
        self.txt_input.pack(fill=tk.BOTH, expand=True)
        paned.add(self.frame_in)

        self.frame_out = tk.LabelFrame(paned, text="Salida")
        self.txt_output = scrolledtext.ScrolledText(
            self.frame_out, width=45, font=("Consolas", 10), bg="#f4f4f4"
        )
        self.txt_output.pack(fill=tk.BOTH, expand=True)
        paned.add(self.frame_out)

        frame_log = tk.LabelFrame(main_frame, text="Consola")
        frame_log.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.txt_logs = scrolledtext.ScrolledText(
            frame_log, height=8, font=("Consolas", 9), fg="#333"
        )
        self.txt_logs.pack(fill=tk.BOTH)

        self.current_data = []
        self.switch_mode()

    def switch_mode(self):
        mode = self.mode.get()
        if mode == "ENCODE":
            self.frame_in.config(text="Entrada (Assembly MIPS)")
            self.frame_out.config(text="Salida (Código Máquina)")
            self.encode_config.pack(side=tk.TOP, fill=tk.X)
            self.decode_config.pack_forget()
            self.load_encode_examples()
        else:
            self.frame_in.config(text="Entrada (Código Máquina)")
            self.frame_out.config(text="Salida (Assembly MIPS)")
            self.decode_config.pack(side=tk.TOP, fill=tk.X)
            self.encode_config.pack_forget()
            self.load_decode_examples()

    def load_encode_examples(self):
        examples = [
            "main:",
            "    addi $t0, $zero, 5      # N = 5",
            "    add $t1, $zero, $zero   # i = 0",
            "    loop:",
            "    beq $t1, $t0, end",
            "    addi $t1, $t1, 1",
            "    j loop",
            "    end:",
            "    sw $t1, 0($zero)",
        ]
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert(tk.END, "\n".join(examples))

    def load_decode_examples(self):
        examples_hex = ["20080005", "00000020", "01094020", "08000001"]
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert(tk.END, "\n".join(examples_hex))

    def load_file(self):
        file_types = [
            ("Archivos ASM", "*.asm"),
            ("Archivos TXT", "*.txt"),
            ("Archivos BIN", "*.bin"),
            ("Todos", "*.*"),
        ]
        path = filedialog.askopenfilename(filetypes=file_types)
        if path:
            try:
                if self.mode.get() == "DECODE" and path.lower().endswith(".bin"):
                    data = load_binary_file(path)
                    content = (
                        "\n".join(data)
                        if self.decode_input_format.get() == "BIN"
                        else "\n".join([format(int(x, 2), "08X") for x in data])
                    )
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                self.txt_input.delete("1.0", tk.END)
                self.txt_input.insert(tk.END, content)
                self.log(f"Cargado: {path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def convert(self):
        txt = self.txt_input.get("1.0", tk.END).strip()
        if not txt:
            messagebox.showwarning("Aviso", "Entrada vacía")
            return

        if self.mode.get() == "ENCODE":
            try:
                clean = clean_lines(txt.splitlines())
                if not clean:
                    return
                labels = first_pass(clean)
                bin_c, logs = assemble(clean, labels)
                if bin_c is None:
                    self.log(logs)
                    messagebox.showerror("Error", logs)
                    return
                self.current_data = bin_c
                out = ""
                for b in bin_c:
                    if self.output_format.get() == "BIN":
                        out += b + "\n"
                    else:
                        out += f"{int(b, 2):08X}\n"
                self.txt_output.delete("1.0", tk.END)
                self.txt_output.insert(tk.END, out)
                self.log("Codificación exitosa")
                for l in logs:
                    self.log(l)
            except Exception as e:
                self.log(f"Error: {e}")
        else:
            res = parse_decode_input(txt, self.decode_input_format.get())
            self.current_data = res
            out = ""
            for r in res:
                if self.decode_output_format.get() == "BOTH":
                    orig = (
                        f"0x{r['hex']}"
                        if self.decode_input_format.get() == "HEX"
                        else r["original"]
                    )
                    out += f"{orig} -> {r['assembly']}\n"
                else:
                    out += f"{r['assembly']}\n"
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, out)
            self.log(f"Decodificación exitosa: {len(res)} instrucciones")
            for r in res:
                self.log(f"{r['hex']} -> {r['assembly']}")

    def save_file(self):
        if not self.current_data:
            messagebox.showwarning("Aviso", "Primero debes realizar una conversión")
            return

        file_types = [
            ("Archivo Assembly", "*.asm"),
            ("Archivo Texto", "*.txt"),
            ("Archivo MEM", "*.mem"),
            ("Archivo Binario", "*.bin"),
        ]

        path = filedialog.asksaveasfilename(filetypes=file_types)
        if path:
            try:
                if path.endswith(".bin") and self.mode.get() == "ENCODE":
                    with open(path, "wb") as f:
                        for b in self.current_data:
                            f.write(int(b, 2).to_bytes(4, "big"))
                    self.log(f"Binario guardado: {path}")
                else:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(self.txt_output.get("1.0", tk.END))
                    self.log(f"Texto guardado: {path}")
                messagebox.showinfo("Éxito", "Archivo guardado correctamente")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def log(self, msg):
        self.txt_logs.insert(tk.END, msg + "\n")
        self.txt_logs.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = MipsHybridGUI(root)
    root.mainloop()
