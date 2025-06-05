#!/usr/bin/env python3
# Diagnóstico para debug de logs
# /home/istec/projeto_final/satellite/diagnose_logs.py

import subprocess
import os
import sys
import json

# Configurações
GS_IP = "192.168.1.96"
GS_USER = "groundstation"
GS_LOGS_DIR = "/home/groundstation/projeto_final/GS/logs"
LOCAL_LOGS_DIR = "/tmp/sat_logs"

def run_cmd(cmd, desc):
    """Executa um comando e exibe o resultado"""
    print(f"\n=== {desc} ===")
    print(f"Comando: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Código de saída:", result.returncode)
        
        stdout = result.stdout.decode("utf-8").strip()
        stderr = result.stderr.decode("utf-8").strip()
        
        if stdout:
            print("STDOUT:")
            print(stdout[:1000] + ("..." if len(stdout) > 1000 else ""))
        
        if stderr:
            print("STDERR:")
            print(stderr[:1000] + ("..." if len(stderr) > 1000 else ""))
            
        return result.returncode == 0, stdout, stderr
    except Exception as e:
        print(f"Erro ao executar comando: {e}")
        return False, "", str(e)

def check_network():
    """Verifica a conectividade com a VMGS"""
    print("\n===== VERIFICANDO CONECTIVIDADE DE REDE =====")
    
    # Ping para GS
    run_cmd(f"ping -c 4 {GS_IP}", "Ping para VMGS")
    
    # Verificar rota
    run_cmd("ip route", "Tabela de rotas")
    
    # Verificar interfaces de rede
    run_cmd("ip addr show", "Interfaces de rede")

def check_ssh():
    """Verifica a conexão SSH com a VMGS"""
    print("\n===== VERIFICANDO CONEXÃO SSH =====")
    
    # Teste de conexão SSH básica
    success, _, _ = run_cmd(f"ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} echo 'Teste de conexão SSH'", 
                          "Teste de conexão SSH básica")
    
    if not success:
        print("\n⚠️ ERRO: Falha na conexão SSH. Verifique:")
        print("1. Se a VMGS está ligada e acessível")
        print("2. Se o usuário e IP estão corretos")
        print("3. Se as chaves SSH estão configuradas corretamente")
        print("\nTente executar: ./setup_ssh_force.sh")

def check_logs_dir():
    """Verifica se os diretórios de logs existem"""
    print("\n===== VERIFICANDO DIRETÓRIOS DE LOGS =====")
    
    # Verificar diretório de logs na VMGS
    cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} "ls -la {GS_LOGS_DIR}"'
    success, stdout, _ = run_cmd(cmd, "Listando diretório de logs na VMGS")
    
    if not success:
        print("\n⚠️ ERRO: O diretório de logs não existe ou não é acessível na VMGS")
        print(f"Criando diretório de logs: {GS_LOGS_DIR}")
        
        # Tentar criar o diretório
        create_cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} "mkdir -p {GS_LOGS_DIR}/adcs {GS_LOGS_DIR}/power {GS_LOGS_DIR}/thermal {GS_LOGS_DIR}/communication {GS_LOGS_DIR}/system && chmod -R 755 {GS_LOGS_DIR}"'
        run_cmd(create_cmd, "Criando diretórios de logs")
    else:
        print("✅ Diretório de logs existe na VMGS")
        
        # Verificar subdiretorios
        for subdir in ['adcs', 'power', 'thermal', 'communication', 'system']:
            cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} "if [ -d {GS_LOGS_DIR}/{subdir} ]; then echo exists; else echo missing; fi"'
            _, stdout, _ = run_cmd(cmd, f"Verificando subdiretório {subdir}")
            
            if "exists" not in stdout:
                create_subdir = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} "mkdir -p {GS_LOGS_DIR}/{subdir} && chmod 755 {GS_LOGS_DIR}/{subdir}"'
                run_cmd(create_subdir, f"Criando subdiretório {subdir}")

def test_write_log():
    """Testa a escrita de um log de teste"""
    print("\n===== TESTANDO ESCRITA DE LOGS =====")
    
    # Criar um log de teste
    test_data = {
        "timestamp": "2025-06-05T12:00:00",
        "test_value": 42,
        "test_message": "Diagnóstico de logs"
    }
    
    test_log_json = json.dumps([test_data]).replace('"', '\\"')
    
    # Tentar escrever diretamente o log
    cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} "echo \'{test_log_json}\' > {GS_LOGS_DIR}/system/test.json"'
    success, _, _ = run_cmd(cmd, "Escrevendo arquivo de log de teste")
    
    if not success:
        print("\n⚠️ ERRO: Falha ao escrever arquivo de log de teste")
        # Verificar permissões
        run_cmd(f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} "ls -la {GS_LOGS_DIR}"', 
                "Verificando permissões")
    else:
        print("✅ Arquivo de log de teste criado com sucesso")
        
        # Verificar se o arquivo foi criado
        verify_cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {GS_USER}@{GS_IP} "cat {GS_LOGS_DIR}/system/test.json"'
        run_cmd(verify_cmd, "Verificando conteúdo do arquivo de log")

def check_dashboard_logs():
    """Verifica se o dashboard está configurado para o caminho de logs correto"""
    print("\n===== VERIFICANDO CONFIGURAÇÃO DO DASHBOARD =====")
    
    dashboard_path = "/home/groundstation/projeto_final/GS/dashboard/app.py"
    
    try:
        with open(dashboard_path, 'r') as f:
            content = f.read()
            
        if "/home/groundstation/projeto_final/GS/logs" in content:
            print("⚠️ AVISO: O dashboard está configurado para ler logs em /home/groundstation/projeto_final/GS/logs")
            
            # Verificar se estamos executando na mesma VM
            if os.path.exists("/home/groundstation"):
                print("✅ Diretório /home/groundstation existe nesta VM")
            else:
                print("⚠️ AVISO: O diretório /home/groundstation não existe nesta VM.")
                print("   Se o dashboard está executando na mesma VM que este diagnóstico,")
                print("   você precisa atualizar o caminho dos logs no arquivo app.py.")
                
    except Exception as e:
        print(f"Erro ao verificar configuração do dashboard: {e}")

def main():
    print("===============================================")
    print("DIAGNÓSTICO DE LOGS DO SISTEMA SATÉLITE-GROUND STATION")
    print("===============================================")
    
    check_network()
    check_ssh()
    check_logs_dir()
    test_write_log()
    check_dashboard_logs()
    
    print("\n===============================================")
    print("RESUMO DE AÇÕES RECOMENDADAS:")
    print("===============================================")
    print("1. Execute ./setup_ssh_force.sh na VMSAT para atualizar as chaves SSH")
    print("2. Verifique se o usuário 'groundstation' existe na VMGS")
    print("3. Confirme se o caminho /home/groundstation/projeto_final/GS/logs está correto na VMGS")
    print("4. Verifique se app.py do dashboard usa o caminho de logs correto")

if __name__ == "__main__":
    main()
