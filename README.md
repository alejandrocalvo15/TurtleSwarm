# TurtleSwarm

Este es un mini-proyecto para la materia de Redes y Comunicación Industrial.

El proyecto consiste en una demostación del control enjambre,
para lograr eso utilizamos ROS2 (Robot Operating System 2) y python,
donde utilizamos el programa turtlesim para spawnear varias tortugas
y que estas realizen un círculo.

# Instrucciones de instalación

> **Nota:** Antes de proceder ya se debe contar con el link del repositorio del proyecto.

## Pasos

1. Ir a la carpeta de Ubuntu en donde se desea clonar el repositorio de git.

2. Una vez ahí, clonar el repositorio con:

   ```bash
   git clone https://github.com/alejandrocalvo15/TurtleSwarm
   ```

3. Ya clonado el repositorio, instalar colcon con:

   ```bash
   sudo apt install colcon
   ```

4. Finalmente, ejecutar el comando para construir el programa:

   ```bash
   colcon build
   ```

Con esto, el proyecto quedará instalado.

# Ejecución

Para la ejecución. El proceso fue el siguiente:

## 1. Lanzamiento del enjambre (esclavos)

1. Se hace `source` en `[carpeta_clon]/TurtleSwarm`:

   ```bash
   source install/setup.bash
   ```

2. Se ejecuta el programa:

   ```bash
   ros2 launch swarm_circles swarm.launch.py
   ```

3. Esto debería abrir el **TurtleSim** con los 4 esclavos.

## 2. Ejecución del maestro (keyboard)

1. En una **nueva terminal**, se hace `source` en `[carpeta_clon]/TurtleSwarm`:

   ```bash
   source install/setup.bash
   ```

2. Se ejecuta el programa `keyboard_node.py`:

   ```bash
   ros2 run swarm_circles keyboard_node
   ```

3. Esto debe abrir el **keyboard** con las teclas de operación
## 3. Funcionamiento conjunto

Con ambas fases funcionando en conjunto queda concluida la puesta en ejecución
