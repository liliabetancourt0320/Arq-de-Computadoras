# Programa: Filtro de Paridad
main:
    addi $t0, $zero, 0      # Base address
    addi $t1, $zero, 0      # i = 0
    addi $t2, $zero, 5      # N = 5
    addi $t5, $zero, 0      # Acumulador = 0
    addi $t6, $zero, 50     # Umbral = 50

loop:
    # Calcular direccion
    add $t7, $t0, $t1       
    
    # Cargar dato (LW)
    lw $t3, 0($t7)          
    
    # 1. Verificar > 50
    slt $t4, $t6, $t3       
    beq $t4, $zero, next    

    # 2. Verificar Paridad
    andi $t4, $t3, 1
    addi $t8, $zero, 1      
    beq $t4, $t8, next      

    # 3. Sumar
    add $t5, $t5, $t3

next:
    addi $t1, $t1, 4        
    addi $t9, $zero, 20     
    beq $t1, $t9, end_loop
    j loop

end_loop:
    sw $t5, 100($zero)      
    j end_loop