# Relatório de Progresso - Simulação de Satélite

## Tarefas Concluídas

### Implementação do Núcleo do Satélite
- Implementação das quatro tarefas críticas do satélite (MAIN_SO, TC_proc, ADCS_proc, TM_proc)
- Definição de prioridades e tamanhos de stack adequados
- Comunicação entre tarefas via filas
- Mutex para proteção de dados partilhados
- Grupos de eventos para sincronização
- Monitorização de recursos e funcionalidades de debugging

### Sistema de Build
- Criação de scripts de build para a simulação
- Ambiente de build baseado em Docker (Dockerfile)
- Opções de build: Docker, direto e manual

### Documentação e Organização
- Criação de guia detalhado de build e execução
- Documentação da arquitetura e design do sistema
- Plano de comunicação com a ground station
- Organização da documentação em pasta `docs`
- Criação dos ficheiros `MINIMUM_REQUIREMENTS.md` e `STEP-BY-STEP.md` em português europeu
- Atualização e migração dos ficheiros de documentação para a pasta `docs`

### Interface Ground Station
- Design do protocolo de comunicação
- Cliente Python para a ground station
- Visualização de telemetria

## Avanços Recentes

1. **Verificação e Solução de Problemas**:
   - Correção de problemas de indentação no código da estação terrestre
   - Adaptação do sistema para utilizar o simulador Python em vez da implementação QEMU
   - Verificação bem-sucedida da comunicação entre satélite e estação terrestre
   - Visualização de dados de telemetria em tempo real

2. **Documentação Abrangente**:
   - Atualização completa do guia passo-a-passo com método simplificado e confiável
   - Revisão dos requisitos mínimos para focar no simulador Python
   - Adição de instruções detalhadas para resolução de problemas
   - Reorganização das opções de execução por ordem de confiabilidade

## Próximos Passos

1. Refinar a interface gráfica da estação terrestre
2. Adicionar mais funcionalidades ao simulador do satélite
3. Melhorar deteção e recuperação de erros
4. Implementar gráficos adicionais para visualização de dados
5. Testes de desempenho e otimização
6. Finalizar documentação e preparar materiais de formação

## Questões Técnicas Resolvidas
- ✅ Configuração do sistema de simulação do satélite
- ✅ Comunicação entre simulador e estação terrestre
- ✅ Visualização de dados de telemetria
- ✅ Documentação organizada e atualizada

## Questões Técnicas em Aberto
- Integração completa com QEMU (pendente, mas não crítico)
- Optimização de recursos (memória, prioridades)
- Expansão de funcionalidades do simulador

## Linha Temporal Revista
1. ✅ Finalização e debugging do sistema base
2. ✅ Implementação e teste da comunicação
3. ✅ Organização da documentação
4. Melhoria da robustez e recuperação (em progresso)
5. Testes de desempenho (pendente)
6. Entrega final (planeada para Julho 2025)
