// Arquivo para exibir gráficos de telemetria
// /home/istec/projeto_final/GS/dashboard/static/js/graphs.js

// Configuração do Chart.js
Chart.defaults.color = '#fff';
Chart.defaults.borderColor = '#444';

// Cores para diferentes métricas
const COLORS = {
    power: '#ff9800',
    battery: '#2196f3',
    temperature: '#f44336',
    attitude: {
        roll: '#4caf50',
        pitch: '#9c27b0', 
        yaw: '#ff5722'
    }
};

// Armazenamento para gráficos
let charts = {};

// Variável para controlar o tipo de gráfico exibido no telemetryChart
let activeTelemetryChart = 'power';

// Formatar data para exibição
function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString();
}

// Inicializar gráficos quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    setupTelemetryButtons();
    
    // Atualizar gráficos a cada 10 segundos
    setInterval(() => {
        updateCharts();
    }, 10000);
});

// Inicializar todos os gráficos
function initCharts() {
    // Inicializar gráfico principal de telemetria
    initMainTelemetryChart();
    
    // Gráfico de temperatura
    initTemperatureChart();
    
    // Gráfico de bateria
    initBatteryChart();
    
    // Gráfico de atitude (orientação)
    initAttitudeChart();
    
    // Gráfico de consumo de energia
    initPowerConsumptionChart();
    
    // Primeira atualização de dados
    updateCharts();
}

// Inicializar o gráfico principal de telemetria
function initMainTelemetryChart() {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    charts.telemetry = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Consumo de Energia (W)',
                data: [],
                borderColor: COLORS.power,
                backgroundColor: 'rgba(255, 152, 0, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            animation: {
                duration: 500
            }
        }
    });
}

// Configurar os botões de telemetria
function setupTelemetryButtons() {
    const buttons = document.querySelectorAll('.card-header .btn-group button');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover classe active de todos os botões
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Adicionar classe active ao botão clicado
            this.classList.add('active');
            
            // Obter o tipo de gráfico a ser exibido
            const chartType = this.getAttribute('data-chart');
            activeTelemetryChart = chartType;
            
            // Atualizar o gráfico principal
            updateMainTelemetryChart(chartType);
        });
    });
}

// Inicializar gráfico de temperatura
function initTemperatureChart() {
    const ctx = document.getElementById('temperatureChart').getContext('2d');
    charts.temperature = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperatura (°C)',
                data: [],
                borderColor: COLORS.temperature,
                tension: 0.4,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Inicializar gráfico de bateria
function initBatteryChart() {
    const ctx = document.getElementById('batteryChart').getContext('2d');
    charts.battery = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Nível de Bateria (%)',
                data: [],
                borderColor: COLORS.battery,
                backgroundColor: 'rgba(33, 150, 243, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Inicializar gráfico de atitude
function initAttitudeChart() {
    const ctx = document.getElementById('attitudeChart').getContext('2d');
    charts.attitude = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Roll (°)',
                    data: [],
                    borderColor: COLORS.attitude.roll,
                    tension: 0.4,
                    fill: false
                },
                {
                    label: 'Pitch (°)',
                    data: [],
                    borderColor: COLORS.attitude.pitch,
                    tension: 0.4,
                    fill: false
                },
                {
                    label: 'Yaw (°)',
                    data: [],
                    borderColor: COLORS.attitude.yaw,
                    tension: 0.4,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Inicializar gráfico de consumo de energia
function initPowerConsumptionChart() {
    const ctx = document.getElementById('powerConsumptionChart').getContext('2d');
    charts.power = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Consumo (W)',
                data: [],
                borderColor: COLORS.power,
                backgroundColor: 'rgba(255, 152, 0, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Atualizar dados de todos os gráficos
function updateCharts() {
    // Temperatura
    fetch('/api/history/thermal/temperatures.json')
        .then(response => response.json())
        .then(data => {
            updateTemperatureChart(data);
            // Se o gráfico ativo for temperatura, também atualiza o gráfico principal
            if (activeTelemetryChart === 'temperature') {
                updateMainTelemetryChart('temperature', data);
            }
        });
    
    // Bateria
    fetch('/api/history/power/battery.json')
        .then(response => response.json())
        .then(data => {
            updateBatteryChart(data);
            // Se o gráfico ativo for bateria, também atualiza o gráfico principal
            if (activeTelemetryChart === 'battery') {
                updateMainTelemetryChart('battery', data);
            }
        });
        
    // Atitude
    fetch('/api/history/adcs/attitude.json')
        .then(response => response.json())
        .then(data => updateAttitudeChart(data));
        
    // Consumo de energia
    fetch('/api/history/power/consumption.json')
        .then(response => response.json())
        .then(data => {
            updatePowerConsumptionChart(data);
            // Se o gráfico ativo for power, também atualiza o gráfico principal
            if (activeTelemetryChart === 'power') {
                updateMainTelemetryChart('power', data);
            }
        });
}

// Atualizar o gráfico principal de telemetria baseado no tipo
function updateMainTelemetryChart(type, data) {
    if (!charts.telemetry || !data || !data.length) return;
    
    const labels = data.map(entry => formatTime(entry.timestamp));
    let values = [];
    let label = '';
    let color = '';
    let bgColor = '';
    
    switch (type) {
        case 'temperature':
            values = data.map(entry => entry.internal || entry.processor || 0);
            label = 'Temperatura (°C)';
            color = COLORS.temperature;
            bgColor = 'rgba(244, 67, 54, 0.2)';
            break;
        case 'power':
            values = data.map(entry => entry.total_watts || 0);
            label = 'Consumo de Energia (W)';
            color = COLORS.power;
            bgColor = 'rgba(255, 152, 0, 0.2)';
            break;
        case 'battery':
            values = data.map(entry => entry.level || 0);
            label = 'Nível de Bateria (%)';
            color = COLORS.battery;
            bgColor = 'rgba(33, 150, 243, 0.2)';
            break;
    }
    
    charts.telemetry.data.labels = labels;
    charts.telemetry.data.datasets[0].data = values;
    charts.telemetry.data.datasets[0].label = label;
    charts.telemetry.data.datasets[0].borderColor = color;
    charts.telemetry.data.datasets[0].backgroundColor = bgColor;
    
    charts.telemetry.update();
}

// Atualizar gráfico de temperatura
function updateTemperatureChart(data) {
    if (!data || !data.length || !charts.temperature) return;
    
    const labels = data.map(entry => formatTime(entry.timestamp));
    const temperatures = data.map(entry => entry.internal || entry.processor || 0);
    
    charts.temperature.data.labels = labels;
    charts.temperature.data.datasets[0].data = temperatures;
    charts.temperature.update();
    
    // Atualizar o valor de temperatura no painel de status
    if (data.length > 0) {
        const lastReading = data[data.length - 1];
        const temp = lastReading.internal || lastReading.processor || 0;
        document.getElementById('temp-value').textContent = `${temp.toFixed(1)}°C`;
    }
}

// Atualizar gráfico de bateria
function updateBatteryChart(data) {
    if (!data || !data.length || !charts.battery) return;
    
    const labels = data.map(entry => formatTime(entry.timestamp));
    const levels = data.map(entry => entry.level || 0);
    
    charts.battery.data.labels = labels;
    charts.battery.data.datasets[0].data = levels;
    charts.battery.update();
    
    // Atualizar o valor de bateria no painel de status
    if (data.length > 0) {
        const lastReading = data[data.length - 1];
        document.getElementById('battery-value').textContent = `${lastReading.level.toFixed(1)}%`;
    }
}

// Atualizar gráfico de atitude
function updateAttitudeChart(data) {
    if (!data || !data.length || !charts.attitude) return;
    
    const labels = data.map(entry => formatTime(entry.timestamp));
    const roll = data.map(entry => entry.roll || 0);
    const pitch = data.map(entry => entry.pitch || 0);
    const yaw = data.map(entry => entry.yaw || 0);
    
    charts.attitude.data.labels = labels;
    charts.attitude.data.datasets[0].data = roll;
    charts.attitude.data.datasets[1].data = pitch;
    charts.attitude.data.datasets[2].data = yaw;
    charts.attitude.update();
}

// Atualizar gráfico de consumo de energia
function updatePowerConsumptionChart(data) {
    if (!data || !data.length || !charts.power) return;
    
    const labels = data.map(entry => formatTime(entry.timestamp));
    const consumption = data.map(entry => entry.total_watts || 0);
    
    charts.power.data.labels = labels;
    charts.power.data.datasets[0].data = consumption;
    charts.power.update();
    
    // Atualizar os valores no painel de status
    if (data.length > 0) {
        const lastReading = data[data.length - 1];
        document.getElementById('power-value').textContent = `${lastReading.total_watts.toFixed(2)}W`;
    }
}

// Atualizar valores de status do sistema
function updateSystemStatus(data) {
    if (!data) return;
    
    // Atualizar latência e perda de pacotes quando dados estiverem disponíveis
    if (data.communication && data.communication.radio) {
        const radio = data.communication.radio;
        const latency = document.getElementById('latency-value');
        const packetLoss = document.getElementById('packet-loss');
        
        if (latency && radio.latency !== undefined) {
            latency.textContent = radio.latency.toFixed(2);
        }
        
        if (packetLoss && radio.packets_sent && radio.packets_received) {
            const loss = 100 - ((radio.packets_received / radio.packets_sent) * 100);
            packetLoss.textContent = loss.toFixed(1);
        }
    }
    
    // Atualizar modo ADCS quando disponível
    if (data.system && data.system.status && data.system.status.mode) {
        const adcsMode = document.getElementById('adcs-mode');
        if (adcsMode) {
            adcsMode.textContent = data.system.status.mode;
        }
    }
}
