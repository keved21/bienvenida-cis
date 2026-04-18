# 🖐️ BienvenidAI - Control por Gestos

BienvenidAI es una aplicación de **Mouse Virtual** impulsada por inteligencia artificial (MediaPipe) que permite controlar el cursor de tu computadora y jugar videojuegos utilizando únicamente movimientos de las manos frente a la cámara.

Este proyecto fue diseñado específicamente para ser utilizado en eventos de bienvenida, permitiendo una interacción fluida y futurista sin necesidad de periféricos físicos o conexión a internet.

---

## 🚀 Características

- **Movimiento Absoluto**: El cursor sigue la posición de tu dedo índice con suavidad y precisión.
- **Click Rápido**: Gesto de "Paz" (índice y medio juntos) para realizar un click izquierdo.
- **Arrastre y Salto**: Pellizco (pulgar e índice) para mantener el click presionado o realizar saltos constantes en juegos.
- **Scroll Vertical**: Mano abierta (4 o 5 dedos) para desplazarte por páginas web o menús.
- **Optimizada para Juegos**: Los gestos de click también activan la tecla `Espacio`, siendo ideal para juegos como *Chrome Dino* o *Geometry Dash*.
- **Sin Lag**: Implementa procesamiento en hilos (threading) y resolución balanceada para una respuesta instantánea.

---

## 🛠️ Tecnologías Utilizadas

*   **Python 3.10+**
*   **MediaPipe**: Para el rastreo de puntos clave de la mano de alta precisión.
*   **OpenCV**: Para la captura de video y la interfaz visual en tiempo real.
*   **PyAutoGUI**: Para la emulación de mouse y teclado a nivel de sistema.
*   **Numpy**: Procesamiento matemático de coordenadas.

---

## 📦 Instalación y Uso

### Requisitos Previos
Asegúrate de tener Python instalado (se recomienda 3.10 o 3.11).

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/keved21/bienvenida-cis.git
cd BienvenidAI
```

### Paso 2: Configurar el entorno (Recomendado)
Puedes crear un entorno virtual para mantener las dependencias aisladas:
```bash
python -m venv venv
venv\Scripts\activate
```

### Paso 3: Instalar dependencias
```bash
pip install opencv-python mediapipe pyautogui numpy
```

### Paso 4: Ejecutar la aplicación
Puedes iniciar el programa simplemente haciendo doble click en:
- `Lanzar_Mouse.bat` (Windows)

O mediante la consola:
```bash
python mouse.py
```

---

## 🎮 Controles y Gestos

| Gesto | Acción |
| :--- | :--- |
| **Solo dedo índice arriba** | Mover cursor |
| **Índice y Medio juntos** | Click Izquierdo / Salto rápido |
| **Pellizco (Pulgar e Índice)** | Mantener click (Drag) / Salto sostenido |
| **Mano abierta (4-5 dedos)** | Scroll (subir/bajar) |
| **Puño cerrado / Mano fuera** | Pausa de seguridad |
| **Tecla [Q]** | Salir de la aplicación |

---

## 📋 Consejos para un mejor rendimiento
1. **Buena Iluminación**: Asegúrate de que tu mano esté bien iluminada para que la cámara la detecte fácilmente.
2. **Fondo Simple**: Evita que haya otras personas u objetos moviéndose detrás de tu mano.
3. **Cámara Estable**: Mantén la cámara fija para evitar vibraciones en el cursor.

---

## 🛠️ Compilación (Crear Ejecutable)
Si deseas crear un archivo `.exe` para distribuir la aplicación sin necesidad de instalar Python:
```bash
pip install pyinstaller
pyinstaller mouse.spec
```
El ejecutable aparecerá en la carpeta `dist/`.

---

Desarrollado con ❤️ para la comunidad de **CIS**.
