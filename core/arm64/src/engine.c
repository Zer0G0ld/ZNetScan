#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>
#include <signal.h>

// Forward declaration da função ASM ARM64
extern unsigned short fast_checksum(const void *data, size_t len);

// Estrutura de resultado
typedef struct {
    int port;
    int status;  // 0=closed, 1=open
    long response_time_us;
    unsigned char ttl;
} ScanResult;

// TCP Connect scan - NÃO precisa de root! Ideal para Termux
ScanResult* tcp_connect_scan(const char *target_ip, int *ports, int port_count, int timeout_ms) {
    ScanResult *results = malloc(sizeof(ScanResult) * port_count);
    struct sockaddr_in target;
    
    if (!results) return NULL;
    
    // Ignorar SIGPIPE para não matar o processo
    signal(SIGPIPE, SIG_IGN);
    
    target.sin_family = AF_INET;
    if (inet_aton(target_ip, &target.sin_addr) == 0) {
        free(results);
        return NULL;
    }
    
    for (int i = 0; i < port_count; i++) {
        struct timeval start, end;
        gettimeofday(&start, NULL);
        
        // Create socket
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            results[i] = (ScanResult){ports[i], 0, 0, 0};
            continue;
        }
        
        // Evitar SIGPIPE no socket também
        int opt = 1;
        setsockopt(sock, SOL_SOCKET, SO_NOSIGPIPE, &opt, sizeof(opt));
        
        // Set non-blocking mode
        int flags = fcntl(sock, F_GETFL, 0);
        fcntl(sock, F_SETFL, flags | O_NONBLOCK);
        
        // Reinicializar timeout para cada porta
        struct timeval tv = { timeout_ms / 1000, (timeout_ms % 1000) * 1000 };
        setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
        
        target.sin_port = htons(ports[i]);
        int ret = connect(sock, (struct sockaddr*)&target, sizeof(target));
        
        results[i].port = ports[i];
        results[i].status = 0;
        
        if (ret < 0 && errno == EINPROGRESS) {
            fd_set fdset;
            FD_ZERO(&fdset);
            FD_SET(sock, &fdset);
            
            // select com timeout reinicializado
            if (select(sock + 1, NULL, &fdset, NULL, &tv) > 0) {
                int so_error;
                socklen_t len = sizeof(so_error);
                getsockopt(sock, SOL_SOCKET, SO_ERROR, &so_error, &len);
                results[i].status = (so_error == 0) ? 1 : 0;
            }
        } else if (ret == 0) {
            results[i].status = 1;  // Connected immediately
        }
        
        gettimeofday(&end, NULL);
        results[i].response_time_us =
            (end.tv_sec - start.tv_sec) * 1000000 +
            (end.tv_usec - start.tv_usec);
        
        // Get TTL if possible
        results[i].ttl = 0;
        socklen_t ttl_len = sizeof(results[i].ttl);
        getsockopt(sock, IPPROTO_IP, IP_TTL, &results[i].ttl, &ttl_len);
        
        close(sock);
    }
    
    return results;
}

// Função exportada para Python - usa TCP Connect (compatível com Termux)
ScanResult* quick_syn_scan(const char *target_ip, int *ports, int port_count, int timeout_ms) {
    // Em ARM64/Termux, usamos TCP Connect (não precisa de root)
    return tcp_connect_scan(target_ip, ports, port_count, timeout_ms);
}
