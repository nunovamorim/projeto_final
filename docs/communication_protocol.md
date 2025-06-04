# Protocolo de Comunicação Satélite-Ground Station

## 1. Visão Geral

Este documento especifica o protocolo de comunicação entre o satélite simulado e a Ground Station. O protocolo é baseado em TCP/IP e utiliza um formato de mensagem personalizado para garantir a integridade e confiabilidade da comunicação.

## 2. Estrutura das Mensagens

### 2.1 Cabeçalho Comum (8 bytes)
```c
struct MessageHeader {
    uint8_t  sync[2];     // Bytes de sincronização (0xAA, 0x55)
    uint8_t  type;        // Tipo da mensagem
    uint8_t  flags;       // Flags de controle
    uint16_t length;      // Comprimento dos dados
    uint16_t checksum;    // CRC-16 dos dados
};
```

### 2.2 Tipos de Mensagens
- 0x01: Comando ADCS
- 0x02: Solicitação de Telemetria
- 0x03: Dados de Telemetria
- 0x04: Acknowledgment
- 0x05: Error
- 0xFF: Heartbeat

### 2.3 Flags de Controle
- Bit 0: Requer ACK
- Bit 1: Mensagem fragmentada
- Bit 2: Último fragmento
- Bit 3-7: Reservado

## 3. Formatos Específicos de Mensagens

### 3.1 Comando ADCS (Type 0x01)
```c
struct ADCSCommand {
    float roll;    // Ângulo de rolagem desejado
    float pitch;   // Ângulo de arfagem desejado
    float yaw;     // Ângulo de guinada desejado
};
```

### 3.2 Dados de Telemetria (Type 0x03)
```c
struct TelemetryData {
    uint32_t timestamp;     // Timestamp em milissegundos
    float    temperature;   // Temperatura em Celsius
    float    power;        // Consumo de energia em Watts
    float    battery;      // Nível da bateria em %
    struct {
        float roll;        // Ângulo atual de rolagem
        float pitch;       // Ângulo atual de arfagem
        float yaw;         // Ângulo atual de guinada
        uint8_t mode;      // Modo de controle ADCS
    } adcs;
};
```

## 4. Fluxo de Comunicação

### 4.1 Estabelecimento de Conexão
1. Ground Station inicia conexão TCP com o satélite
2. Após conexão estabelecida, ambos trocam mensagens Heartbeat
3. Conexão é considerada estabelecida após troca bem-sucedida

### 4.2 Manutenção da Conexão
- Heartbeats são trocados a cada 5 segundos
- Ausência de heartbeat por 15 segundos indica perda de conexão
- Reconexão automática é tentada a cada 5 segundos

### 4.3 Envio de Comandos
1. Ground Station envia comando com flag "Requer ACK"
2. Satélite processa comando e envia ACK
3. Ground Station aguarda confirmação por até 5 segundos
4. Reenvio automático após timeout

### 4.4 Telemetria
1. Satélite envia dados de telemetria periodicamente (1 Hz)
2. Ground Station confirma recebimento com ACK se solicitado
3. Dados são armazenados e exibidos no dashboard

## 5. Tratamento de Erros

### 5.1 Tipos de Erros
- 0x01: Comando inválido
- 0x02: Checksum inválido
- 0x03: Timeout
- 0x04: Parâmetros inválidos
- 0x05: Estado inválido

### 5.2 Recuperação de Erros
- Comandos com erro são rejeitados com mensagem de erro
- Telemetria perdida é ignorada (próximo pacote contém dados atualizados)
- Erros de conexão levam a tentativas de reconexão

## 6. Considerações de Segurança

### 6.1 Integridade
- Checksum CRC-16 em todas as mensagens
- Validação de sequência e formato de dados

### 6.2 Disponibilidade
- Watchdog monitora comunicação
- Reconexão automática
- Buffer circular para mensagens

## 7. Exemplos de Mensagens

### 7.1 Comando ADCS
```
AA 55 01 01 0C 00 XX XX | 00 00 80 3F 00 00 00 00 00 00 00 00
```
Header:
- AA 55: Sync bytes
- 01: Type (ADCS Command)
- 01: Flags (Require ACK)
- 0C 00: Length (12 bytes)
- XX XX: Checksum
Data:
- 00 00 80 3F: roll (1.0 float)
- 00 00 00 00: pitch (0.0 float)
- 00 00 00 00: yaw (0.0 float)

### 7.2 Telemetria
```
AA 55 03 00 18 00 XX XX | [24 bytes of telemetry data]
```
