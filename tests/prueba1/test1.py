def main():
    nombre = input("Ingresa tu nombre: ")
    edad = input("Ingresa tu edad: ")

    datos = f"Nombre: {nombre}\nEdad: {edad}\n"

    with open("datos_persona.txt", "a", encoding="utf-8") as archivo:
        archivo.write(datos)

    print(f"Tu nombre es {nombre} y tu edad es {edad}")
    print("La información se ha almacenado en datos_persona.txt")

if __name__ == "__main__":
    main()
