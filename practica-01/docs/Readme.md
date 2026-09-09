# Diagrama UML
## Actuadores
<img width="185" height="293" alt="image" src="https://github.com/user-attachments/assets/6ceebfda-70aa-477d-8463-8c417aa4c295" />

## Sensores
<img width="893" height="843" alt="image" src="https://github.com/user-attachments/assets/639b627e-0160-4c29-a77e-c35298bc8c27" />

### Abstracción: 
Permite ocultar la complejidad interna de un sistema y mostrar únicamente lo necesario para utilizarlo. Por ejemplo en `Actuador` solo es necesario `ajustar(75.5)` para indicar el valor deseado e internamente, el programa verifica que el valor esté dentro del rango permitido, si es asi actualiza la información y genera el evento correspondiente. De forma similar, `leer_valor_actual()` en `Sensor` entrega directamente la medición ocultando procesos como la generación del valor, el redondeo y la asignación de unidades

### Encapsulamiento: 
Protege los datos internos de una clase para evitar modificaciones incorrectas. En `Actuador` `punto_operacion` solo puede modificarse usando `ajustar()`, siempre que el valor se encuentre dentro de los límites establecidos. En `Sensor`, la medición se obtiene mediante `leer_valor_actual()`, asegurando que se entregue con los decimales y la unidad correctos. lo que hace que ambas clases simplifican su uso mediante métodos sencillos y al mismo tiempo protegen sus datos y procesos internos
