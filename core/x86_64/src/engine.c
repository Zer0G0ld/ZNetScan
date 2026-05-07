#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>

// Forward declaration da função ASM
extern unsigned short fast_checksum(const void *data, size_t len);

// Estrutura de resultado
typedef struct {
    int port;
    int status;  // 0=closed, 1=open, 2=filtered
    long response_time_us;
    unsigned char ttl;
} ScanResult;

// Função exportada para Python
ScanResult* quick_syn_scan(const char *target_ip, int *ports, int port_count, int timeout_ms) {
    ScanResult *results = malloc(sizeof(ScanResult) * port_count);
    struct sockaddr_in target;
    
    // Cria socket raw
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sock < 0) return NULL;
    
    target.sin_family = AF_INET;
    inet_aton(target_ip, &target.sin_addr);
    
    // Configura timeout
    struct timeval tv = { timeout_ms / 1000, (timeout_ms % 1000) * 1000 };
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    
    // Para cada porta, envia SYN packet
    for (int i = 0; i < port_count; i++) {
        unsigned char packet[sizeof(struct iphdr) + sizeof(struct tcphdr)] = {0};
        struct iphdr *iph = (struct iphdr*)packet;
        struct tcphdr *tcph = (struct tcphdr*)(packet + sizeof(struct iphdr));
        
        // Preenche cabeçalhos
        iph->ihl = 5;
        iph->version = 4;
        iph->tot_len = htons(sizeof(packet));
        iph->ttl = 64;
        iph->protocol = IPPROTO_TCP;
        iph->saddr = inet_addr("0.0.0.0");
        iph->daddr = target.sin_addr.s_addr;
        
        tcph->source = htons(12345 + ports[i]);
        tcph->dest = htons(ports[i]);
        tcph->seq = htonl(rand());
        tcph->doff = 5;
        tcph->syn = 1;
        tcph->window = htons(65535);
        
        // Checksum usando ASM
        tcph->check = fast_checksum(tcph, sizeof(struct tcphdr));
        
        // Envia
        results[i].port = ports[i];
        results[i].status = 0;
        
        if (sendto(sock, packet, sizeof(packet), 0, 
                   (struct sockaddr*)&target, sizeof(target)) > 0) {
            // Aguarda resposta
            unsigned char buffer[4096];
            int len = recv(sock, buffer, sizeof(buffer), 0);
            if (len > 0) {
                results[i].status = 1; // open
            }
        }
    }
    
    close(sock);
    return results;
}