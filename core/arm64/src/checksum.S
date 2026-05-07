// ARM64 assembly para cálculo de checksum TCP/IP
// Sintaxe GNU Assembler (GAS) para aarch64

.section .text
.global fast_checksum

// fast_checksum(const void *data, size_t len)
// x0 = ponteiro dos dados, x1 = tamanho (len)
// Retorno: w0 (valor do checksum de 16 bits)

fast_checksum:
    mov     x2, #0              // Inicializa acumulador de 64 bits em 0

.Lloop:
    cmp     x1, #2
    blt     .Lodd_byte          // Se sobrar menos de 2 bytes, trata o byte ímpar

    ldrh    w3, [x0], #2        // Carrega 16 bits (half-word) e avança o ponteiro
    add     x2, x2, x3          // Adiciona à soma
    sub     x1, x1, #2          // Decrementa o tamanho
    b       .Lloop

.Lodd_byte:
    cbz     x1, .Lfold          // Se len for 0, pula para o fechamento
    ldrb    w3, [x0]            // Carrega o último byte restante
    add     x2, x2, x3          // Adiciona à soma

.Lfold:
    // Redução do acumulador de 64 bits para 16 bits (1's complement fold)
    lsr     x3, x2, #32
    add     x2, x2, x3
    lsr     x3, x2, #16
    add     x2, x2, x3
    
    // Máscara para garantir 16 bits e tratar carries finais
    and     w3, w2, #0xFFFF
    lsr     w2, w2, #16
    add     w3, w3, w2
    
    mvn     w0, w3              // Aplica o NOT (complemento de 1)
    and     w0, w0, #0xFFFF     // Garante o retorno de apenas 16 bits
    ret

// Diretiva de segurança para o linker (evita aviso de pilha executável)
.section .note.GNU-stack,"",%progbits

