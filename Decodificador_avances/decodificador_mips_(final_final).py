import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# --- Lógica del Decodificador ---

# Mapa de instrucciones escalable.
# Define las instrucciones R-type e I-type soportadas.
INSTRUCTION_MAP = {
    # --- Tipo R (opcode 0) ---
    # Formato: MNEM $rd, $rs, $rt
    "ADD": {"type": "R", "opcode": 0, "funct": 0x20},
    "SUB": {"type": "R", "opcode": 0, "funct": 0x22},
    "OR": {"type": "R", "opcode": 0, "funct": 0x25},
    "AND": {"type": "R", "opcode": 0, "funct": 0x24},
    "SLT": {"type": "R", "opcode": 0, "funct": 0x2A},  # Set on Less Than
    # --- Tipo I ---
    # Formato: MNEM $rt, $rs, immediate
    "ADDI": {"type": "I", "opcode": 0x08},  # Add Immediate
}


def parse_register(reg_str):
    """
    Convierte una cadena de registro (ej. "$10,") en un entero.
    Lanza un ValueError si el formato es incorrecto.
    """
    try:
        # Limpia el string de '$' y ','
        cleaned_str = reg_str.replace("$", "").replace(",", "")
        reg_num = int(cleaned_str)
        if 0 <= reg_num <= 31:
            return reg_num
        else:
            raise ValueError(f"Registro fuera de rango: {reg_str} (debe ser $0-$31)")
    except Exception:
        raise ValueError(f"Formato de registro inválido: {reg_str}")


def parse_immediate(imm_str):
    """
    Convierte una cadena de inmediato (ej. "100" o "-50") en un entero.
    Valida el rango de 16 bits con signo.
    """
    try:
        imm = int(imm_str)
        # Validar rango de 16 bits con signo (-32768 a 32767)
        if not (-32768 <= imm <= 32767):
            raise ValueError(
                f"Valor inmediato fuera de rango (-32768 a 32767): {imm_str}"
            )
        return imm
    except Exception:
        raise ValueError(f"Formato inmediato inválido: {imm_str}")


def decode_r_type(parts, op_details):
    """
    Decodifica una instrucción R-type a su código máquina de 32 bits.
    Formato esperado: MNEMONIC $rd, $rs, $rt
    """
    if len(parts) != 4:
        raise ValueError(
            f"Operandos insuficientes. Se esperaban 3, se obtuvieron {len(parts) - 1}"
        )

    # Convención MIPS: "ADD $rd, $rs, $rt"
    rd = parse_register(parts[1])
    rs = parse_register(parts[2])
    rt = parse_register(parts[3])

    # Obtener detalles de la instrucción
    opcode = op_details["opcode"]
    funct = op_details["funct"]
    shamt = 0  # 0 para estas operaciones

    # Ensamblar la instrucción de 32 bits
    # Formato: opcode[31:26], rs[25:21], rt[20:16], rd[15:11], shamt[10:6], funct[5:0]
    instruction = 0
    instruction |= (opcode & 0x3F) << 26  # 6 bits
    instruction |= (rs & 0x1F) << 21  # 5 bits
    instruction |= (rt & 0x1F) << 16  # 5 bits
    instruction |= (rd & 0x1F) << 11  # 5 bits
    instruction |= (shamt & 0x1F) << 6  # 5 bits
    instruction |= funct & 0x3F  # 6 bits

    return instruction


def decode_i_type(parts, op_details):
    """
    Decodifica una instrucción I-type a su código máquina de 32 bits.
    Formato esperado: MNEMONIC $rt, $rs, immediate
    """
    if len(parts) != 4:
        raise ValueError(
            f"Operandos insuficientes. Se esperaban 3, se obtuvieron {len(parts) - 1}"
        )

    # Convención MIPS: "ADDI $rt, $rs, immediate"
    rt = parse_register(parts[1])
    rs = parse_register(parts[2])
    immediate = parse_immediate(parts[3])

    # Obtener detalles de la instrucción
    opcode = op_details["opcode"]

    # Ensamblar la instrucción de 32 bits
    # Formato: opcode[31:26], rs[25:21], rt[20:16], immediate[15:0]
    instruction = 0
    instruction |= (opcode & 0x3F) << 26  # 6 bits
    instruction |= (rs & 0x1F) << 21  # 5 bits
    instruction |= (rt & 0x1F) << 16  # 5 bits

    # & 0xFFFF asegura que el inmediato (incluso negativo)
    # se trunque a 16 bits (representación en complemento a 2)
    instruction |= immediate & 0xFFFF  # 16 bits

    return instruction


def process_lines(lines):
    """
    Procesa una lista de líneas de código ensamblador.
    Devuelve una tupla (lista_de_instrucciones, mensaje_de_estado).
    Si hay un error, lista_de_instrucciones es None y mensaje_de_estado contiene el error.
    """
    decoded_instructions = []

    for i, line in enumerate(lines):
        line_content = line.strip()

        # Ignorar líneas vacías o comentarios
        if not line_content or line_content.startswith("#"):
            continue

        parts = line_content.split()
        mnemonic = parts[0].upper()

        if mnemonic in INSTRUCTION_MAP:
            details = INSTRUCTION_MAP[mnemonic]
            inst_type = details["type"]

            try:
                inst_code = 0
                if inst_type == "R":
                    inst_code = decode_r_type(parts, details)
                elif inst_type == "I":
                    inst_code = decode_i_type(parts, details)
                # elif inst_type == 'J':
                #     inst_code = decode_j_type(parts, details) # Para futura expansión
                else:
                    return (
                        None,
                        f"Error en línea {i + 1}: Tipo de instrucción '{inst_type}' no soportado.",
                    )

                decoded_instructions.append(inst_code)

            except Exception as e:
                return None, f"Error en línea {i + 1} ('{line}'): {e}"
        else:
            return None, f"Error en línea {i + 1}: Instrucción desconocida '{mnemonic}'"

    if not decoded_instructions:
        return None, "No se encontraron instrucciones válidas para decodificar."

    return (
        decoded_instructions,
        f"Decodificación exitosa: {len(decoded_instructions)} instrucciones procesadas.",
    )


def save_big_endian(instructions, filename):
    """
    Guarda la lista de instrucciones de 32 bits en un archivo
    como bytes en formato Big Endian.
    """
    try:
        with open(filename, "wb") as f:  # 'wb' = write binary
            for inst in instructions:
                # Desglosar la instrucción de 32 bits en 4 bytes (Big Endian)
                # Byte 0 (MSB) = bits [31:24]
                # Byte 1       = bits [23:16]
                # Byte 2       = bits [15:8]
                # Byte 3 (LSB) = bits [7:0]
                f.write(inst.to_bytes(4, byteorder="big"))

        return True, f"Archivo guardado exitosamente en:\n{filename}"
    except Exception as e:
        return False, f"Error al guardar archivo: {e}"


# --- Interfaz Gráfica (GUI) ---


class MipsDecoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Decodificador MIPS (Final) - R, I")

        # Configurar un padding principal
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Área de texto para entrada
        tk.Label(
            main_frame, text="Escribe tus instrucciones MIPS aquí o carga un archivo:"
        ).pack(anchor="w")

        self.text_input = scrolledtext.ScrolledText(
            main_frame, height=15, width=60, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Insertar ejemplo
        example_code = """# Ejemplo de código
# --- Tipo R ---
ADD $10, $3, $4
SUB $8, $8, $9
OR $2, $2, $1
AND $5, $6, $7
SLT $1, $3, $4  # $1 = 1 si $3 < $4, sino 0

# --- Tipo I ---
ADDI $12, $10, 100 # $12 = $10 + 100
ADDI $13, $8, -50  # $13 = $8 - 50
"""
        self.text_input.insert(tk.END, example_code)

        # 2. Frame para botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.btn_load = tk.Button(
            button_frame, text="Buscar Archivo (.txt)", command=self.load_file
        )
        self.btn_load.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_decode = tk.Button(
            button_frame,
            text="Decodificar y Guardar",
            command=self.decode_and_save,
            font=("Arial", 10, "bold"),
        )
        self.btn_decode.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 3. Etiqueta de estado
        tk.Label(main_frame, text="Estado:").pack(anchor="w", pady=(10, 0))
        self.status_label = tk.Label(
            main_frame,
            text="Listo.",
            relief=tk.SUNKEN,
            anchor="w",
            justify=tk.LEFT,
            bg="#f0f0f0",
            height=3,
            padx=5,
            wraplength=580,
        )
        self.status_label.pack(fill=tk.X, expand=False)

    def update_status(self, message, is_error=False):
        """Actualiza la etiqueta de estado con un mensaje y color."""
        if is_error:
            self.status_label.config(text=message, fg="red", bg="#fff0f0")
        else:
            self.status_label.config(text=message, fg="black", bg="#f0f0f0")

    def load_file(self):
        """Abre un diálogo para seleccionar un archivo .txt y lo carga en el área de texto."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return  # El usuario canceló

        content = ""
        try:
            # --- MODIFICACIÓN ---
            # Intentar leer como UTF-8 (estándar moderno) primero.
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Si falla UTF-8 (como en el error '0xf3'),
            # intentar con 'latin-1', que es común en Windows
            # para archivos de texto antiguos.
            try:
                with open(filepath, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as e:
                # Si ambos fallan, mostrar el error
                self.update_status(f"Error al cargar archivo: {e}", is_error=True)
                messagebox.showerror(
                    "Error al Cargar",
                    f"No se pudo leer el archivo (se intentó UTF-8 y Latin-1):\n{e}",
                )
                return
        except Exception as e:
            # Capturar otros errores (ej. permiso denegado)
            self.update_status(f"Error al cargar archivo: {e}", is_error=True)
            messagebox.showerror("Error al Cargar", f"No se pudo leer el archivo:\n{e}")
            return

        # Si todo salió bien (con UTF-8 o Latin-1), cargar el contenido
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, content)
        self.update_status(f"Archivo cargado: {filepath}")

    def decode_and_save(self):
        """Toma el texto, lo procesa y guarda el binario de salida."""
        content = self.text_input.get("1.0", tk.END)
        lines = content.splitlines()

        # 1. Procesar las líneas
        instructions, message = process_lines(lines)

        if instructions is None:
            # Hubo un error durante la decodificación
            self.update_status(message, is_error=True)
            messagebox.showerror("Error de Decodificación", message)
            return

        # 2. Pedir ubicación para guardar
        savepath = filedialog.asksaveasfilename(
            title="Guardar archivo binario de salida",
            defaultextension=".bin",
            filetypes=[("Binary files (*.bin)", "*.bin"), ("All files (*.*)", "*.*")],
        )

        if not savepath:
            self.update_status("Guardado cancelado por el usuario.")
            return  # El usuario canceló

        # 3. Guardar el archivo
        success, save_message = save_big_endian(instructions, savepath)

        if success:
            self.update_status(save_message)
            messagebox.showinfo("Éxito", save_message)
        else:
            self.update_status(save_message, is_error=True)
            messagebox.showerror("Error al Guardar", save_message)


# --- Punto de entrada principal ---
if __name__ == "__main__":
    root = tk.Tk()

    # Centrar la ventana (opcional)
    window_width = 600
    window_height = 450
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.minsize(500, 400)  # Tamaño mínimo

    app = MipsDecoderApp(root)
    root.mainloop()
