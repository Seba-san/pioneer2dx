# Libreria Pioneer2dx
La idea de esta libreria es poder descargarla y sin compilar nada podes correr el escenario. Para esto es necesario tener instalado ROS, las variables de entorno sourceadas y ejecutar el comando:

```sh
$ cd pioneer2dx
$ roslaunch display_camera.launch model:=model.xacro
```
Es importante que se ejecute desde el directorio del repositorio (en este caso pioneer2dx) 
Este comando iniciará gazebo server sin la interfaz gráfica, iniciara el mundo test_word.sdf y pone el pioneer2dx en el origen de coordenadas.

Pioneer2dx cuenta con una cámara  frontal 800x600px publicando las imagenes a 15 frames. Todo esto es configurable en el archivo camera_plug.xacro




License
----

MIT (por ahora)
