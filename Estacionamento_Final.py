# ====== IMPORTAÇÕES ======
import cv2
import numpy as np
from dataclasses import dataclass
import threading
import sys

# ====== CLASSE: ParkingSpot (Uma vaga de estacionamento) ======
@dataclass
class ParkingSpot:
    id: int  # Número da vaga (1, 2, 3, 4)
    x: int  # Posição horizontal
    y: int  # Posição vertical
    width: int  # Largura
    height: int  # Altura
    is_occupied: bool = False  # Ocupada ou não
    threshold: int = 3000  # Sensibilidade

# ====== CLASSE: ParkingLotDetector (O sistema principal) ======
class ParkingLotDetector:
    
    def __init__(self, spots_list):
        # Converter coordenadas em objetos ParkingSpot
        self.spots = [
            ParkingSpot(i+1, x, y, w, h) 
            for i, (x, y, w, h) in enumerate(spots_list)
        ]
        
        # Configurações de processamento de imagem
        self.config = {
            'adaptive_size': 25,
            'adaptive_const': 16,
            'median_blur': 5,
            'base_threshold': 3000
        }
        
        self.cap = None  # Câmera
        self.frame_count = 0  # Contador de frames
        self.current_frame = None  # Frame atual
        self.paused = False  # Se está pausado
        self.display_mode = "normal"  # normal ou threshold
        self.calibration_mode = False  # Modo de calibração
        self.calibration_points = []  # Pontos marcados
        self.lock = threading.Lock()  # Trava para threads

    # ====== CONECTAR CÂMERA ======
    def detect_and_connect_camera(self):
        """Procura e conecta à câmera USB"""
        
        print("\n📹 Procurando câmeras disponíveis...\n")
        
        cameras = []  # Lista de câmeras encontradas
        
        # Testar câmeras de 0 a 9
        for i in range(10):
            cap = cv2.VideoCapture(i)
            
            if cap.isOpened():  # Se conseguiu abrir
                # Pegar informações da câmera
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
        
        # Se não encontrou câmera
        if not cameras:
            print("❌ Nenhuma câmera encontrada!")
            return False
        
        # Escolher câmera USB (última da lista)
        camera_choice = cameras[-1] if len(cameras) > 1 else cameras[0]
        
        print(f"\n🎯 Usando câmera {camera_choice['index']}")
        
        # Fechar câmeras não usadas
        for cam in cameras:
            if cam['index'] != camera_choice['index']:
                cam['cap'].release()
        
        # Configurar câmera escolhida
        self.cap = camera_choice['cap']
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        
        print("✅ Câmera configurada e pronta!\n")
        return True

    # ====== PROCESSAR FRAME ======
    def process_frame(self, frame):
        """Processar imagem e detectar vagas"""
        
        # Redimensionar se necessário
        if frame.shape[:2] != (720, 1280):
            frame = cv2.resize(frame, (1280, 720))
        
        # Converter para cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Threshold adaptativo (destacar carros)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 
            self.config['adaptive_size'], 
            self.config['adaptive_const']
        )
        
        # Suavizar imagem
        blurred = cv2.medianBlur(thresh, self.config['median_blur'])
        
        # Dilatar (expandir áreas brancas)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(blurred, kernel, iterations=2)
        
        # ====== ANALISAR CADA VAGA ======
        for spot in self.spots:
            # Recortar região da vaga
            roi = dilated[spot.y:spot.y+spot.height, spot.x:spot.x+spot.width]
            
            # Contar pixels brancos
            white_pixels = cv2.countNonZero(roi)
            
            # Pegar threshold
            threshold = spot.threshold if spot.threshold > 0 else self.config['base_threshold']
            
            # Determinar se está ocupada
            spot.is_occupied = white_pixels > threshold
        
        # ====== RETORNAR FRAME ======
        if self.display_mode == "threshold":
            # Modo threshold: mostrar processamento
            result = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)
        else:
            # Modo normal: desenhar retângulos
            result = self._draw(frame)
        
        # Se em calibração, desenhar pontos
        if self.calibration_mode:
            result = self._draw_calibration(result)
        
        return result

    # ====== DESENHAR RETÂNGULOS ======
    def _draw(self, frame):
        """Desenhar retângulos das vagas no vídeo"""
        
        for spot in self.spots:
            # Escolher cor: vermelho (ocupada) ou verde (livre)
            color = (0, 0, 255) if spot.is_occupied else (0, 255, 0)
            
            # Desenhar retângulo
            cv2.rectangle(frame, (spot.x, spot.y), 
                         (spot.x + spot.width, spot.y + spot.height), color, 3)
            
            # Texto: OCP (ocupada) ou LVR (livre)
            status = "OCP" if spot.is_occupied else "LVR"
            
            # Desenhar texto
            cv2.putText(frame, f"{spot.id}:{status}", (spot.x + 10, spot.y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame

    # ====== DESENHAR PONTOS DE CALIBRAÇÃO ======
    def _draw_calibration(self, frame):
        """Desenhar pontos marcados durante calibração"""
        
        # Desenhar cada ponto
        for i, (x, y) in enumerate(self.calibration_points):
            cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)  # Círculo preenchido
            cv2.circle(frame, (x, y), 10, (0, 255, 0), 2)  # Borda
        
        # Desenhar retângulos (pares de pontos)
        for i in range(0, len(self.calibration_points) - 1, 2):
            x1, y1 = self.calibration_points[i]
            x2, y2 = self.calibration_points[i+1]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        return frame

    # ====== ADICIONAR PONTO DE CALIBRAÇÃO ======
    def add_calibration_point(self, x, y):
        """Quando usuário clica, adicionar ponto"""
        
        self.calibration_points.append((x, y))
        print(f"✅ Ponto marcado: ({x}, {y})")
        
        # Se temos um par (2 pontos), mostrar qual vaga é
        if len(self.calibration_points) % 2 == 0:
            x1, y1 = self.calibration_points[-2]
            x2, y2 = self.calibration_points[-1]
            
            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)
            
            w = x_max - x_min
            h = y_max - y_min
            vaga_num = len(self.calibration_points) // 2
            
            print(f"✅ Vaga {vaga_num}: [{x_min}, {y_min}, {w}, {h}]")

    # ====== FINALIZAR CALIBRAÇÃO ======
    def finalize_calibration(self):
        """Converter pontos em coordenadas de vagas"""
        
        # Verificar se marcou os 8 pontos
        if len(self.calibration_points) < 8:
            print("❌ Você precisa marcar 4 vagas (8 pontos)")
            return False
        
        # Limpar vagas antigas
        self.spots = []
        
        # Criar novas vagas
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
        
        print("✅ Calibração finalizada!")
        self.calibration_mode = False
        self.calibration_points = []
        return True

    # ====== PEGAR STATUS ======
    def get_status(self):
        """Retornar informações do sistema"""
        
        free = sum(1 for s in self.spots if not s.is_occupied)
        occupied = len(self.spots) - free
        percent = round((occupied / len(self.spots) * 100), 1) if self.spots else 0
        
        return {
            'free': free,
            'occupied': occupied,
            'total': len(self.spots),
            'percent': percent,
            'frame': self.frame_count,
            'spots': [s.is_occupied for s in self.spots],
            'thresholds': {s.id: s.threshold for s in self.spots}
        }

    # ====== PAUSAR/RETOMAR ======
    def toggle_pause(self):
        """Pausar ou retomar vídeo"""
        self.paused = not self.paused

    # ====== TROCAR MODO ======
    def toggle_display_mode(self):
        """Trocar entre normal e threshold"""
        self.display_mode = "threshold" if self.display_mode == "normal" else "normal"
        print(f"✅ Modo: {self.display_mode.upper()}")

    # ====== RESETAR CONTADOR ======
    def reset(self):
        """Resetar contador de frames"""
        self.frame_count = 0

    # ====== MUDAR THRESHOLD DE VAGA ======
    def set_vaga_threshold(self, vaga_id, threshold):
        """Mudar sensibilidade de uma vaga"""
        
        for spot in self.spots:
            if spot.id == vaga_id:
                spot.threshold = threshold
                return True
        return False

    # ====== OBTER FRAME DA CÂMERA ======
    def get_frame(self):
        """Pegar frame da câmera e processar"""
        
        if self.paused and self.current_frame is not None:
            return self.current_frame  # Retornar frame pausado
        
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        self.current_frame = self.process_frame(frame)
        self.frame_count += 1
        return self.current_frame

    # ====== INICIAR CALIBRAÇÃO ======
    def start_calibration(self):
        """Ativar modo de calibração"""
        self.calibration_mode = True
        self.calibration_points = []
        print("\n🎯 MODO DE CALIBRAÇÃO INICIADO")
        print("Clique no vídeo para marcar 8 pontos (4 vagas)\n")

    # ====== CANCELAR CALIBRAÇÃO ======
    def cancel_calibration(self):
        """Cancelar calibração"""
        self.calibration_mode = False
        self.calibration_points = []


# ====== FUNÇÃO: LIDAR COM CLIQUES DO MOUSE ======
def mouse_callback(event, x, y, flags, param):
    """Função chamada quando usuário clica no vídeo"""
    
    detector = param  # Receber o detector como parâmetro
    
    # Se clicou com botão esquerdo
    if event == cv2.EVENT_LBUTTONDOWN:
        if detector.calibration_mode:
            # Em modo calibração, adicionar ponto
            detector.add_calibration_point(x, y)
        else:
            # Fora de calibração, mostrar coordenadas
            print(f"Clique em: ({x}, {y})")


# ====== COORDENADAS INICIAIS DAS 4 VAGAS ======
VAGAS_COORDS = [
    [100, 100, 150, 200],  # Vaga 1
    [300, 100, 150, 200],  # Vaga 2
    [500, 100, 150, 200],  # Vaga 3
    [700, 100, 150, 200],  # Vaga 4
]


# ====== FUNÇÃO PRINCIPAL ======
def main():
    """Função principal do programa"""
    
    print("\n" + "="*70)
    print("🅿️  ESTACIONAMENTO INTELIGENTE - VERSÃO OPENCV PURA")
    print("="*70)
    print("\nControles:")
    print("  P = Pausar/Retomar")
    print("  M = Trocar modo (Normal/Threshold)")
    print("  C = Iniciar Calibração")
    print("  F = Finalizar Calibração")
    print("  X = Cancelar Calibração")
    print("  +/- = Aumentar/Diminuir threshold da vaga selecionada")
    print("  1-4 = Selecionar vaga (1, 2, 3, 4)")
    print("  R = Resetar contador")
    print("  Q = Sair\n")
    
    # ====== CRIAR DETECTOR ======
    detector = ParkingLotDetector(VAGAS_COORDS)
    
    # ====== CONECTAR CÂMERA ======
    if not detector.detect_and_connect_camera():
        print("❌ Erro ao conectar câmera!")
        return
    
    # ====== CRIAR JANELA ======
    window_name = "Estacionamento Inteligente"
    cv2.namedWindow(window_name)
    
    # ====== DEFINIR CALLBACK DO MOUSE ======
    cv2.setMouseCallback(window_name, mouse_callback, detector)
    
    selected_vaga = 1  # Vaga selecionada
    
    # ====== LOOP PRINCIPAL ======
    print("🎥 Vídeo iniciado. Pressione as teclas conforme instruções.\n")
    
    while True:
        # ====== OBTER FRAME ======
        frame = detector.get_frame()
        
        if frame is None:
            print("❌ Erro ao obter frame")
            break
        
        # ====== INFORMAÇÕES NA TELA ======
        status = detector.get_status()
        
        # Adicionar textos informativos
        cv2.putText(frame, f"Livres: {status['free']}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Ocupadas: {status['occupied']}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.putText(frame, f"Ocupacao: {status['percent']}%", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        cv2.putText(frame, f"Frames: {status['frame']}", (10, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Mostrar modo
        mode_text = "NORMAL" if detector.display_mode == "normal" else "THRESHOLD"
        cv2.putText(frame, f"Modo: {mode_text}", (10, 190),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Mostrar vaga selecionada
        if not detector.calibration_mode:
            threshold = status['thresholds'][selected_vaga]
            cv2.putText(frame, f"Vaga {selected_vaga} selecionada | Threshold: {threshold}", 
                       (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(frame, f"CALIBRACAO: {len(detector.calibration_points)}/8 pontos", 
                       (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        
        # ====== MOSTRAR FRAME ======
        cv2.imshow(window_name, frame)
        
        # ====== CAPTURAR TECLA ======
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):  # Sair
            print("\n👋 Encerrando...")
            break
        
        elif key == ord('p'):  # Pausar/Retomar
            detector.toggle_pause()
            status_text = "PAUSADO" if detector.paused else "RODANDO"
            print(f"⏸️  {status_text}")
        
        elif key == ord('m'):  # Trocar modo
            detector.toggle_display_mode()
        
        elif key == ord('c'):  # Iniciar calibração
            detector.start_calibration()
        
        elif key == ord('f'):  # Finalizar calibração
            if detector.calibration_mode:
                detector.finalize_calibration()
        
        elif key == ord('x'):  # Cancelar calibração
            detector.cancel_calibration()
            print("❌ Calibração cancelada")
        
        elif key == ord('r'):  # Resetar
            detector.reset()
            print("🔄 Contador resetado")
        
        elif key == ord('+') or key == ord('='):  # Aumentar threshold
            new_threshold = status['thresholds'][selected_vaga] + 200
            detector.set_vaga_threshold(selected_vaga, new_threshold)
            print(f"⬆️  Vaga {selected_vaga} threshold: {new_threshold}")
        
        elif key == ord('-'):  # Diminuir threshold
            new_threshold = max(500, status['thresholds'][selected_vaga] - 200)
            detector.set_vaga_threshold(selected_vaga, new_threshold)
            print(f"⬇️  Vaga {selected_vaga} threshold: {new_threshold}")
        
        elif key >= ord('1') and key <= ord('4'):  # Selecionar vaga
            selected_vaga = int(chr(key))
            print(f"🎯 Vaga {selected_vaga} selecionada")
    
    # ====== ENCERRAR ======
    if detector.cap:
        detector.cap.release()
    cv2.destroyAllWindows()
    print("✅ Programa encerrado!")


# ====== EXECUTAR ======
if __name__ == '__main__':
    main()
