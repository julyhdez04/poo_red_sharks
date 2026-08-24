def main():
    nombre = input(" Ingresa tu nombre: ")
    edad = input(" Ingresa tu edad: ")
    correo_electronico = input(" Ingresa tu correo institucional: ")
    matricula = input(" Ingresa tu matricula: ")

    datos = f"Nombre: {nombre}\nEdad: {edad}\nCorreo: {correo_electronico}\n"

    with open("datos_persona.txt", "a", encoding="utf-8") as archivo:
        archivo.write(datos)

    print(f" Tu nombre es {nombre} y tu edad es {edad} ")
    print(f" Tu correo es {correo_electronico} ") 
    print(f" Tu matrícula es {matricula} ")
    print("La información se ha almacenado en datos_persona.txt")

if __name__ == "__main__":
    main()
