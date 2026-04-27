CC = gcc
NASM = nasm
CFLAGS = -Wall -O3 -fPIC -pthread -march=native
LDFLAGS = -shared -pthread

TARGET = libznet_core.so
OBJDIR = build

SRCS_C = src/engine.c
SRCS_ASM = src/checksum.asm
OBJS = $(addprefix $(OBJDIR)/, $(notdir $(SRCS_C:.c=.o))) \
       $(addprefix $(OBJDIR)/, $(notdir $(SRCS_ASM:.asm=.o)))

all: $(TARGET)

$(OBJDIR):
	mkdir -p $(OBJDIR)

$(OBJDIR)/%.o: src/%.c | $(OBJDIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJDIR)/%.o: src/%.asm | $(OBJDIR)
	$(NASM) -f elf64 $< -o $@

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $(TARGET) $(OBJS)

clean:
	rm -rf $(OBJDIR) $(TARGET)

install:
	cp $(TARGET) ../znet_core.so

.PHONY: all clean install