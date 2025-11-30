Manual de Usuario y Guía de Instalación
Procesador MIPS32 Pipeline
Guía de instalación, configuración y simulación. 
1. Estructura del Proyecto
El sistema integra una simulación de hardware en Verilog y una herramienta de software en Python para la traducción bidireccional entre el lenguaje ensamblador y el código máquina.
Hardware (Verilog)
* mips_pipeline.v: Módulo principal (Top Level). Conecta todas las etapas del procesador.
* modules.v: Contiene los submódulos: ALU, Unidad de Control, Memoria de Instrucciones/Datos y Banco de Registros.
* testbench.v: Generador de señales de reloj y reset para la simulación.
Software & Código
* Codificador.py: Interfaz gráfica desarrollada en Python. Soporta la carga de archivos .asm y .bin para:
   * Codificar: Traducir de Assembly (.asm) a Hexadecimal/Binario.
   * Decodificar: Traducir de Código Máquina a Assembly.
* programa.asm: Código fuente en ensamblador MIPS que contiene el algoritmo del "Filtro de Paridad".
* instrucciones.mem: Archivo de salida generado por el codificador, necesario para la memoria del procesador.
2. Requisitos del Sistema
Para la correcta ejecución del proyecto es necesario contar con el siguiente software instalado:
1. Visual Studio Code (o IDE compatible con Python):
   * Requerido para ejecutar el script Codificador.py.
   * Nota: Debe tener Python 3.x instalado en el sistema.
2. ModelSim (Intel/Altera o Mentor Graphics):
   * Requerido para compilar los archivos Verilog y visualizar la simulación de hardware.
3. Guía de Instalación y Uso
Funcionalidad A: Codificación (Assembly → Máquina)
Antes de simular, es necesario traducir el programa ensamblador a un formato legible por el procesador.
1. Ejecutar Herramienta: Abra el archivo Codificador.py en Visual Studio Code y ejecútelo.
2. Subir Archivo .asm:
   * Haga clic en el botón "Abrir archivo".
   * En el explorador de archivos, seleccione su archivo de código fuente (por ejemplo, programa.asm o cualquier otro archivo .asm / .txt).
   * El código se cargará automáticamente en el editor de entrada.
3. Configurar: Asegúrese de que el Modo esté en "Codificar" y el Formato de salida en "Binario".
4. Convertir y Guardar:
   * Presione el botón "Convertir".
   * Haga clic en "Guardar resultado".
   * Importante: Guarde el archivo con el nombre exacto instrucciones.mem en la misma carpeta que los archivos Verilog.
Funcionalidad B: Decodificación (Máquina → Assembly)
Esta herramienta permite ingeniería inversa para recuperar el código fuente original a partir de un archivo binario o hexadecimal.
1. Cambiar Modo: En la parte superior de la interfaz, seleccione el modo Decodificar.
2. Subir Archivo Binario: Haga clic en "Abrir archivo" para cargar un archivo .bin o .mem, o pegue el código manualmente.
3. Configurar Entrada:
   * Si el código son ceros y unos (00101...), seleccione Entrada: Binario.
   * Si el código es hexadecimal (20080...), seleccione Entrada: Hexadecimal.
4. Convertir: Presione el botón "Convertir". El código Assembly recuperado aparecerá en el panel de salida.
Funcionalidad C: Simulación de Hardware (ModelSim)
Una vez generado el archivo de memoria (instrucciones.mem), configure el entorno de simulación.
1. Crear Proyecto: Abra ModelSim y cree un nuevo proyecto (File > New > Project).
2. Añadir Archivos: Agregue los archivos mips_pipeline.v, modules.v y testbench.v al proyecto.
3. Configurar Ruta de Memoria:
   * Abra el archivo modules.v en el editor de ModelSim.
   * Busque la línea que contiene $readmemb.
   * Edite la ruta dentro de las comillas para que apunte a la ubicación de su archivo instrucciones.mem.
   * Nota: Use barras diagonales normales (/) en la ruta.
4. Compilar: Haga clic en "Compile All". Verifique que no haya errores.
5. Simular:
   * Vaya a Simulate > Start Simulation.
   * Expanda la librería work y seleccione testbench.
   * En la ventana de objetos, añada a la onda (Wave) las señales: clk, reset y wb_final_data.
   * Ejecute el comando: run 2000 en la consola.
4. Lógica del Programa (Assembly)
El archivo programa.asm implementa un algoritmo de filtrado de datos con la siguiente lógica:
* Entrada: Lee un arreglo de 5 números desde la memoria.
* Condición 1 (Magnitud): Verifica si el número es mayor a 50.
* Condición 2 (Paridad): Verifica si el número es impar.
* Acción: Si el número cumple ambas condiciones (es mayor a 50 y es impar), se suma a un acumulador (Registro $t5).
* Salida: Al finalizar el ciclo, el resultado total se escribe en la dirección de memoria 100.