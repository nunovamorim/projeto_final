# Projeto

## 1. Planeamento Inicial e Preparação do Ambiente

### 1.1. **Definir requisitos funcionais e não funcionais**

- Confirmar os processos essenciais a implementar: MAIN_SO, TC_proc, ADCS_proc, TM_proc.
- Especificar objetivos claros para cada processo (função, comunicação, prioridade).
- Definir métricas de teste (latência, CPU, memória, fiabilidade).

**1.1.1 Requisitos Funcionais (RF)**

Os requisitos funcionais descrevem o que o sistema deve fazer, ou seja, as funcionalidades específicas que o RTOS deve suportar no contexto do satélite simulado:

- **RF1 - Implementação de processos essenciais**
    
    O sistema deve implementar os quatro processos principais:
    
    - **MAIN_SO**: Gestão central do sistema operativo, coordenação das tarefas, processamento de comandos recebidos e envio de respostas.
    - **TC_proc (Telecommand Process)**: Receção e interpretação dos comandos enviados da Ground Station para controlar o satélite.
    - **ADCS_proc (Attitude Determination and Control System Process)**: Simulação da determinação e controlo da atitude do satélite, responsável pelo posicionamento e orientação.
    - **TM_proc (Telemetry Process)**: Coleta, formatação e envio de dados de telemetria para a Ground Station.
- **RF2 - Comunicação interprocessos**
    
    Deve garantir comunicação eficiente e sincronizada entre os processos, por exemplo, usando filas (queues) para troca de mensagens.
    
- **RF3 - Comunicação externa**
    
    O sistema deve enviar telemetria para a Ground Station e receber comandos via protocolo de comunicação TCP/IP na rede interna.
    
- **RF4 - Escalonamento e prioridade de tarefas**
    
    O RTOS deve suportar escalonamento preemptivo baseado em prioridades definidas para garantir resposta determinística às tarefas críticas.
    
- **RF5 - Gestão de falhas básicas**
    
    Deve ser possível detetar falhas em tarefas (exemplo: bloqueios) e acionar mecanismos de recuperação, como reinicialização de tarefas ou sistema.
    

**1.1.2 Requisitos Não Funcionais (RNF)**

Estes requisitos definem as qualidades e restrições do sistema, importantes para garantir desempenho, fiabilidade e eficiência, fundamentais em sistemas embarcados de satélites LEO:

- **RNF1 - Limitação de recursos**
    
    O sistema deve operar dentro dos recursos computacionais limitados simulados no QEMU (ex.: memória restrita, CPU limitada).
    
- **RNF2 - Tempo de resposta determinístico**
    
    As tarefas críticas devem ser executadas dentro de limites temporais definidos para assegurar o controlo adequado do satélite.
    
- **RNF3 - Robustez e fiabilidade**
    
    O sistema deve manter operação contínua mesmo perante falhas simuladas, assegurando a recuperação rápida sem necessidade de reinício total.
    
- **RNF4 - Eficiência energética (simulada)**
    
    Apesar de em ambiente virtual, o RTOS deve contemplar estratégias para otimizar o uso do processador, simulando gestão de energia.
    
- **RNF5 - Segurança e integridade da comunicação**
    
    Os dados trocados entre Satélite e Ground Station devem garantir integridade e evitar corrupção, mesmo em ambiente simulado.
    
- **RNF6 - Facilidade de monitorização e testes**
    
    O sistema deve gerar logs e métricas que permitam avaliar desempenho e detetar problemas facilmente.
    

**1.1.3 Definição de Métricas e Critérios de Teste**

Para validar o funcionamento e desempenho do RTOS simulado, serão definidas métricas quantificáveis e critérios para avaliação:

- **Latência de resposta**
    
    Medir o tempo desde a receção de um comando na Ground Station até a sua execução confirmada no satélite, em milissegundos.
    
- **Utilização de CPU e memória**
    
    Avaliar a percentagem média e máxima de utilização dos recursos computacionais pela execução dos processos.
    
- **Taxa de falhas e tempo de recuperação**
    
    Quantificar o número de falhas simuladas (exemplo: bloqueios) e medir o tempo médio necessário para recuperação e restabelecimento do funcionamento.
    
- **Taxa de sucesso na comunicação**
    
    Percentagem de mensagens enviadas e recebidas sem erros ou perdas, incluindo validação da integridade dos dados.
    
- **Disponibilidade do sistema**
    
    Percentagem de tempo em que o sistema está operacional e a responder a comandos sem falhas críticas.
    

---

### **1.2. Configurar ambiente virtual**

- Criar duas VMs Hyper-V (Satélite e Ground Station) com IP fixo em rede interna.
- Instalar Pop!_OS nas duas VMs.
- Configurar QEMU na VM Satélite para executar FreeRTOS em arquitetura POSIX (emulação simplificada).

**Passos para a Configuração**

1. **Escolha da Plataforma de Emulação (Arquitetura POSIX)**
    - Optar por executar FreeRTOS numa plataforma POSIX simulada dentro do QEMU, que permite correr o kernel FreeRTOS num sistema operativo Linux hospedado, simplificando o desenvolvimento e testes.
    - Esta configuração reduz a complexidade da emulação de hardware específico (ex.: ARM Cortex-M) e permite uso direto das chamadas POSIX para temporização e gestão de tarefas, com menor overhead.
2. **Instalação e Configuração do QEMU na VM Satélite**
    - Instalar o QEMU no Pop!_OS da VM Satélite via gestor de pacotes (ex.: `sudo apt install qemu`).
    - Garantir que o QEMU suporta a arquitetura desejada (x86_64, ARM ou a arquitetura de emulação POSIX).
    - Configurar rede interna entre a VM Satélite e Ground Station para permitir comunicação TCP/IP entre QEMU e dashboard.
3. **Compilação do FreeRTOS para Ambiente POSIX**
    - Obter o código fonte do FreeRTOS com suporte POSIX (ex.: port POSIX disponível no repositório oficial).
    - Adaptar e compilar o FreeRTOS para correr como processo no Linux da VM, utilizando o QEMU para isolar e limitar recursos (memória, CPU).
    - Configurar o projeto para simular as restrições típicas de um sistema embarcado, limitando recursos e temporização para aproximar-se do comportamento real.
4. **Configuração de Limitação de Recursos no QEMU**
    - Definir limites explícitos de CPU (ex.: capping em 10-20% de uso) e memória (ex.: 64MB ou menos) para simular hardware de satélite.
    - Utilizar opções do QEMU para simular temporizações e interrupções que representem um sistema embarcado.
5. **Implementação da Comunicação entre QEMU (FreeRTOS) e Ground Station**
    - Configurar canais de comunicação virtuais (ex.: sockets TCP/IP bridged entre QEMU e a rede da VM).
    - Garantir que o FreeRTOS na emulação POSIX inclui cliente TCP para envio de telemetria e receção de comandos.
6. **Validação da Configuração**
    - Executar FreeRTOS no QEMU, verificar que as tasks correm corretamente dentro do ambiente POSIX.
    - Testar envio/receção básica de mensagens TCP para a Ground Station.
    - Confirmar que as restrições de recursos estão ativas e observáveis (medir latência, uso CPU/memória).
    - Definir método de comunicação entre VMs (exemplo: sockets TCP/IP para simular comunicação satélite-terra).
    

---

## 2. Design e Arquitetura do RTOS Simulado

### 2.1. **Escolha arquitetural do kernel**

- Optar por kernel baseado em FreeRTOS padrão (microkernel simples com scheduler preemptivo por prioridades).
- Definir prioridades para os processos: MAIN_SO (mais alta), TC_proc, ADCS_proc, TM_proc (mais baixa).

**2.1.1 Fundamentação da escolha do kernel FreeRTOS**

- **Microkernel simples e leve:**
    
    O FreeRTOS é um sistema operativo de tempo real com arquitetura de microkernel que proporciona uma estrutura modular e leve, adequada a sistemas embarcados com recursos limitados, como satélites LEO. Esta arquitetura permite a execução de múltiplas tarefas isoladas e uma gestão eficiente dos recursos computacionais.
    
- **Escalonamento preemptivo por prioridades:**
    
    O FreeRTOS utiliza um escalonador preemptivo baseado em prioridades, fundamental para sistemas críticos onde tarefas de alta prioridade devem garantir resposta rápida e determinística, característica essencial para controlar processos críticos do satélite, como telemetria e controlo de atitude.
    
- **Facilidade de configuração e portabilidade:**
    
    A vasta adoção do FreeRTOS na indústria aeroespacial e a sua disponibilidade para múltiplas arquiteturas facilita a adaptação e integração com hardware real ou simulado, tornando-o uma escolha sólida para desenvolvimento e estudo.
    

**2.1.2 Definição das prioridades das tarefas**

A atribuição de prioridades é determinante para garantir que tarefas críticas recebem tempo de CPU suficiente para cumprir requisitos temporais rigorosos, enquanto tarefas menos críticas operam em segundo plano.

- **MAIN_SO (Prioridade mais alta):**
    
    Como o processo central de gestão do sistema operativo, coordena as restantes tarefas, controla o fluxo de comandos e garante a integridade operacional. Requer prioridade máxima para assegurar rápida resposta a eventos críticos e orquestração eficaz.
    
- **TC_proc (Prioridade alta):**
    
    Responsável pela receção e processamento dos comandos enviados pela Ground Station, deve possuir prioridade elevada para garantir que comandos são tratados sem atrasos, evitando latência que possa comprometer o controlo do satélite.
    
- **ADCS_proc (Prioridade média):**
    
    Simula o controlo de atitude e orientação do satélite, que embora crítico, pode tolerar ligeiros atrasos em relação ao processamento de comandos, justificando uma prioridade intermediária.
    
- **TM_proc (Prioridade mais baixa):**
    
    Dedicado à recolha e envio de telemetria para a Ground Station, é fundamental mas menos crítico em termos de tempo real imediato, podendo operar em background sem comprometer as operações principais.
    

**2.1.3 Justificação do modelo arquitetural**

A escolha de um microkernel simples com escalonamento preemptivo e prioridades fixas assegura:

- **Determinismo temporal**: Garantia de execução das tarefas críticas dentro de prazos definidos, indispensável para aplicações espaciais.
- **Modularidade e isolamento**: Facilita a identificação e tratamento de falhas, aumentando a robustez do sistema.
- **Eficiência no uso de recursos**: Adequado para o ambiente restrito de satélites LEO, onde memória e CPU são limitadas.

### 2.2. **Definição das tarefas e suas funcionalidades**

- MAIN_SO: Gestão global, recepção e despacho de comandos.
- TC_proc: Processamento de comandos de telecontrolo.
- ADCS_proc: Simulação de controlo de atitude (orientação do satélite).
- TM_proc: Telemetria e envio de dados para a Ground Station.
    
    

**2.2.1 MAIN_SO (Sistema Operativo Principal)**

- **Função principal:**
    
    Atua como o gestor central do RTOS, responsável pela coordenação global das tarefas, gestão dos recursos do sistema e controlo do fluxo de dados e comandos.
    
- **Responsabilidades específicas:**
    - Inicializar o sistema e os recursos partilhados (filas, buffers, semáforos).
    - Receber e validar comandos provenientes da Ground Station via TC_proc.
    - Despachar comandos para as tarefas específicas (ex.: enviar instruções ao ADCS_proc).
    - Monitorizar o estado das tarefas, detectar falhas ou anomalias e tomar ações corretivas (ex.: reiniciar tarefas).
    - Gerir a sincronização e comunicação interprocessos para assegurar a coerência dos dados.
- **Importância:**
    
    Esta tarefa é crítica para o funcionamento integrado do sistema, funcionando como núcleo decisor e supervisor.
    

**2.2.2 TC_proc (Processo de Telecontrolo)**

- **Função principal:**
    
    Responsável pela receção, interpretação e pré-processamento dos comandos enviados pela Ground Station, garantindo que são corretamente formatados e encaminhados para execução.
    
- **Responsabilidades específicas:**
    - Estabelecer e manter a ligação de comunicação TCP/IP com a Ground Station.
    - Receber comandos de telecontrolo, validar a sua integridade e autenticidade (se aplicável).
    - Converter os comandos recebidos em mensagens internas que possam ser interpretadas pelo MAIN_SO.
    - Enviar feedback inicial de receção dos comandos à Ground Station.
- **Importância:**
    
    Constitui o interface principal de controlo externo, sendo fundamental garantir baixa latência e elevada fiabilidade nesta tarefa.
    

**2.2.3 ADCS_proc (Processo de Determinação e Controlo de Atitude)**

- **Função principal:**
    
    Simular o controlo da orientação do satélite, essencial para garantir que o satélite mantém a posição e o alinhamento adequados durante a missão.
    
- **Responsabilidades específicas:**
    - Processar dados de sensores simulados (ex.: giroscópios, acelerómetros) para determinar a atitude atual.
    - Executar algoritmos de controlo para ajustar a orientação conforme comandos recebidos (ex.: manobras de apontamento).
    - Atualizar o estado interno da atitude e disponibilizar dados para telemetria.
    - Gerar alertas em caso de desvios significativos ou falhas no controlo.
- **Importância:**
    
    É um subsistema crítico para a missão, sendo necessário assegurar execução periódica e resposta consistente a comandos.
    

**2.2.4 TM_proc (Processo de Telemetria)**

- **Função principal:**
    
    Agregar, formatar e enviar os dados de telemetria coletados das várias tarefas para a Ground Station, permitindo monitorização em tempo real do satélite.
    
- **Responsabilidades específicas:**
    - Recolher dados periódicos do sistema e das tarefas (ex.: estado do ADCS, utilização de CPU, status do MAIN_SO).
    - Formatar os dados segundo protocolos definidos para transmissão (ex.: pacotes CCSDS simplificados).
    - Enviar os pacotes de telemetria via ligação TCP/IP para a Ground Station.
    - Gerir eventuais retransmissões em caso de falhas na comunicação.
- **Importância:**
    
    Facilita a observação contínua do estado do satélite, sendo essencial para diagnóstico, controlo e resposta rápida a situações anómalas.
    

### 2.3. **Comunicação interprocessos**

- Implementar filas (queues) ou buffers partilhados para troca de mensagens entre processos.
- Protocolo simplificado para comunicação TCP entre Satélite (FreeRTOS/QEMU) e Ground Station (dashboard).
    
    

**2.3.1 Comunicação Interna entre Processos no RTOS**

- **Mecanismos utilizados:**
    - **Filas (Queues):** Estruturas FIFO usadas para enviar mensagens ou dados entre tarefas, garantindo ordem e integridade na comunicação.
    - **Buffers partilhados:** Áreas de memória acessíveis por múltiplas tarefas, normalmente protegidas por mecanismos de exclusão mútua (mutexes ou semáforos) para evitar acessos concorrentes e inconsistências.
    - **Semáforos e mutexes:** Utilizados para sincronização entre tarefas, controlando o acesso a recursos partilhados e evitando deadlocks.
- **Funcionalidades:**
    - Permitir a passagem de comandos do TC_proc para o MAIN_SO e outras tarefas.
    - Transmitir estados, resultados e pedidos de ações entre MAIN_SO, ADCS_proc e TM_proc.
    - Garantir comunicação assíncrona e não bloqueante para manter a responsividade do sistema.
- **Benefícios:**
    - Modularidade e desacoplamento das tarefas.
    - Prevenção de interferências e condições de corrida.
    - Suporte a prioridades e sincronização temporal entre processos.

**2.3.2 Comunicação Externa entre Satélite e Ground Station**

- **Protocolo de Comunicação:**
    - Implementação de um protocolo simplificado baseado em TCP/IP, permitindo comunicação fiável e orientada à ligação entre a VM Satélite (FreeRTOS/QEMU) e a VM Ground Station.
    - Utilização de sockets TCP para envio de telemetria (TM_proc) e receção de comandos (TC_proc).
- **Características do protocolo simplificado:**
    - **Formato de mensagens:** Estruturado para incluir cabeçalhos com identificação de tipo, tamanho e checksum para integridade.
    - **Sincronização:** Mensagens assincronamente enviadas e recebidas, com confirmação simples para garantir entrega.
    - **Tratamento de erros:** Reenvio de mensagens em caso de falha na transmissão, detecção de perda ou corrupção de dados.
    - **Segurança (simulada):** Pode incluir verificações básicas de integridade e autenticidade, mesmo em ambiente isolado.
- **Funcionalidade:**
    - TM_proc envia periodicamente pacotes de telemetria para o dashboard na Ground Station.
    - TC_proc mantém conexão aberta para receber comandos e enviar confirmações à Ground Station.
    - Permite interação em tempo real para testes funcionais e monitorização.

**2.3.3 Considerações para Implementação**

- **Latência e desempenho:**
    - O protocolo TCP/IP garante fiabilidade, mas deve ser monitorizado para garantir que não introduz latências excessivas, especialmente para comandos críticos.
- **Escalabilidade e modularidade:**
    - A arquitetura de comunicação deve permitir fácil adição de novos processos e tipos de mensagens no futuro.
- **Simplicidade para simulação:**
    - O protocolo deve ser suficientemente simples para facilitar a depuração e testes no ambiente virtual, evitando complexidades desnecessárias.

---

## 3. Implementação e Desenvolvimento

### 3.1. **Desenvolver cada processo como task FreeRTOS**

- Criar stubs funcionais inicialmente (tarefas que enviam e recebem mensagens simuladas).
- Implementar simulação básica de funções (exemplo: TC_proc recebe comando, MAIN_SO processa, TM_proc envia dados).

### 3.2. **Simular ambiente limitado de recursos**

- Configurar QEMU para limitar memória e CPU (simular recursos restritos típicos de satélites).
- Monitorizar uso de recursos e ajustar cargas das tarefas.

### 3.3. **Implementar comunicação com Ground Station**

- Criar cliente TCP no FreeRTOS para enviar telemetria.
- Criar servidor TCP na Ground Station para receber dados e enviar comandos.

### 3.4. **Desenvolver dashboard básico na Ground Station**

- Interface web simples (ex: Flask + JavaScript) para visualização da telemetria recebida.
- Botões para enviar comandos simulados à VM Satélite.

---

## 4. Testes e Validação

### 4.1. **Testes funcionais**

- Verificar execução correta das tarefas e comunicação bidirecional.
- Testar envio e receção de comandos e dados.

**4.1.1 Verificação da Execução Correta das Tarefas**

- **Objetivo:**
    
    Confirmar que cada tarefa (MAIN_SO, TC_proc, ADCS_proc, TM_proc) é inicializada corretamente, executa a sua função conforme definido e responde adequadamente a eventos internos e externos.
    
- **Atividades:**
    - Monitorizar o ciclo de vida das tarefas, assegurando que são criadas, executadas periodicamente e terminam conforme o esperado.
    - Verificar a correta priorização e escalonamento das tarefas, garantindo que as tarefas críticas têm precedência conforme definido no design do RTOS.
    - Confirmar que as tarefas respondem aos eventos e comandos internos (exemplo: MAIN_SO despacha comandos recebidos ao ADCS_proc).
    - Avaliar o correto manuseamento dos mecanismos de comunicação interna (filas, semáforos) usados para sincronização e passagem de mensagens.
- **Ferramentas e métodos:**
    - Utilização de logs internos ou contadores de execução para monitorizar o estado das tarefas.
    - Análise de mensagens trocadas entre tarefas para validar a sequência correta de operações.

**4.1.2 Teste da Comunicação Bidirecional**

- **Objetivo:**
    
    Garantir que a comunicação entre o satélite simulado e a Ground Station funciona corretamente, permitindo o envio e receção de comandos e dados.
    
- **Atividades:**
    - Testar o envio de comandos da Ground Station para a VM Satélite via TC_proc, verificando a receção correta, interpretação e ação correspondente pelo RTOS.
    - Confirmar o envio periódico de dados de telemetria pelo TM_proc para a Ground Station, garantindo a integridade e atualidade da informação transmitida.
    - Validar que as respostas e confirmações (feedback) a comandos são transmitidas corretamente e recebidas pela Ground Station.
    - Simular situações normais e excecionais (exemplo: perda de pacotes, comandos inválidos) para verificar a robustez da comunicação.
- **Ferramentas e métodos:**
    - Uso do dashboard na Ground Station para monitorizar mensagens recebidas e enviar comandos de controlo.
    - Análise dos registos de comunicação para identificar falhas, atrasos ou erros.
    - Testes manuais e automatizados para simular vários cenários de uso.

**4.1.3 Critérios de Sucesso**

- Todas as tarefas devem iniciar e operar conforme especificado sem erros ou bloqueios.
- As mensagens entre processos internos e entre as VMs devem ser entregues corretamente e em tempo útil.
- A comunicação deve ser estável e tolerante a falhas simples, com feedback adequado para a Ground Station.
- O sistema deve apresentar comportamento previsível e consistente em todas as interações testadas.

### 4.2. **Testes de desempenho e carga**

- Medir latência na resposta a comandos críticos (MAIN_SO e TC_proc).
- Monitorizar utilização CPU e memória nas tarefas.

**4.2.1 Medição da Latência na Resposta a Comandos Críticos**

- **Objetivo:**
    
    Avaliar o tempo que o sistema demora a processar e executar comandos críticos enviados da Ground Station, em particular pelos processos MAIN_SO e TC_proc, que são responsáveis pelo controlo e gestão do satélite.
    
- **Metodologia:**
    - Enviar comandos de controlo específicos através do dashboard da Ground Station para o satélite simulado.
    - Registar o instante exato da receção do comando pelo TC_proc e o momento em que o MAIN_SO completa a ação correspondente.
    - Calcular a latência como o intervalo de tempo entre o envio do comando e a confirmação da sua execução.
    - Repetir o teste em múltiplas condições de carga para avaliar variações na latência.
- **Importância:**
    
    Garantir que a latência mantém-se dentro de limites definidos é crucial para operações temporizadas e seguras do satélite, permitindo respostas rápidas a eventos críticos.
    

**4.2.2 Monitorização da Utilização de CPU e Memória**

- **Objetivo:**
    
    Quantificar o uso dos recursos computacionais do sistema (CPU e memória) durante a execução dos processos do RTOS, de modo a verificar a eficiência e a adequação do sistema às restrições de hardware típicas de um satélite LEO.
    
- **Metodologia:**
    - Utilizar ferramentas internas do FreeRTOS ou do ambiente QEMU para recolher métricas de utilização de CPU e memória por cada tarefa.
    - Avaliar o consumo em condições normais e em cenários de carga máxima, por exemplo, durante picos de processamento de comandos ou envio intensivo de telemetria.
    - Identificar possíveis gargalos ou tarefas que consomem recursos de forma excessiva.
    - Avaliar o impacto de mecanismos de gestão de energia simulados na utilização de CPU.
- **Importância:**
    
    O controlo rigoroso do uso dos recursos é fundamental para evitar falhas por sobrecarga, garantir a longevidade da missão e otimizar o desempenho global do sistema.
    

### 4.3. **Testes de falhas e recuperação**

- Simular falhas (exemplo: bloqueio de uma tarefa, falha na comunicação).
- Implementar watchdog para reset de tarefas e testes de recuperação.
    
    

**4.3.1 Simulação de Falhas**

- **Objetivo:**
    
    Induzir deliberadamente falhas controladas para testar a capacidade do sistema em identificar e reagir a situações anómalas.
    
- **Tipos de falhas simuladas:**
    - **Bloqueio de tarefa:** Simular uma tarefa que deixa de responder (exemplo: TC_proc ou ADCS_proc entra em deadlock ou loop infinito).
    - **Falha na comunicação:** Introduzir perda, atraso ou corrupção de mensagens entre o satélite e a Ground Station.
    - **Sobrecarga de recursos:** Forçar situações onde a CPU ou memória atingem limites críticos, provocando degradação do sistema.
    - **Falhas de hardware simuladas:** Embora em ambiente virtual, simular erros que imitam falhas físicas (exemplo: perda temporária de dados de sensores simulados).
- **Métodos de simulação:**
    - Manipulação direta do código das tarefas para induzir estados inválidos ou atrasos.
    - Interrupção temporária da comunicação TCP/IP para testar tolerância a falhas de ligação.
    - Inserção de condições extremas nos parâmetros do sistema para provocar erros.

**4.3.2 Implementação e Teste do Watchdog**

- **Objetivo:**
    
    Garantir que o RTOS dispõe de um mecanismo automático que detecta falhas e inicia ações corretivas para restaurar a operação normal do sistema.
    
- **Funcionalidades do Watchdog:**
    - Monitorizar periodicamente a execução das tarefas críticas, verificando sinais de vida (heartbeats) ou contadores de atividade.
    - Detectar ausência de resposta ou estados de bloqueio.
    - Acionar reinicialização da tarefa falhada ou do sistema operativo, conforme a gravidade da falha.
    - Registar eventos de falha e recuperação para análise posterior.
- **Testes de validação:**
    - Confirmar que o watchdog deteta corretamente uma tarefa bloqueada e executa a recuperação.
    - Avaliar o tempo de recuperação e impacto na continuidade das operações.
    - Testar a capacidade do sistema de retomar o funcionamento normal após reinicialização parcial ou total.
    - Verificar que o mecanismo não provoca reinicializações indevidas em situações normais.
    

**4.3.3 Importância dos Testes de Falhas e Recuperação**

- **Robustez:** A capacidade de manter a operação contínua mesmo perante falhas aumenta a fiabilidade do sistema, essencial para missões espaciais onde a intervenção humana direta é limitada ou impossível.
- **Segurança:** Detetar e corrigir rapidamente estados anómalos evita consequências críticas para o satélite e para a missão.
- **Preparação para cenários reais:** Embora o ambiente seja virtual, a simulação rigorosa de falhas prepara o sistema para situações adversas reais, facilitando a adaptação futura a hardware físico.

### 4.4. **Simulação de condições adversas**

- Introduzir atrasos, perdas de pacotes ou falhas temporárias para testar robustez.
    
    

**4.4.1 Tipos de Condições Adversas a Simular**

- **Atrasos na comunicação:**
    - Introdução de latências variáveis na transmissão de dados entre o satélite simulado e a Ground Station.
    - Avaliar impacto no tempo de resposta a comandos e atualização da telemetria.
- **Perda de pacotes:**
    - Simular a não receção de mensagens ou pacotes de dados, devido a falhas na rede interna ou no protocolo de comunicação.
    - Verificar mecanismos de retransmissão, deteção de erros e recuperação de informação.
- **Falhas temporárias de comunicação:**
    - Interrupções momentâneas no canal TCP/IP, simulando perda de ligação temporária.
    - Analisar capacidade do sistema em retomar a comunicação automaticamente após a falha.
- **Oscilações e variações de carga:**
    - Introdução de picos inesperados na carga das tarefas (exemplo: aumento súbito de comandos ou telemetria).
    - Avaliar resposta do escalonador e estabilidade do sistema perante sobrecarga momentânea.
- **Condições anómalas de execução:**
    - Forçar variações imprevistas no comportamento das tarefas, como execuções mais longas ou respostas tardias.
    - Verificar o comportamento dos mecanismos de deteção de falhas e as respostas do sistema.

**4.4.2 Métodos para Implementação da Simulação**

- **Injeção controlada de latência:**
    - Introduzir atrasos programados nas rotinas de envio/receção de mensagens, usando temporizadores internos ou buffers.
- **Simulação de perda de pacotes:**
    - Ignorar ou descartar deliberadamente certas mensagens para simular falhas de transmissão.
- **Interrupção programada da ligação TCP/IP:**
    - Desativar e reativar a interface de rede ou fechar a conexão temporariamente para testar a robustez da reconexão.
- **Variedade e repetição dos testes:**
    - Executar as simulações em diferentes condições, durações e frequências para garantir uma análise abrangente.

**4.4.3 Importância e Benefícios**

- **Avaliação da robustez do RTOS:**
    - Garantir que o sistema não entra em estados inconsistentes ou falha em recuperar após perturbações.
- **Validação dos mecanismos de recuperação:**
    - Confirmar que as estratégias de retransmissão, timeout e watchdog são eficazes perante condições adversas.
- **Preparação para o ambiente real:**
    - Satélites LEO enfrentam interferências, variações ambientais e falhas transitórias; a simulação destes cenários permite antecipar e mitigar riscos.
- **Melhoria contínua:**
    - Identificação de pontos fracos no sistema que podem ser corrigidos para aumentar a fiabilidade.

---

## 5. Análise de Resultados e Relatório

### 5.1. **Coletar métricas (KPI’s e KSI’s)**

- Latência de resposta medida por timestamps.
- Utilização de CPU/memória via contadores ou logs do FreeRTOS/QEMU.
- Tempo de recuperação de falhas.
- Tempo de operação sem falhas.

**5.1.1 Indicadores de Desempenho (KPI’s)**

- **Latência de Resposta**
    - **Descrição:** Medida do intervalo temporal entre o envio de um comando pela Ground Station e a sua execução confirmada pelo RTOS no satélite simulado.
    - **Método de recolha:** Utilização de timestamps registados no envio e receção das mensagens, possibilitando cálculo preciso da latência.
    - **Importância:** Reflete a capacidade do sistema em responder rapidamente a comandos críticos, fundamental para controlo em tempo real.
- **Utilização de CPU e Memória**
    - **Descrição:** Percentagem de recursos computacionais consumidos pelas tarefas do RTOS durante a sua execução.
    - **Método de recolha:** Monitorização contínua via contadores internos do FreeRTOS e métricas fornecidas pelo QEMU que emula o hardware, incluindo memória alocada e tempo de CPU gasto por tarefa.
    - **Importância:** Avalia a eficiência do sistema na gestão dos recursos limitados típicos de satélites, identificando possíveis sobrecargas ou desperdício.

**5.1.2 Indicadores de Sucesso (KSI’s)**

- **Tempo de Recuperação de Falhas**
    - **Descrição:** Intervalo temporal necessário para o sistema identificar, reagir e restabelecer a operação normal após a ocorrência de uma falha (ex.: bloqueio de tarefa, perda de comunicação).
    - **Método de recolha:** Registo dos eventos de falha e do momento em que o sistema recupera a funcionalidade, medido através de logs e eventos do watchdog.
    - **Importância:** Mede a resiliência do RTOS, essencial para garantir continuidade da missão mesmo diante de incidentes.
- **Tempo de Operação Sem Falhas (Disponibilidade)**
    - **Descrição:** Percentagem do tempo total em que o sistema permanece operacional e sem falhas críticas.
    - **Método de recolha:** Análise dos logs de sistema para contabilizar períodos de funcionamento normal versus períodos de falhas ou reinicializações.
    - **Importância:** Reflete a fiabilidade geral do sistema, indicador chave para missões espaciais que exigem operação contínua e segura.

**5.1.3 Metodologia de Recolha e Análise**

- **Automatização da recolha de métricas:**
    
    Implementação de mecanismos de logging dentro do RTOS e do ambiente QEMU, que registam automaticamente eventos, uso de recursos e tempos de resposta.
    
- **Centralização dos dados:**
    
    Armazenamento das métricas num formato estruturado, possibilitando análise posterior, geração de gráficos e relatórios.
    
- **Validação periódica:**
    
    Realização de sessões regulares de testes para garantir consistência e fiabilidade dos dados recolhidos.
    
- **Interpretação contextual:**
    
    Análise dos resultados em função dos cenários testados (normal, carga elevada, falhas simuladas), para compreender o comportamento do sistema sob diversas condições.
    

### 5.2. **Documentar resultados**

- Apresentar tabelas e gráficos no dashboard ou num relatório separado.
- Interpretar resultados e apontar melhorias para o RTOS.
    
    

**5.2.1 Apresentação dos Resultados**

- **Tabelas Resumo**
    - Organizar os dados coletados em tabelas claras e estruturadas, incluindo métricas como latência média, utilização de CPU, memória consumida, tempo de recuperação de falhas e disponibilidade do sistema.
    - Agrupar os dados por tipo de teste ou cenário (ex.: operação normal, carga máxima, simulação de falhas) para facilitar a comparação.
    - Utilizar legendas e notas explicativas para clarificar unidades de medida, condições de teste e variáveis relevantes.
- **Gráficos e Visualizações**
    - Utilizar gráficos de linhas para representar a evolução temporal da latência, utilização de CPU ou memória.
    - Gráficos de barras ou histogramas podem ilustrar comparações entre diferentes cenários ou tarefas.
    - Diagramas de pizza ou gráficos de radar são úteis para apresentar a distribuição percentual de utilização de recursos ou a fiabilidade relativa das tarefas.
    - Incluir visualizações interativas no dashboard, se aplicável, para permitir exploração dinâmica dos dados durante demonstrações ou análises.
- **Localização dos Resultados**
    - Apresentar os resultados diretamente no dashboard da Ground Station para visualização em tempo real durante a simulação.
    - Preparar relatórios formais, separados do dashboard, para documentação académica, contendo análises detalhadas, conclusões e recomendações.

**5.2.2 Interpretação dos Resultados**

- **Análise crítica das métricas**
    - Comparar os valores obtidos com os requisitos definidos inicialmente, avaliando se o sistema cumpre os objetivos de desempenho e fiabilidade.
    - Identificar padrões ou anomalias, como picos inesperados de latência, utilização excessiva de recursos ou tempos de recuperação elevados.
    - Avaliar o impacto das condições adversas simuladas na estabilidade e resposta do sistema.
- **Apontar Melhorias para o RTOS**
    - Sugerir otimizações no escalonador, na gestão de tarefas ou nos mecanismos de comunicação para reduzir latência e melhorar eficiência.
    - Propor ajustes nos mecanismos de deteção e recuperação de falhas para aumentar a robustez.
    - Recomendar melhorias na arquitetura ou na configuração dos processos, baseadas nas observações dos testes.
    - Identificar potenciais extensões para incluir novos módulos ou funcionalidades que aumentem a capacidade do sistema.
- **Contextualização dos Resultados**
    - Relacionar os resultados com cenários reais de operação de satélites LEO, discutindo a relevância prática das observações.
    - Apontar limitações da simulação e impacto potencial no comportamento em hardware real.

---

## 6. Passos Fututos (opcional)

- Expandir processos (ex.: incluir BMS_proc, HK_proc).
- Simular hardware mais complexo (multicore, SoC).
- Implementar protocolos espaciais reais (SpaceWire, CCSDS).
- Validar integração com frameworks como cFS.

---