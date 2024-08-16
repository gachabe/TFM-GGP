from pyswip import Prolog
prolog = Prolog
prolog.consult("Unificacion.pl")
palabras_clave = ["role", "input", "base", "init", "does", "next", "legal"]


def abrir_archivo(juego):
    with open(juego, "r", encoding="utf8") as file:
        proposiciones = []
        for line in file:
            if not any([palabra in line for palabra in palabras_clave]) and line != "\n":
                proposiciones.append(line.strip())
        return proposiciones


def goal_rol(rol, juego):
    proposiciones = abrir_archivo(juego)
    resultado = []
    recompensas = []
    query = f"goal({rol}"
    for proposicion in proposiciones:
        if "goal" in proposicion:
            if query in proposicion:
                recompensas.append(proposicion.split(" :-")[0])
                resultado.append(proposicion)
        else:
            resultado.append(proposicion)
    return recompensas, resultado


def list2dict(lista):
    def unir_funciones_segmentadas(segmentos):
        funciones_completas = []
        funcion_actual = ""

        for i, segmento in enumerate(segmentos):
            if ")" not in segmento:
                funcion_actual += segmento + ","
            else:

                funcion_actual += segmento
            # Verifica si es el final de una función segmentada (asumimos que una función completa termina en ').')
            if funcion_actual.endswith(')'):
                funciones_completas.append(funcion_actual.strip())
                funcion_actual = ""  # Reinicia la variable para la siguiente función

        # Si hay alguna función no terminada al final, añadirla también
        if funcion_actual:
            funciones_completas.append(funcion_actual.strip())

        # Retorna una tupla con las funciones completas
        return tuple(funciones_completas)
    reglas = {}
    for elemento in lista:
        if ":-" in elemento:
            elemento = elemento.split(":-")
            elemento = list(map((lambda x: x.replace(" ", "")), elemento))
            reglas[unir_funciones_segmentadas(tuple(elemento[1].split(",")))] = elemento[0]
    return reglas


def parse_funcion(funcion):
    # Encontrar el nombre de la función y la parte de los argumentos
    name_end_idx = funcion.find('(')
    name = funcion[:name_end_idx]

    # Extraer los argumentos y eliminamos los paréntesis
    args_str = funcion[name_end_idx + 1:-1]
    if args_str.endswith(")"):
        args_str = funcion[name_end_idx + 1:-2]

    # Separar los argumentos por comas
    args = [arg.strip() for arg in args_str.split(',')]

    return name, args


def build_funcion(name, args):
    # Unir los argumentos en una cadena separada por comas
    args_str = ', '.join(args)

    # Construir la representación de la función como cadena
    funcion = f"{name}({args_str})"

    return funcion


def sustitucion(funcion, valores):
    """
    Dada una funcion f(x,y,z) y una lista de tuplas [(X,x), (Y,y),...] cambia las ocurrencias en f de la lista
    """
    funcion, argumentos = parse_funcion(funcion)
    for i, argumento in enumerate(argumentos):
        if argumento in valores:
            argumentos[i] = valores[argumento]
    return build_funcion(funcion, argumentos)


def busca_funciones(funcion, diccionario):
    """
    Esta funcion recibe una funcion f(x,y,z) y un diccionario de proposiciones y devuelve una lista de listas con
    todas las posibles unificaciones. Cada sublista sera una unificacion distinta.
    """
    def procesar_sustituciones(resultado):
        if resultado:
            sustituciones = resultado[0]['Sustituciones']
            # Mapear los nombres originales a las variables internas
            variables = {key: value for key, value in resultado[0].items() if key != 'Sustituciones'}
            sustituciones_legibles = {}
            for sustitucion in sustituciones:
                var, valor = sustitucion.args
                # Encontrar el nombre original de la variable
                nombre_var = next((k for k, v in variables.items() if v == var), str(var))
                sustituciones_legibles[nombre_var] = f"{valor}"
            return sustituciones_legibles
        return []

    f, argumentos = parse_funcion(funcion)
    string = "[" + ", ".join(argumentos) + "]"
    unificados = []

    for cuerpo, cabeza in diccionario.items():
        f2, argumentos2 = parse_funcion(cabeza)
        string2 = "[" + ", ".join(argumentos2) + "]"
        query = list(prolog.query(f"unificar_funciones(f({f},{string}),f({f2},{string2}),Sustituciones)."))
        sustituciones = procesar_sustituciones(query)
        if isinstance(sustituciones, dict):
            sustituidos = [sustitucion(unificado, sustituciones) for unificado in cuerpo]
            unificados.append(sustituidos)

    return unificados
