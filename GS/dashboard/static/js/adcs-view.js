// Inicialização do Three.js para visualização 3D do ADCS
let scene, camera, renderer, satellite;
let isAnimating = false;
let targetRotation = { x: 0, y: 0, z: 0 };
let currentRotation = { x: 0, y: 0, z: 0 };

function initADCS() {
    // Criar cena
    scene = new THREE.Scene();
    
    // Configurar câmera
    camera = new THREE.PerspectiveCamera(75, 400/300, 0.1, 1000);
    camera.position.z = 5;
    
    // Criar renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(400, 300);
    renderer.setClearColor(0x000000, 1);
    
    // Adicionar ao DOM
    document.getElementById('adcs-3d-view').appendChild(renderer.domElement);
    
    // Criar modelo do satélite
    const geometry = new THREE.BoxGeometry(2, 1, 1);
    const material = new THREE.MeshPhongMaterial({
        color: 0x666666,
        shininess: 100
    });
    
    satellite = new THREE.Mesh(geometry, material);
    scene.add(satellite);
    
    // Adicionar painéis solares
    const panelGeometry = new THREE.PlaneGeometry(1, 2);
    const panelMaterial = new THREE.MeshPhongMaterial({
        color: 0x0066ff,
        shininess: 100,
        side: THREE.DoubleSide
    });
    
    const leftPanel = new THREE.Mesh(panelGeometry, panelMaterial);
    leftPanel.position.x = -1.5;
    satellite.add(leftPanel);
    
    const rightPanel = new THREE.Mesh(panelGeometry, panelMaterial);
    rightPanel.position.x = 1.5;
    satellite.add(rightPanel);
    
    // Adicionar iluminação
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5, 5, 5);
    scene.add(light);
    
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    
    // Iniciar animação
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    
    if (isAnimating) {
        // Interpolar suavemente para a rotação alvo
        currentRotation.x += (targetRotation.x - currentRotation.x) * 0.1;
        currentRotation.y += (targetRotation.y - currentRotation.y) * 0.1;
        currentRotation.z += (targetRotation.z - currentRotation.z) * 0.1;
        
        satellite.rotation.x = currentRotation.x;
        satellite.rotation.y = currentRotation.y;
        satellite.rotation.z = currentRotation.z;
    }
    
    renderer.render(scene, camera);
}

function updateSatelliteAttitude(roll, pitch, yaw) {
    targetRotation.x = THREE.MathUtils.degToRad(pitch);
    targetRotation.y = THREE.MathUtils.degToRad(yaw);
    targetRotation.z = THREE.MathUtils.degToRad(roll);
    
    if (!isAnimating) {
        isAnimating = true;
    }
}

// Inicializar quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', initADCS);
