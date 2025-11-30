==================================================
1. DESCRIPCIÓN
Este programa es una aplicación gráfica (GUI) desarrollada en Python con Tkinter.
Su objetivo es leer instrucciones en ensamblador MIPS (Tipos R e I), decodificarlas
a su equivalente en código máquina MIPS32 de 32 bits, y guardar el resultado en un
archivo binario (.bin) en formato Big Endian.
Instrucciones Soportadas:
* Tipo R: ADD, SUB, OR, AND, SLT
* Tipo I: ADDI
==================================================
2. REQUISITOS
* Python 3.x (con la biblioteca Tkinter incluida, que es estándar en la
instalación de Python para Windows y macOS).
==================================================
   3. INSTRUCCIONES DE EJECUCIÓN
Para ejecutar el programa, simplemente corre el script de Python desde tu terminal
o un IDE:
python decodificador_mips_final.py
(Si tu sistema usa 'python3' para distinguir, utiliza ese comando en su lugar).
==================================================
   4. CÓMO USAR LA APLICACIÓN
4.1 Escribir Código:
Puedes escribir tus instrucciones MIPS directamente en el cuadro de texto principal.
4.2 Cargar un Archivo:
      * Haz clic en el botón "Buscar Archivo (.txt)".
      * Se abrirá un diálogo para que selecciones un archivo de texto con tu código.
      * El programa maneja archivos codificados en UTF-8 y Latin-1 (ANSI).
      5. Decodificar y Guardar:
      * Una vez que tu código esté en el cuadro de texto, haz clic en el botón
"Decodificar y Guardar".
      * Si el programa encuentra un error (ej. 'XOR $1, $2, $3'), se detendrá
y te mostrará un mensaje de error con el número de línea.
      * Si todo el código es válido, te pedirá que elijas dónde guardar el
archivo de salida (ej. 'salida.bin').
         6. Formato del Código de Entrada:
         * El programa ignora líneas vacías.
         * El programa ignora cualquier línea que comience con un símbolo de
comentario ('#').
         * Los comentarios al final de una línea (ej. 'ADD $1, $2, $3 # Esto es un comentario')
también son ignorados.