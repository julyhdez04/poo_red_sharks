# Diagrama UML
## Actuadores
<img width="185" height="293" alt="image" src="https://github.com/user-attachments/assets/6ceebfda-70aa-477d-8463-8c417aa4c295" />

## Sensores
<img width="893" height="843" alt="image" src="https://github.com/user-attachments/assets/639b627e-0160-4c29-a77e-c35298bc8c27" />

¿Qué es la abstracción?
La abstracción consiste en ocultar el trabajo complejo que ocurre fuera de la vista de usuario para que solo se tengan que usar comandos directos.
En el ajuste del Actuador (encender, ajustar): Solo se da la instrucción de encenderse o ponerse a un nivel como 75%. La abstracción te oculta cómo el programa revisa matemáticamente que ese 75% no rebase los límites permitidos, cómo actualiza la memoria de la máquina y cómo fabrica el mensaje de texto que se envía automáticamente a la pantalla de eventos.
En la lectura del Sensor (leer_valor_actual): Solo se le solicita al sensor que entregue su medición. La abstracción esconde cómo se simula o captura el número, cómo aplica reglas de redondeo para dejar exactamente 2 o 3 decimales, ni cómo le elige la unidad de medida (como "Bar" o "L/min") para crear una lectura perfecta lista para el usuario.
