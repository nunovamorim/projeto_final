// Initialize Socket.IO connection
const socket = io();

// A inicialização do gráfico foi movida para graphs.js
// Variáveis mantidas para compatibilidade com código existente
let telemetryChart = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Setup command form handler
    document.getElementById('command-form').addEventListener('submit', handleCommand);
});

// Socket event handlers
socket.on('connect', () => {
    updateConnectionStatus(true);
});

socket.on('disconnect', () => {
    updateConnectionStatus(false);
});

socket.on('telemetry_update', (data) => {
    // Não precisamos mais chamar updateTelemetryChart aqui, pois agora usamos o graphs.js para isso
    // mas podemos usar os dados para atualizar outros indicadores
    
    // Atualizar log de sistema
    appendToLog(`Telemetria recebida: ${new Date().toLocaleTimeString()}`);
    
    // Atualizar status do sistema com os novos dados
    if (window.updateSystemStatus && typeof window.updateSystemStatus === 'function') {
        window.updateSystemStatus(data);
    }
});

// UI update functions
function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connection-status');
    if (connected) {
        statusBadge.textContent = 'Connected';
        statusBadge.classList.replace('bg-danger', 'bg-success');
    } else {
        statusBadge.textContent = 'Disconnected';
        statusBadge.classList.replace('bg-success', 'bg-danger');
    }
}

// Esta função é mantida apenas para compatibilidade, não usada mais
function updateTelemetryChart(data) {
    console.log('Telemetria recebida:', data);
    // Os gráficos agora são atualizados pelo arquivo graphs.js
}

// Esta função foi movida para o arquivo graphs.js
function updateSystemStatus(data) {
    console.log('Atualizando status do sistema com dados:', data);
    // Esta implementação é apenas um stub, a real está no arquivo graphs.js
}


function handleCommand(event) {
    event.preventDefault();
    
    const commandType = document.getElementById('command-type').value;
    const commandParams = document.getElementById('command-params').value;

    socket.emit('send_command', {
        type: commandType,
        parameters: commandParams
    });
    
    appendToLog(`Comando ${commandType} enviado ao satélite`);
}

// Adicionar entradas ao log do sistema
function appendToLog(message) {
    const logDisplay = document.getElementById('log-display');
    if (!logDisplay) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `<span class="log-time">[${timestamp}]</span> ${message}`;
    
    logDisplay.appendChild(logEntry);
    logDisplay.scrollTop = logDisplay.scrollHeight;
    
    // Limitar a 100 mensagens para evitar sobrecarga de memória
    if (logDisplay.children.length > 100) {
        logDisplay.removeChild(logDisplay.children[0]);
    }
}

// Configurar o botão para limpar logs
document.addEventListener('DOMContentLoaded', function() {
    const clearLogBtn = document.getElementById('clear-log');
    if (clearLogBtn) {
        clearLogBtn.addEventListener('click', function() {
            const logDisplay = document.getElementById('log-display');
            if (logDisplay) {
                logDisplay.innerHTML = '';
                appendToLog('Log limpo');
            }
        });
    }
    
    // Adicionar mensagem inicial ao log
    appendToLog('Dashboard inicializado.');
    
    // Configurar handler para botão de injeção de falhas
    const injectFaultBtn = document.getElementById('inject-fault');
    if (injectFaultBtn) {
        injectFaultBtn.addEventListener('click', function() {
            const faultType = document.getElementById('fault-type').value;
            const faultDuration = document.getElementById('fault-duration').value;
            const faultProbability = document.getElementById('fault-probability').value;
            
            if (faultType !== 'NONE') {
                appendToLog(`Injetando falha: ${faultType} (duração: ${faultDuration}ms, probabilidade: ${faultProbability}%)`);
                socket.emit('inject_fault', {
                    type: faultType,
                    duration: parseInt(faultDuration),
                    probability: parseInt(faultProbability)
                });
            }
        });
    }
});
