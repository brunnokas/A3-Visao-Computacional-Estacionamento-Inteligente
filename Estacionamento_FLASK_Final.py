from flask import Flask, Response, jsonify, render_template_string
import cv2
import numpy as np
from dataclasses import dataclass
import threading
import sys
import json

# ========== CLASSES ==========

@dataclass
class ParkingSpot:
    id: int
    x: int
    y: int
    width: int
    height: int
    is_occupied: bool = False
    threshold: int = 3000

class ParkingLotDetector:
    def __init__(self, spots_list):
        """
        spots_list: Lista de vagas [x, y, w, h]
        """
        self.spots = [
            ParkingSpot(i+1, x, y, w, h) 
            for i, (x, y, w, h) in enumerate(spots_list)
        ]
        self.config = {
            'adaptive_size': 25,
            'adaptive_const': 16,
            'median_blur': 5,
            'base_threshold': 3000
        }
        self.cap = None
        self.frame_count = 0
        self.current_frame = None
        self.paused = False
        self.lock = threading.Lock()
        self.camera_info = ""
        self.display_mode = "normal"  # normal ou threshold
        self.calibration_mode = False  # modo de calibração
        self.calibration_points = []  # pontos de calibração
        self.current_vaga_editing = 0  # qual vaga está sendo editada

    def detect_and_connect_camera(self):
        """Detecta e conecta à câmera USB (não à câmera frontal)"""
        print("\n📹 Procurando câmeras disponíveis...\n")
        
        cameras = []
        
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                cameras.append({
                    'index': i,
                    'width': frame_width,
                    'height': frame_height,
                    'fps': fps,
                    'cap': cap
                })
                
                print(f"✅ Câmera {i}: {frame_width}x{frame_height} @ {fps}fps")
        
        if not cameras:
            print("❌ Nenhuma câmera encontrada!")
            return False
        
        camera_choice = cameras[-1] if len(cameras) > 1 else cameras[0]
        
        print(f"\n🎯 Usando câmera {camera_choice['index']}: {camera_choice['width']}x{camera_choice['height']}")
        
        for cam in cameras:
            if cam['index'] != camera_choice['index']:
                cam['cap'].release()
        
        self.cap = camera_choice['cap']
        self.camera_info = f"Câmera {camera_choice['index']}"
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        
        print("✅ Câmera configurada e pronta!\n")
        return True

    def connect_camera_manual(self, camera_index):
        """Conecta manualmente a uma câmera específica"""
        print(f"\n📹 Conectando à câmera {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            print(f"❌ Câmera {camera_index} não encontrada!")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        
        self.camera_info = f"Câmera {camera_index}"
        print(f"✅ Câmera {camera_index} conectada!\n")
        return True

    def process_frame(self, frame):
        """Processa frame e detecta vagas"""
        if frame.shape[:2] != (720, 1280):
            frame = cv2.resize(frame, (1280, 720))
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 
            self.config['adaptive_size'], 
            self.config['adaptive_const']
        )
        blurred = cv2.medianBlur(thresh, self.config['median_blur'])
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(blurred, kernel, iterations=2)
        
        for spot in self.spots:
            roi = dilated[spot.y:spot.y+spot.height, spot.x:spot.x+spot.width]
            white_pixels = cv2.countNonZero(roi)
            threshold = spot.threshold if spot.threshold > 0 else self.config['base_threshold']
            spot.is_occupied = white_pixels > threshold
        
        # Modo normal ou threshold
        if self.display_mode == "threshold":
            result = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)
        else:
            result = self._draw(frame)
        
        # Se em modo calibração, desenhar pontos
        if self.calibration_mode:
            result = self._draw_calibration(result)
        
        return result

    def _draw(self, frame):
        """Desenha retângulos das vagas"""
        for spot in self.spots:
            color = (0, 0, 255) if spot.is_occupied else (0, 255, 0)
            cv2.rectangle(frame, (spot.x, spot.y), 
                         (spot.x + spot.width, spot.y + spot.height), color, 3)
            status = "OCP" if spot.is_occupied else "LVR"
            cv2.putText(frame, f"{spot.id}:{status}", (spot.x + 10, spot.y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        return frame
    
    def _draw_calibration(self, frame):
        """Desenha pontos de calibração"""
        # Desenhar todos os pontos já marcados
        for i, (x, y) in enumerate(self.calibration_points):
            cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
            cv2.circle(frame, (x, y), 10, (0, 255, 0), 2)
        
        # Se temos pares de pontos completos, desenhar retângulos
        for i in range(0, len(self.calibration_points) - 1, 2):
            x1, y1 = self.calibration_points[i]
            x2, y2 = self.calibration_points[i+1]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        return frame

    def add_calibration_point(self, x, y):
        """Adiciona ponto de calibração"""
        self.calibration_points.append((x, y))
        print(f"✅ Ponto marcado: ({x}, {y})")
        
        # Se temos 2 pontos, criar vaga
        if len(self.calibration_points) % 2 == 0:
            x1, y1 = self.calibration_points[-2]
            x2, y2 = self.calibration_points[-1]
            
            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)
            
            w = x_max - x_min
            h = y_max - y_min
            
            vaga_num = (len(self.calibration_points) // 2)
            print(f"✅ Vaga {vaga_num}: [{x_min}, {y_min}, {w}, {h}]")

    def finalize_calibration(self):
        """Finaliza calibração e atualiza vagas"""
        if len(self.calibration_points) < 8:
            print("❌ Você precisa marcar 4 vagas (8 pontos)")
            return False
        
        # Limpar e reconstruir spots
        self.spots = []
        
        for i in range(0, 8, 2):
            x1, y1 = self.calibration_points[i]
            x2, y2 = self.calibration_points[i+1]
            
            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)
            
            w = x_max - x_min
            h = y_max - y_min
            
            vaga_id = (i // 2) + 1
            self.spots.append(ParkingSpot(vaga_id, x_min, y_min, w, h))
        
        print("✅ Calibração finalizada com sucesso!")
        self.calibration_mode = False
        self.calibration_points = []
        return True

    def get_frame_bytes(self):
        """Retorna frame em bytes JPEG"""
        with self.lock:
            if self.paused and self.current_frame is not None:
                _, buffer = cv2.imencode('.jpg', self.current_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                return buffer.tobytes()
            
            if self.cap is None or not self.cap.isOpened():
                return None

            ret, frame = self.cap.read()
            if not ret:
                return None

            self.current_frame = self.process_frame(frame)
            self.frame_count += 1
            _, buffer = cv2.imencode('.jpg', self.current_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            return buffer.tobytes()

    def get_status(self):
        """Retorna status de todas as vagas"""
        with self.lock:
            free = sum(1 for s in self.spots if not s.is_occupied)
            occupied = len(self.spots) - free
            return {
                'free': free,
                'occupied': occupied,
                'total': len(self.spots),
                'percent': round((occupied / len(self.spots) * 100), 1) if self.spots else 0,
                'frame': self.frame_count,
                'spots': [s.is_occupied for s in self.spots],
                'paused': self.paused,
                'camera': self.camera_info,
                'thresholds': {s.id: s.threshold for s in self.spots},
                'display_mode': self.display_mode,
                'calibration_mode': self.calibration_mode,
                'calibration_points': len(self.calibration_points)
            }

    def toggle_pause(self):
        """Pausa/Retoma vídeo"""
        self.paused = not self.paused

    def toggle_display_mode(self):
        """Alterna entre modo normal e threshold"""
        self.display_mode = "threshold" if self.display_mode == "normal" else "normal"
        print(f"✅ Modo alterado para: {self.display_mode.upper()}")

    def reset(self):
        """Reseta contador de frames"""
        with self.lock:
            self.frame_count = 0
    
    def set_vaga_threshold(self, vaga_id, threshold):
        """Define threshold específico para uma vaga"""
        for spot in self.spots:
            if spot.id == vaga_id:
                spot.threshold = threshold
                return True
        return False

# ========== COORDENADAS DAS 4 VAGAS ==========

VAGAS_COORDS = [
    [1, 89, 108, 213],
    [289, 89, 138, 212],
    [591, 90, 132, 206],
    [881, 93, 138, 201],
]

# ========== INICIALIZAÇÃO ==========

print("\n" + "="*70)
print("🅿️  ESTACIONAMENTO INTELIGENTE - CALIBRADOR VISUAL")
print("="*70)

detector = ParkingLotDetector(VAGAS_COORDS)

if not detector.detect_and_connect_camera():
    print("\n⚠️  Nenhuma câmera automática encontrada!")
    if not detector.connect_camera_manual(0):
        print("\n❌ Erro: Nenhuma câmera disponível!")
        sys.exit(1)

# ========== FLASK APP ==========

app = Flask(__name__)

def video_stream():
    """Stream MJPEG contínuo"""
    last_frame = None
    while True:
        frame_bytes = detector.get_frame_bytes()
        if frame_bytes is None:
            frame_bytes = last_frame
        else:
            last_frame = frame_bytes
        
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                   + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video():
    """Endpoint de streaming de vídeo"""
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """Endpoint de status em tempo real"""
    return jsonify(detector.get_status())

@app.route('/pause', methods=['POST'])
def pause():
    """Endpoint para pausar/retomar"""
    detector.toggle_pause()
    return jsonify({'paused': detector.paused})

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    """Endpoint para alternar modo de câmera"""
    detector.toggle_display_mode()
    return jsonify({'display_mode': detector.display_mode})

@app.route('/start_calibration', methods=['POST'])
def start_calibration():
    """Inicia modo de calibração"""
    detector.calibration_mode = True
    detector.calibration_points = []
    print("\n🎯 MODO DE CALIBRAÇÃO INICIADO")
    print("Clique no vídeo para marcar os pontos das vagas (8 cliques total)")
    return jsonify({'success': True, 'message': 'Calibração iniciada'})

@app.route('/add_point/<int:x>/<int:y>', methods=['POST'])
def add_point(x, y):
    """Adiciona ponto de calibração"""
    if not detector.calibration_mode:
        return jsonify({'success': False, 'error': 'Modo de calibração não ativo'})
    
    detector.add_calibration_point(x, y)
    return jsonify({
        'success': True,
        'points': len(detector.calibration_points),
        'vaga': (len(detector.calibration_points) // 2)
    })

@app.route('/finalize_calibration', methods=['POST'])
def finalize_calibration():
    """Finaliza calibração"""
    success = detector.finalize_calibration()
    return jsonify({
        'success': success,
        'message': 'Calibração finalizada' if success else 'Erro na calibração'
    })

@app.route('/cancel_calibration', methods=['POST'])
def cancel_calibration():
    """Cancela calibração"""
    detector.calibration_mode = False
    detector.calibration_points = []
    return jsonify({'success': True, 'message': 'Calibração cancelada'})

@app.route('/reset', methods=['POST'])
def reset():
    """Endpoint para resetar contador"""
    detector.reset()
    return jsonify({'success': True})

@app.route('/set_threshold/<int:vaga_id>/<int:threshold>', methods=['POST'])
def set_threshold(vaga_id, threshold):
    """Endpoint para ajustar threshold de uma vaga"""
    if detector.set_vaga_threshold(vaga_id, threshold):
        return jsonify({'success': True, 'vaga': vaga_id, 'threshold': threshold})
    return jsonify({'success': False, 'error': 'Vaga não encontrada'})

@app.route('/')
def index():
    """Dashboard HTML com calibrador visual"""
    return '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🅿️ Estacionamento - Calibrador Visual</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #000;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        
        .sidebar {
            width: 100%;
            max-width: 280px;
            background: linear-gradient(180deg, #0d0d0d 0%, #1a1a1a 100%);
            color: white;
            padding: 15px;
            overflow-y: auto;
            border-right: 3px solid #0066CC;
        }
        
        .video-container {
            flex: 1;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }
        
        .video-wrapper {
            position: relative;
            width: 100%;
            height: 100%;
        }
        
        .video-container img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            cursor: crosshair;
        }
        
        .live-indicator {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #CC0000;
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .mode-indicator {
            position: absolute;
            bottom: 50px;
            right: 10px;
            background: #7030A0;
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
        }
        
        .mode-indicator.threshold {
            background: #CC6600;
        }
        
        .calibration-indicator {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: #FF6600;
            color: white;
            padding: 10px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .live-dot {
            width: 6px;
            height: 6px;
            background: white;
            border-radius: 50%;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 49%, 100% { opacity: 1; }
            50%, 99% { opacity: 0.3; }
        }
        
        .header {
            text-align: center;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #0066CC, #7030A0);
            padding: 12px;
            border-radius: 10px;
        }
        
        .logo { font-size: 35px; margin-bottom: 5px; }
        .title { font-size: 12px; font-weight: bold; }
        
        .mode-switch {
            display: flex;
            gap: 6px;
            margin: 12px 0;
            background: #1a1a1a;
            padding: 8px;
            border-radius: 8px;
            border: 1px solid #333;
        }
        
        .mode-btn {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 10px;
            font-weight: bold;
            background: #333;
            color: #888;
            transition: all 0.3s;
        }
        
        .mode-btn.active {
            background: #0066CC;
            color: white;
            box-shadow: 0 0 10px rgba(0, 102, 204, 0.5);
        }
        
        .mode-btn.threshold-active {
            background: #CC6600;
            color: white;
            box-shadow: 0 0 10px rgba(204, 102, 0, 0.5);
        }
        
        .btn {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            background: #0066CC;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 11px;
            transition: 0.2s;
        }
        
        .btn:hover { background: #005aa6; }
        .btn.danger { background: #CC0000; }
        .btn.danger:hover { background: #990000; }
        .btn.calibration { background: #FF6600; }
        .btn.calibration:hover { background: #DD5500; }
        
        .metric-row {
            background: #2a2a2a;
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid #0066CC;
            font-size: 12px;
        }
        
        .metric-label { color: #888; text-transform: uppercase; font-size: 9px; }
        .metric-value { font-size: 18px; font-weight: bold; margin-top: 3px; }
        
        .section-title {
            font-size: 11px;
            color: #0066CC;
            font-weight: bold;
            margin-top: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .spots-mini {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 6px;
            margin: 10px 0;
        }
        
        .spot-mini {
            aspect-ratio: 1;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }
        
        .spot-mini-free { background: linear-gradient(135deg, #00CC55, #00AA44); }
        .spot-mini-occ { background: linear-gradient(135deg, #FF5555, #CC0000); }
        
        .vaga-control {
            background: #1a1a1a;
            padding: 10px;
            margin: 8px 0;
            border-radius: 6px;
            border: 1px solid #333;
        }
        
        .vaga-control-label {
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
        }
        
        .slider-group {
            display: flex;
            gap: 5px;
            align-items: center;
        }
        
        .slider-group input[type="range"] {
            flex: 1;
            height: 4px;
            border-radius: 2px;
            background: #333;
            outline: none;
            -webkit-appearance: none;
        }
        
        .slider-group input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #0066CC;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,102,204,0.5);
        }
        
        .threshold-value {
            font-size: 10px;
            font-weight: bold;
            min-width: 35px;
            text-align: right;
            color: #0066CC;
        }
        
        .info-footer {
            font-size: 9px;
            color: #666;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #333;
        }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #1a1a1a; }
        ::-webkit-scrollbar-thumb { background: #0066CC; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="header">
            <div class="logo">🅿️</div>
            <div class="title">CALIBRADOR VISUAL</div>
        </div>
        
        <div class="mode-switch">
            <button class="mode-btn active" id="normal-btn" onclick="switchMode('normal')">📷 Normal</button>
            <button class="mode-btn" id="threshold-btn" onclick="switchMode('threshold')">🔍 Threshold</button>
        </div>
        
        <button class="btn calibration" onclick="startCalibration()" id="calib-btn">
            🎯 Calibrar Vagas
        </button>
        
        <div id="calibration-controls" style="display: none;">
            <div style="background: #FF6600; padding: 8px; border-radius: 6px; margin: 10px 0; font-size: 10px; text-align: center; font-weight: bold;">
                Clique no vídeo para marcar 8 pontos
            </div>
            <div style="background: #1a1a1a; padding: 10px; border-radius: 6px; margin: 10px 0; font-size: 11px;">
                <div>Pontos marcados: <span id="cal-points" style="color: #FF6600; font-weight: bold;">0/8</span></div>
            </div>
            <button class="btn" onclick="finalizCalibration()" style="background: #00AA44;">✅ Finalizar</button>
            <button class="btn danger" onclick="cancelCalibration()">❌ Cancelar</button>
        </div>
        
        <div id="normal-controls">
            <div class="metric-row occupied">
                <div class="metric-label">Ocupadas</div>
                <div class="metric-value" id="occupied">0</div>
            </div>
            
            <div class="metric-row free">
                <div class="metric-label">Disponíveis</div>
                <div class="metric-value" id="free">0</div>
            </div>
            
            <div style="margin: 10px 0;">
                <div class="section-title">🎯 Status das Vagas</div>
                <div class="spots-mini" id="spots"></div>
            </div>
            
            <div style="display: flex; gap: 8px;">
                <button class="btn" id="pauseBtn" onclick="togglePause()" style="flex: 1;">⏸️ Pausar</button>
                <button class="btn danger" onclick="resetCounter()" style="flex: 1;">🔄 Reset</button>
            </div>
            
            <div class="section-title">⚙️ Ajuste Threshold</div>
            <div id="vaga-controls"></div>
        </div>
        
        <div class="info-footer">
            <div id="camera-info">📹 Câmera: Detectando...</div>
            <div style="margin-top: 5px;">📊 Frames: <span id="frame" style="color: #0066CC; font-weight: bold;">0</span></div>
            <div style="margin-top: 5px;">Status: <span id="status" style="color: #00AA44;">▶️ AO VIVO</span></div>
        </div>
    </div>
    
    <div class="video-container">
        <div class="video-wrapper">
            <div class="live-indicator">
                <div class="live-dot"></div>
                CÂMERA
            </div>
            <div class="mode-indicator" id="mode-indicator">📷 NORMAL</div>
            <div class="calibration-indicator" id="calib-indicator" style="display: none;">
                🎯 CALIBRAÇÃO: <span id="calib-counter">0</span>/8
            </div>
            <img id="video-stream" src="/video_feed" alt="Stream Câmera" onclick="handleVideoClick(event)">
        </div>
    </div>

    <script>
        let isCalibrating = false;
        
        function handleVideoClick(event) {
            if (!isCalibrating) return;
            
            const img = event.target;
            const rect = img.getBoundingClientRect();
            
            // Calcular posição relativa à imagem
            const x = Math.round((event.clientX - rect.left) * (img.naturalWidth || 1280) / rect.width);
            const y = Math.round((event.clientY - rect.top) * (img.naturalHeight || 720) / rect.height);
            
            fetch(`/add_point/${x}/${y}`, {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    document.getElementById('cal-points').innerText = d.points + '/8';
                    console.log(`Ponto ${d.points}: Vaga ${d.vaga}`);
                });
        }
        
        function startCalibration() {
            fetch('/start_calibration', {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    isCalibrating = true;
                    document.getElementById('calibration-controls').style.display = 'block';
                    document.getElementById('normal-controls').style.display = 'none';
                    document.getElementById('calib-indicator').style.display = 'block';
                    document.getElementById('calib-btn').disabled = true;
                });
        }
        
        function finalizCalibration() {
            fetch('/finalize_calibration', {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    if (d.success) {
                        alert('✅ Calibração finalizada com sucesso!');
                        cancelCalibration();
                        updateStatus();
                    } else {
                        alert('❌ Erro na calibração');
                    }
                });
        }
        
        function cancelCalibration() {
            fetch('/cancel_calibration', {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    isCalibrating = false;
                    document.getElementById('calibration-controls').style.display = 'none';
                    document.getElementById('normal-controls').style.display = 'block';
                    document.getElementById('calib-indicator').style.display = 'none';
                    document.getElementById('calib-btn').disabled = false;
                    document.getElementById('cal-points').innerText = '0/8';
                });
        }
        
        function updateStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('occupied').innerText = data.occupied;
                    document.getElementById('free').innerText = data.free;
                    document.getElementById('frame').innerText = data.frame;
                    document.getElementById('camera-info').innerText = '📹 ' + data.camera;
                    
                    if (data.calibration_mode) {
                        document.getElementById('calib-counter').innerText = data.calibration_points;
                    }
                    
                    const indicator = document.getElementById('mode-indicator');
                    if (data.display_mode === 'threshold') {
                        indicator.innerText = '🔍 THRESHOLD';
                        indicator.className = 'mode-indicator threshold';
                    } else {
                        indicator.innerText = '📷 NORMAL';
                        indicator.className = 'mode-indicator';
                    }
                    
                    let spotsHtml = '';
                    for (let i = 0; i < data.spots.length; i++) {
                        const cls = data.spots[i] ? 'spot-mini-occ' : 'spot-mini-free';
                        spotsHtml += `<div class="spot-mini ${cls}">${i+1}</div>`;
                    }
                    document.getElementById('spots').innerHTML = spotsHtml;
                    
                    for (let i = 0; i < data.spots.length; i++) {
                        const vagaId = i + 1;
                        const threshold = data.thresholds[vagaId];
                        const valueEl = document.getElementById(`threshold-${vagaId}`);
                        if (valueEl) valueEl.innerText = threshold;
                    }
                })
                .catch(e => console.error('Erro:', e));
        }
        
        function switchMode(mode) {
            fetch('/toggle_mode', {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    const normalBtn = document.getElementById('normal-btn');
                    const thresholdBtn = document.getElementById('threshold-btn');
                    
                    if (d.display_mode === 'normal') {
                        normalBtn.className = 'mode-btn active';
                        thresholdBtn.className = 'mode-btn';
                    } else {
                        normalBtn.className = 'mode-btn';
                        thresholdBtn.className = 'mode-btn threshold-active';
                    }
                });
        }
        
        function togglePause() {
            fetch('/pause', {method: 'POST'})
                .then(r => r.json())
                .then(d => updateStatus());
        }
        
        function resetCounter() {
            if (confirm('Resetar contador?')) {
                fetch('/reset', {method: 'POST'})
                    .then(r => r.json())
                    .then(d => updateStatus());
            }
        }
        
        function setThreshold(vagaId, value) {
            fetch(`/set_threshold/${vagaId}/${value}`, {method: 'POST'});
        }
        
        function initializeControls() {
            const container = document.getElementById('vaga-controls');
            container.innerHTML = '';
            
            for (let i = 1; i <= 4; i++) {
                const controlHtml = `
                    <div class="vaga-control">
                        <div class="vaga-control-label">
                            <span>Vaga ${i}</span>
                        </div>
                        <div class="slider-group">
                            <input type="range" min="1000" max="8000" step="100" 
                                   value="3000" 
                                   onchange="setThreshold(${i}, this.value)"
                                   onmousemove="setThreshold(${i}, this.value)">
                            <span class="threshold-value" id="threshold-${i}">3000</span>
                        </div>
                    </div>
                `;
                container.innerHTML += controlHtml;
            }
        }
        
        initializeControls();
        setInterval(updateStatus, 300);
        updateStatus();
    </script>
</body>
</html>
    '''

# ========== INICIAR ==========

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📊 ESTACIONAMENTO INTELIGENTE - CALIBRADOR VISUAL")
    print("="*70)
    print(f"\n✅ Modo Calibração: Clique no vídeo para marcar as vagas")
    print(f"✅ Total de vagas: 4 (8 pontos de clique)")
    print(f"\n🌐 Abra em: http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
