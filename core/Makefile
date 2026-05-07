CC = gcc
CFLAGS = -Wall -O3 -fPIC -pthread
LDFLAGS = -shared -pthread
TARGET = libznet_core.so
OBJDIR = build

ARCH := $(shell uname -m)

ifeq ($(ARCH), x86_64)
    AS = nasm
    ASFLAGS = -f elf64
    ASM_SRC = x86_64/src/checksum.asm
    C_SRC = x86_64/src/engine.c
endif

ifeq ($(ARCH), aarch64)
    AS = as
    ASFLAGS = 
    ASM_SRC = arm64/src/checksum.S
    C_SRC = arm64/src/engine.c
endif

C_OBJ = engine.o
ASM_OBJ = checksum.o
OBJS = $(OBJDIR)/$(C_OBJ) $(OBJDIR)/$(ASM_OBJ)

all: info $(TARGET)

info:
	@echo "========================================="
	@echo "Compilando ZNetScan Core"
	@echo "Arquitetura: $(ARCH)"
	@echo "ASM: $(ASM_SRC)"
	@echo "========================================="

$(OBJDIR):
	mkdir -p $(OBJDIR)

$(OBJDIR)/$(C_OBJ): $(C_SRC) | $(OBJDIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/$(ASM_OBJ): $(ASM_SRC) | $(OBJDIR)
	$(AS) $(ASFLAGS) $< -o $@

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $(TARGET) $(OBJS)
	@file $(TARGET)

clean:
	rm -rf $(OBJDIR) $(TARGET)

install:
	cp $(TARGET) ../

.PHONY: all clean install info
