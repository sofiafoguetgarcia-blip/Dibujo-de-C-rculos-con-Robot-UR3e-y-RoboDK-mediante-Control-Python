# -*- coding: utf-8 -*-
from robodk.robolink import *                   # importa API de RoboDK para conectarse a la estación, accede a robots, targets, etc.
from robodk.robomath import *                   # para el uso de funciones matemáticas
import math                                     # librería estándar de Python (trigonometría, radianes/grados, etc)

RDK = Robolink()                                # enlace con la RoboDK en la que nos encontramos
RDK.setRunMode(RUNMODE_SIMULATE)                # uso para ejecución tan SOLO en Simulación

# ----------- PARÁMETROS -----------
RADIO_MM        = 50.0       
ALTURA_Z        = 15.0                          # “bolígrafo abajo”
ALTURA_SALIDA   = ALTURA_Z + 30                 # “bolígrafo arriba”
PUNTOS          = 120                           # más puntos → círculo más suave
REDONDEO_MM     = 2.0                           # blend para el trazado (no para subir/bajar)

# ----------- OBJETOS -----------
robot = RDK.Item('', ITEM_TYPE_ROBOT)           # usa  el primer robot de la estación (si tienes varios, mejor usa Item('UR3e', ITEM_TYPE_ROBOT) con nombre)
base  = RDK.Item('UR3e Base', ITEM_TYPE_FRAME)  # busca el frame con ese nombre (tu base de trabajo).
tool  = robot.getLink(ITEM_TYPE_TOOL)           # obtiene la herramienta activa (tu lápiz).
t1    = RDK.Item('Target 1', ITEM_TYPE_TARGET)  # target que se usa como centro del círculo y para fijar orientación.

robot.setFrame(base)                            # todos los movimientos referenciados a la base del UR3e.
robot.setTool(tool)                             # activa la herramienta (TCP correcto).

# ----------- GUARDAR JUNTAS INICIALES -----------
joints_iniciales = robot.Joints()               # Lee y guarda las juntas actuales del robot (articulares).
                                                # Al final, volverás exactamente a esta postura (aparcar como empezó).

pose_center = t1.Pose()                         # orientación fija del lápiz. Matriz 4×4 de la pose del Target 1 (posición y orientación).
xc, yc, _ = pose_center.Pos()                   # Pos(): extrae los componentes XYZ de esa pose.
                                                # xc, yc, _: te quedas con X e Y como centro del círculo (Z lo fijas tú con ALTURA_Z).

# ----------- PUNTOS DEL CÍRCULO -----------
pts = []
for i in range(PUNTOS):                         # recorre uniformemente 0…360° en PUNTOS pasos.
    ang = math.radians(i * (360.0 / PUNTOS))    # convierte grados a radianes (trigonometría).
    x = xc + RADIO_MM * math.cos(ang)           
    y = yc + RADIO_MM * math.sin(ang)           # x, y: coordenadas paramétricas del círculo (centro (xc, yc), radio RADIO_MM).
    p = pose_center.copy()                      # clona también la orientación del Target 1 para cada punto (mantiene el lápiz orientado igual).
    p.setPos([x, y, ALTURA_Z])                  # fija la altura de dibujo (todos los puntos exactamente a Z=15 mm).
    pts.append(p)                               # guarda la pose del punto de trazo.

# Punto inicial (para cierre exacto)
p0 = pts[0]

try:
    # 0) Ir al target 1 (config segura)
    robot.MoveJ(t1)                              # va a Target 1 en articular (rápido, sin garantizar trayectoria recta). Útil para posicionarse de forma segura y fijar una configuración de juntas “cómoda”.

    # 1) Bajar vertical (bolígrafo abajo) SIN blend
    px, py, _ = pose_center.Pos()                # extraes px, py (el centro)
    p_down = pose_center.copy()                  # misma orientación, misma X/Y del centro, Z = ALTURA_Z.
    p_down.setPos([px, py, ALTURA_Z])
    robot.setRounding(0.0)                       # sin blend → bajada vertical pura (sin anticipar movimientos).
    robot.MoveL(p_down)                          # movimiento lineal (recto) al plano de dibujo.

    # 2) Ir al primer punto SIN blend
    robot.MoveL(p0)                              # Lleva el TCP al primer punto del círculo, aún sin blend para que no “trace” diagonales raras ni deje marcas al entrar.

    # 3) Trazar el círculo con blend pequeño
                                                 # Activas el blend (suavizado) para los segmentos intermedios → trazo fluido.
                                                 # Recorres todos los puntos restantes del círculo con líneas cortas.
    robot.setRounding(REDONDEO_MM)
    for p in pts[1:]:
        robot.MoveL(p)

    # 4) Cerrar el círculo EXACTO al p0
                                                 # Antes de cerrar, desactivas el blend para que no anticipe el siguiente movimiento.
                                                 # Vuelves exactamente al primer punto y cierras sin que dibuje de más.
    robot.setRounding(0.0)
    robot.MoveL(p0)

    # 5) Subir vertical (bolígrafo arriba)
    p_up = pose_center.copy()                    # misma X/Y del centro; Z = ALTURA_SALIDA (15 + 30).
    p_up.setPos([px, py, ALTURA_SALIDA])         # Con Rounding=0.0, la subida es vertical pura, sin marcar el plano.
    robot.MoveL(p_up)

    # 6) VOLVER A LA POSICIÓN INICIAL REAL
    robot.MoveJ(joints_iniciales)                # regresa a la misma postura articular en la que empezó el programa (no solo a Target 1).

    print("✔ Círculo completado y regreso a la posición inicial.")

except Exception as e:
    print("Error:", e)                           # Si ocurre cualquier excepción (por ejemplo, inalcanzable, herramienta no válida, etc.), la imprime en consola en lugar de romper silenciosamente.