import sys
import os

# --- DEFINICIONES MIPS ---
OPCODES = {
    "R-TYPE": "000000",
    "addi": "001000",
    "andi": "001100",
    "ori": "001101",
    "xori": "001110",
    "slti": "001010",
    "beq": "000100",
    "lw": "100011",
    "sw": "101011",
    "j": "000010",
}

FUNCT = {
    "add": "100000",
    "sub": "100010",
    "and": "100100",
    "or": "100101",
    "slt": "101010",
}

REGISTERS = {
    "$zero": 0,
    "$at": 1,
    "$v0": 2,
    "$v1": 3,
    "$a0": 4,
    "$a1": 5,
    "$a2": 6,
    "$a3": 7,
    "$t0": 8,
    "$t1": 9,
    "$t2": 10,
    "$t3": 11,
    "$t4": 12,
    "$t5": 13,
    "$t6": 14,
    "$t7": 15,
    "$t8": 16,
    "$t9": 17,
    "$s0": 18,
    "$s1": 19,
    "$s2": 20,
    "$s3": 21,
    "$s4": 22,
    "$s5": 23,
    "$s6": 24,
    "$s7": 25,
    "$k0": 26,
    "$k1": 27,
    "$gp": 28,
    "$sp": 29,
    "$fp": 30,
    "$ra": 31,
}


def to_bin(val, bits):
    """Convierte entero a binario de N bits (soporta negativos)"""
    val = int(val)
    if val < 0:
        val = (1 << bits) + val
    return format(val, f"0{bits}b")


def clean_lines(raw_lines):
    """Limpia comentarios y líneas vacías. Separa etiquetas."""
    cleaned = []
    for line in raw_lines:
        line = line.split("#")[0].strip()  # Quitar comentarios
        if not line:
            continue

        # Manejar etiquetas (ej: "loop: add...")
        if ":" in line:
            parts = line.split(":")
            label = parts[0].strip()
            instruction = parts[1].strip()
            cleaned.append({"type": "label", "content": label})
            if instruction:  # Si hay instrucción en la misma línea
                cleaned.append({"type": "instr", "content": instruction})
        else:
            cleaned.append({"type": "instr", "content": line})
    return cleaned


def first_pass(cleaned_lines):
    """Mapa de etiquetas a número de instrucción (Dirección PC)"""
    labels = {}
    instr_count = 0
    for item in cleaned_lines:
        if item["type"] == "label":
            labels[item["content"]] = instr_count
        else:
            instr_count += 1
    return labels


def assemble(cleaned_lines, labels):
    binary_lines = []
    pc = 0  # Program Counter (índice de instrucción)

    for item in cleaned_lines:
        if item["type"] == "label":
            continue  # Ignorar etiquetas en la 2da vuelta

        line = item["content"]
        parts = line.replace(",", " ").replace("(", " ").replace(")", " ").split()
        instr = parts[0].lower()
        bin_instr = None

        try:
            # --- TIPO R ---
            if instr in FUNCT:
                rd = REGISTERS[parts[1]]
                rs = REGISTERS[parts[2]]
                rt = REGISTERS[parts[3]]
                bin_instr = f"{OPCODES['R-TYPE']}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(rd, 5)}00000{FUNCT[instr]}"

            # --- TIPO I (Cargas/Logica) ---
            elif instr in ["addi", "andi", "ori", "xori", "slti"]:
                rt = REGISTERS[parts[1]]
                rs = REGISTERS[parts[2]]
                imm = int(parts[3])
                bin_instr = (
                    f"{OPCODES[instr]}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(imm, 16)}"
                )

            # --- TIPO I (Memoria) ---
            elif instr in ["lw", "sw"]:
                rt = REGISTERS[parts[1]]
                offset = int(parts[2])
                rs = REGISTERS[parts[3]]
                bin_instr = f"{OPCODES[instr]}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(offset, 16)}"

            # --- TIPO I (Branch - BEQ) ---
            elif instr == "beq":
                rs = REGISTERS[parts[1]]
                rt = REGISTERS[parts[2]]
                label_target = parts[3]

                # Calcular Offset: (Destino - (PC actual + 1))
                if label_target in labels:
                    target_idx = labels[label_target]
                    offset = target_idx - (pc + 1)
                else:
                    offset = int(label_target)  # Si ya era numero

                bin_instr = f"{OPCODES[instr]}{to_bin(rs, 5)}{to_bin(rt, 5)}{to_bin(offset, 16)}"

            # --- TIPO J ---
            elif instr == "j":
                label_target = parts[1]
                if label_target in labels:
                    target_idx = labels[label_target]
                else:
                    target_idx = int(label_target)

                bin_instr = f"{OPCODES[instr]}{to_bin(target_idx, 26)}"

        except Exception as e:
            print(f"Error en instrucción: '{line}' -> {e}")
            return []

        if bin_instr:
            binary_lines.append(bin_instr)
            print(f"PC[{pc}] {line:<25} -> {bin_instr} (Hex: {hex(int(bin_instr, 2))})")
            pc += 1

    return binary_lines


def main():
    # Detectar carpeta actual automáticamente
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "programa.asm")
    output_file = os.path.join(script_dir, "instrucciones.mem")

    print(f"--- Iniciando Ensamblador MIPS ---")
    print(f"Leyendo: {input_file}")

    if not os.path.exists(input_file):
        print(
            "ERROR: No encuentro 'programa.asm'. Asegúrate de que esté en la misma carpeta."
        )
        return

    with open(input_file, "r") as f:
        raw_lines = f.readlines()

    # Paso 1: Limpiar y encontrar etiquetas
    clean_data = clean_lines(raw_lines)
    labels = first_pass(clean_data)
    print(f"Etiquetas encontradas: {labels}")

    # Paso 2: Generar binario
    bin_code = assemble(clean_data, labels)

    # Guardar archivo
    if bin_code:
        with open(output_file, "w") as f:
            for line in bin_code:
                f.write(line + "\n")
        print(f"\n¡ÉXITO! Archivo generado: {output_file}")
    else:
        print("\nFALLO: No se pudo generar el archivo binario.")


if __name__ == "__main__":
    main()
