# TurtleSwarm

Este es un mini-proyecto para la materia de Redes y Comunicación Industrial.

El proyecto consiste en una demostación del control enjambre,
para lograr eso utilizamos ROS2 (Robot Operating System 2) y python,
donde utilizamos el programa turtlesim para spawnear varias tortugas
y que estas realizen un círculo.

## Instalación
```bash

```

## Ejecutar
Para ejecutar el código:

```bash
# Para abrir turtlesim
source ./install/setup.bash
ros2 launch swarm_circles swarm.launch.py
```

En otra terminal el control de las tortugas
```bash
source ./install/setup.bash
ros2 run swarm_circles keyboard_node
```
