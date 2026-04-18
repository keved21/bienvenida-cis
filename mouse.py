import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import math
import threading
import time

class VideoCaptureThread:
    def __init__(self, src=0, width=640, height=480):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # Bajar resolucion de la cámara elimina drásticamente el LAG
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self
 
    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy() if self.ret else None

    def stop(self):
        self.stopped = True
        self.cap.release()

class HandMouse:
    def __init__(self):
        # Configurar MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Eliminar cualquier Lag interno de PyAutoGUI
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False

        # Suavizado de movimiento (anti-temblor)
        self.smoothening = 5
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        
        # Variables de estado
        self.is_dragging = False
        self.scroll_y = 0
        self.last_click_time = 0
        
        # Cuadro virtual de captura REDUCIDO para llegar facil a TODOS los bordes
        self.frame_r = 100 

    def run(self):
        # Hilo separado para no laguear la deteccion
        cap = VideoCaptureThread().start()

        while True:
            success, img = cap.read()
            if not success or img is None:
                continue
            
            # Modo espejo para que sea intuitivo
            img = cv2.flip(img, 1) 
            h, w, c = img.shape
            
            # ---------------- COLOR Y DISEÑO UI ----------------
            # Dibujar el cuadro virtual donde se mueve el mouse
            cv2.rectangle(img, (self.frame_r, self.frame_r), (w - self.frame_r, h - self.frame_r), (255, 105, 180), 3)
            
            # Barra superior con titulo
            cv2.rectangle(img, (0, 0), (w, 60), (30, 30, 30), cv2.FILLED)
            cv2.putText(img, "MOUSE VIRTUAL - ABSOLUTO", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(img, "[Q] Salir", (w - 120, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Extraer puntos clave de la mano
                    lm_list = []
                    for id, lm in enumerate(hand_landmarks.landmark):
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lm_list.append([cx, cy])
                        
                    if len(lm_list) != 21:
                        continue
                        
                    # Coordenadas de los dedos principales
                    thumb_x, thumb_y = lm_list[4][0], lm_list[4][1]
                    index_x, index_y = lm_list[8][0], lm_list[8][1]
                    middle_x, middle_y = lm_list[12][0], lm_list[12][1]
                    
                    # Deteccion de dedos levantados (usando la articulacion media como referencia)
                    index_up = index_y < lm_list[6][1]
                    middle_up = middle_y < lm_list[10][1]
                    ring_up = lm_list[16][1] < lm_list[14][1]
                    pinky_up = lm_list[20][1] < lm_list[18][1]
                    
                    # Distancias
                    pinch_dist = math.hypot(thumb_x - index_x, thumb_y - index_y)
                    index_middle_dist = math.hypot(index_x - middle_x, index_y - middle_y)
                    
                    # ------------------- LÓGICA RETRO MEJORADA (MAPEO ABSOLUTO) -------------------
                    
                    # 1. SCROLL (Subir/Bajar páginas): Los 4 dedos levantados
                    if index_up and middle_up and ring_up and pinky_up:
                        if self.scroll_y == 0:
                            self.scroll_y = int(index_y)
                        diff = self.scroll_y - index_y
                        if abs(diff) > 10:
                            pyautogui.scroll(int(diff * 2))
                            self.scroll_y = int(index_y)
                        cv2.putText(img, "ESTADO: SCROLL", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
                        
                    # 2. CLICK RÁPIDO: Índice y Medio juntos parados (Signo de Paz cerrado)
                    elif index_up and middle_up and not ring_up and not pinky_up and index_middle_dist < 50:
                        self.scroll_y = 0
                        cv2.circle(img, (index_x, index_y), 20, (0, 255, 255), cv2.FILLED)
                        cv2.putText(img, "ESTADO: CLICK NORMAL", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                        
                        current_time = time.time()
                        if current_time - self.last_click_time > 0.3: # Cooldown de seguridad
                            pyautogui.click()
                            pyautogui.press('space') # Compatible con juegos
                            self.last_click_time = current_time
                            
                        # Limpiar arrastre de paso
                        if self.is_dragging:
                            pyautogui.mouseUp()
                            pyautogui.keyUp('space')
                            self.is_dragging = False

                    # 3. MOVER Y CLIC/ARRASTRAR: Solo Índice arriba
                    elif index_up and not middle_up and not ring_up and not pinky_up:
                        self.scroll_y = 0 
                        
                        # --- MOVIMIENTO ABSOLUTO (Como la version anterior pero ampliado) ---
                        x3 = np.interp(index_x, (self.frame_r, w - self.frame_r), (0, self.screen_w))
                        y3 = np.interp(index_y, (self.frame_r, h - self.frame_r), (0, self.screen_h))
                        
                        # Suavizado anti-temblor tradicional optimizado
                        self.curr_x = self.prev_x + (x3 - self.prev_x) / self.smoothening
                        self.curr_y = self.prev_y + (y3 - self.prev_y) / self.smoothening
                        
                        # Mantener dentro de la pantalla rigurosamente
                        self.curr_x = max(0, min(self.screen_w - 1, self.curr_x))
                        self.curr_y = max(0, min(self.screen_h - 1, self.curr_y))
                        
                        try:
                            pyautogui.moveTo(self.curr_x, self.curr_y) 
                        except:
                            pass
                            
                        self.prev_x, self.prev_y = self.curr_x, self.curr_y
                        
                        # ----- PELLIZCO PARA MANTENER CLICK PRESIONADO / VOLAR NAVE -----
                        if pinch_dist < 45: 
                            cv2.circle(img, (int((thumb_x+index_x)/2), int((thumb_y+index_y)/2)), 20, (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, "ESTADO: MANTENIENDO CLIC/SALTO", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                            
                            if not self.is_dragging:
                                pyautogui.mouseDown()
                                pyautogui.keyDown('space')
                                self.is_dragging = True
                                
                        else: # Soltar pellizco
                            cv2.circle(img, (index_x, index_y), 15, (255, 0, 255), cv2.FILLED)
                            cv2.putText(img, "ESTADO: MOVIENDO", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)
                            
                            if self.is_dragging:
                                pyautogui.mouseUp()
                                pyautogui.keyUp('space')
                                self.is_dragging = False
                                
                    # 4. IDLE (Puño cerrado -> Pausa total para dar descanso)
                    else:
                        if self.is_dragging:
                            pyautogui.mouseUp()
                            pyautogui.keyUp('space')
                            self.is_dragging = False
                        cv2.putText(img, "ESTADO: PAUSA", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            else:
                # Si la mano se sale de cámara soltamos clicks por seguridad
                if getattr(self, 'is_dragging', False):
                    pyautogui.mouseUp()
                    pyautogui.keyUp('space')
                    self.is_dragging = False

            cv2.imshow("Hand Gesture Mouse Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Limpiar hardware al cerrar
        cap.stop()
        cv2.destroyAllWindows()
        if getattr(self, 'is_dragging', False):
            pyautogui.mouseUp()
            pyautogui.keyUp('space')
            
if __name__ == "__main__":
    HandMouse().run()