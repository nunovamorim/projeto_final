# Correções do Sistema de Comunicação Satellite-Ground Station

## Problemas Resolvidos
1. **Atualização de caminhos de usuário**: Todos os scripts foram atualizados para usar o usuário correto `groundstation` em vez de `istec` na VMGS (192.168.1.96).
2. **Correção de diretórios**: Os caminhos para logs foram atualizados de `/home/istec/projeto_final/GS/logs` para `/home/groundstation/projeto_final/GS/logs`.
3. **Dashboard atualizado**: O dashboard foi configurado para ler os logs do diretório correto.
4. **Scripts de utilitários melhorados**:
   - Adicionado script `verify_setup.sh` para verificar a configuração do sistema
   - Melhorado `fix_common_issues.sh` para corrigir automaticamente problemas comuns
   - Atualizado menu de opções no `start_satellite.sh`

## Testes Realizados
1. **Verificação de configuração**: Script `verify_setup.sh` executa 5 verificações essenciais:
   - Verificação de configuração de usuário em scripts
   - Verificação de conectividade com VMGS
   - Verificação de conexão SSH
   - Verificação de estrutura de diretórios
   - Teste de escrita de arquivo
   
2. **Teste de telemetria**: O script `generate_telemetry.py` foi testado e confirmado que está enviando dados corretamente para a VMGS.

## Arquivos Modificados
1. `/home/istec/projeto_final/satellite/process_qemu_output.py`
2. `/home/istec/projeto_final/satellite/generate_telemetry.py`
3. `/home/istec/projeto_final/satellite/cortex_qemu_satellite/run_qemu.sh`
4. `/home/istec/projeto_final/GS/dashboard/app.py`
5. `/home/istec/projeto_final/satellite/simulate_logs.py`
6. `/home/istec/projeto_final/satellite/diagnose_logs.py`
7. `/home/istec/projeto_final/satellite/fix_common_issues.sh`
8. `/home/istec/projeto_final/satellite/start_satellite.sh`
9. `/home/istec/projeto_final/satellite/README.md`

## Arquivos Adicionados
1. `/home/istec/projeto_final/satellite/verify_setup.sh`: Script para verificar se o sistema está configurado corretamente

## Como Usar o Sistema
1. Execute o script `start_satellite.sh` para abrir o menu principal
2. Escolha a opção 7 para verificar a configuração do sistema
3. Se tudo estiver correto, escolha a opção 1 para iniciar o simulador com QEMU, ou a opção 3 para usar apenas o gerador de telemetria simulada
4. Acesse o dashboard no navegador: http://192.168.1.96:8000

## Em Caso de Problemas
Se enfrentar algum problema, execute o script `fix_common_issues.sh` ou escolha a opção 4 do menu principal para corrigir automaticamente os problemas mais comuns.
