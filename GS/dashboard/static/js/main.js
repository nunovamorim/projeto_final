// Initialize Socket.IO connection
const socket = io();

// Chart configuration
let telemetryChart;
const chartConfig = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperature',
            data: [],
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1
        }, {
            label: 'Power',
            data: [],
            borderColor: 'rgb(54, 162, 235)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
};

// Initialize chart when document is ready
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    telemetryChart = new Chart(ctx, chartConfig);

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
    updateTelemetryChart(data);
    updateSystemStatus(data);
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

function updateTelemetryChart(data) {
    const timestamp = new Date().toLocaleTimeString();
    
    // Update chart data
    telemetryChart.data.labels.push(timestamp);
    telemetryChart.data.datasets[0].data.push(data.temperature);
    telemetryChart.data.datasets[1].data.push(data.power);

    // Keep last 20 data points
    if (telemetryChart.data.labels.length > 20) {
        telemetryChart.data.labels.shift();
        telemetryChart.data.datasets.forEach(dataset => dataset.data.shift());
    }

    telemetryChart.update();
}

function updateSystemStatus(data) {
    const statusDisplay = document.getElementById('status-display');
    statusDisplay.innerHTML = `
        <div class="col-md-3">
            <h5>Temperature</h5>
            <p>${data.temperature}°C</p>
        </div>
        <div class="col-md-3">
            <h5>Power</h5>
            <p>${data.power}W</p>
        </div>
        <div class="col-md-3">
            <h5>ADCS Status</h5>
            <p>${data.adcs_status}</p>
        </div>
        <div class="col-md-3">
            <h5>Battery</h5>
            <p>${data.battery_level}%</p>
        </div>
    `;
}

function handleCommand(event) {
    event.preventDefault();
    
    const commandType = document.getElementById('command-type').value;
    const commandParams = document.getElementById('command-params').value;

    socket.emit('send_command', {
        type: commandType,
        parameters: commandParams
    });
}
