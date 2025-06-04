#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>
#include "tcp_client.h"

// Socket file descriptor
static int sock_fd = -1;

TCPStatus xTCPConnect(const char* ip_address, uint16_t port)
{
    struct sockaddr_in server_addr;
    
    // Create socket
    sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if(sock_fd < 0)
    {
        return TCP_ERROR;
    }
    
    // Configure server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    
    if(inet_pton(AF_INET, ip_address, &server_addr.sin_addr) <= 0)
    {
        close(sock_fd);
        sock_fd = -1;
        return TCP_ERROR;
    }
    
    // Connect to server
    if(connect(sock_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0)
    {
        close(sock_fd);
        sock_fd = -1;
        return TCP_ERROR;
    }
    
    return TCP_OK;
}

TCPStatus xTCPSend(const void* data, size_t length)
{
    if(sock_fd < 0 || data == NULL)
    {
        return TCP_ERROR;
    }
    
    ssize_t sent = send(sock_fd, data, length, 0);
    if(sent < 0)
    {
        if(errno == ECONNRESET || errno == EPIPE)
        {
            return TCP_DISCONNECTED;
        }
        return TCP_ERROR;
    }
    
    return (sent == length) ? TCP_OK : TCP_ERROR;
}

TCPStatus xTCPReceive(void* buffer, size_t length, size_t* received)
{
    if(sock_fd < 0 || buffer == NULL || received == NULL)
    {
        return TCP_ERROR;
    }
    
    ssize_t bytes = recv(sock_fd, buffer, length, 0);
    if(bytes < 0)
    {
        if(errno == ECONNRESET)
        {
            return TCP_DISCONNECTED;
        }
        return TCP_ERROR;
    }
    else if(bytes == 0)
    {
        return TCP_DISCONNECTED;
    }
    
    *received = bytes;
    return TCP_OK;
}

void vTCPDisconnect(void)
{
    if(sock_fd >= 0)
    {
        close(sock_fd);
        sock_fd = -1;
    }
}
