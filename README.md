## Trazado de Círculos con un Robot UR3e usando Python + RoboDK
Este proyecto implementa una solución completa para controlar un robot UR3e desde RoboDK con Python, con el objetivo de realizar el trazado preciso de un círculo sobre una superficie usando un lápiz como herramienta. El programa gestiona el descenso vertical del TCP, la generación del círculo mediante puntos discretos, movimientos seguros sin autocolisiones y retorno a la postura inicial del robot.


#  Características

✔ Dibujo de círculos mediante discretización (120 puntos → suavidad óptima)
✔ Control del lápiz (TCP): bajada vertical precisa a Z=15 mm
✔ Movimientos seguros: sin colisiones internas y sin cambios de orientación inesperados
✔ Blend controlado para evitar “rayitas” en el inicio y fin del trazo
✔ Compatibilidad con simulación y robot real
✔ Retorno automático a la postura inicial del robot
✔ Código totalmente limpio, comentado y fácil de extender


# Funcionamiento General del Sistema
El robot utiliza Target 1 como punto de referencia para:

Determinar el centro del círculo
Definir la orientación del lápiz (TCP)
Establecer la configuración segura inicial

El programa realiza las siguientes etapas:
  1️⃣ Inicio
  
    Conexión con RoboDK
    Detección del robot UR3e, herramienta del lápiz y frame base
    Lectura y guardado de la postura articular inicial
  
  2️⃣ Preparación del dibujo
  
  Se calcula matemáticamente un conjunto de puntos (poses 4×4) formando un círculo:
  
    Coordenadas X, Y paramétricas
    Orientación copiada de Target 1 (para que el lápiz nunca rote)
    Altura fija Z = 15 mm
    
  3️⃣ Movimiento seguro
  
    MoveJ → ir a Target 1
    MoveL → bajar en vertical hasta Z=15 mm (sin blend)
    MoveL → ir al primer punto (sin blend, evita rayas)
    
  4️⃣ Trazado del círculo
  
    Activa blend (rounding = 2 mm)
    MoveL a los 120 puntos del círculo
    Desactiva blend y vuelve al punto inicial → cierre perfecto
  
  5️⃣ Salida y retorno
  
    MoveL → subida vertical limpia Z+30 mm
    MoveJ → volver a la postura articular guardada al inicio
    

# Generación del círculo

Se usa la ecuación paramétrica del círculo:
x = xc + R · cos(θ)
y = yc + R · sin(θ)

donde:

xc, yc = coordenadas del Target 1
R = radio definido (50 mm)
θ avanza en pasos de 360° / nº de puntos

El resultado es un conjunto de poses con la misma orientación original pero con posiciones X,Y distintas.


# Requisitos

RoboDK instalado
Python 3.x
Librerías internas:

robodk.robolink
robodk.robomath
math


Robot simulado UR3e con TCP configurado en la punta del lápiz
Targets colocados correctamente:

Target 1 → centro y orientación del círculo

# Cómo Ejecutar

Abrir RoboDK
Cargar estación con:

Robot UR3e
Herramienta Generic Pencil Tool
Target 1


Abrir circle_draw.py en el editor integrado
Pulsar Run
El robot:

Baja el lápiz
Traza el círculo
Sube
Vuelve a su postura inicial

# Seguridad del Movimiento
El código evita problemas típicos:

 - Bloqueos de cinemática

 - Rotaciones inesperadas de muñeca

 - Autocolisiones del UR3e

 - Rayas residuales entre operaciones

 - Cambios no deseados de TCP

Gracias a:

 - Uso de MoveL verticales con setRounding(0.0)

 - Mantener siempre la orientación del Target 1

 - No usar MoveC (que puede producir flips según orientación)

 - Retorno controlado con MoveJ

# Video

https://github.com/user-attachments/assets/5f0ad105-8abf-488e-95c6-7905b9b9e50e


