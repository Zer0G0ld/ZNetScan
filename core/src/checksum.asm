section .text
global fast_checksum

; fast_checksum(const void *data, size_t len)
; Otimizado para cálculos de checksum TCP/IP
; rdi = data, rsi = len
fast_checksum:
    xor     eax, eax
    xor     edx, edx
    mov     rcx, rsi        ; length
    shr     rcx, 1          ; number of 16-bit words
    xor     rdx, rdx        ; sum = 0
    
.loop:
    movzx   eax, word [rdi] ; load word
    add     dx, ax          ; add to sum
    adc     dx, 0           ; add carry
    add     rdi, 2
    dec     rcx
    jnz     .loop
    
    ; Handle odd byte
    test    rsi, 1
    jz      .even
    movzx   eax, byte [rdi]
    add     dx, ax
    adc     dx, 0
    
.even:
    ; Fold 32-bit to 16-bit
    mov     eax, edx
    shr     eax, 16
    add     ax, dx
    adc     ax, 0
    
    ; Complement
    not     ax
    ret