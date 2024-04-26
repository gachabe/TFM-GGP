import pyswip as ps
from Agentes import Legal, Aleatorio, Ansioso
prolog = ps.Prolog()


class Partida:
    """
    Esta clase recibirá una lista de agentes, el nombre del juego que se quiera jugar y creará una nueva instancia de
    partida. Esta clase se encargará de gestionar toda la partida, conectado el archivo 'reglas.pl' con 'partida.pl'
    El funcionamiento será copiar las reglas y el estado inicial de la partida en un archivo aparte y después, mediante
    prolog, lanzar las consultas y usar assertz para y generando los nuevos estados.
    """
    def __init__(self, juego, tiempo_turno=None, agentes=None):
        self.juego = juego
        self.tiempo_turno = tiempo_turno
        self.ruta_reglas = r"juegos/" + juego + ".pl"
        self.agentes = self.crear_agentes(agentes) #Hay que cambiar esto para comprobar que es una lista de clase Agente

        self.partida = r"partidas/"+juego+".pl"
        self.reglas = self.abrir_reglas()

    def __str__(self):
        return f"Una partida de {self.juego} y juegan {self.agentes}"

    def crear_agentes(self,lista):#Por mejorar
        def crear_instancias(lista,roles):
            instancias = []
            for elemento,rol  in zip(lista,roles):
                if elemento == "Ansioso":
                    instancia = Ansioso(reglas = self.ruta_reglas,rol =rol)
                elif elemento == "Legal":
                    instancia = Legal(rol=rol)
                elif elemento == "Aleatorio":
                    instancia = Aleatorio(rol=rol)
                else:
                    print(f"Error: Elemento desconocido '{elemento}'")
                    continue
                instancias.append(instancia)
            return instancias
        prolog.consult(self.ruta_reglas, catcherrors=True)
        roles = []
        query = prolog.query("role(X)")
        for rol in query:
            roles.append(rol['X'])
        query.close()
        return crear_instancias(lista,roles)

    def abrir_reglas(self):
        """
        Con este método abriremos las reglas
        """
        lineas = []
        with open(self.ruta_reglas, "r") as archivo:
            for linea in archivo:
                lineas.append(linea)
        return lineas

    def estado_inicial(self):
        prolog.consult(self.ruta_reglas, catcherrors=False)
        estados = prolog.query("init(X)")
        aux = []
        for estado in estados:
            aux.append(estado["X"])
        estados.close()
        return aux

    def buscar_acciones(self, agente):

        prolog.consult(self.partida, catcherrors=True)
        acciones = []
        query = prolog.query("legal("+agente.rol+",X)")

        for busqueda in query:
            acciones.append(busqueda["X"])
        query.close()
        agente.accionesLegales(acciones)
        return acciones

    def siguiente_estado(self):# Esto habra que cambiarlo cuadno haga los agentes
        prolog.consult(self.partida, catcherrors=False)
        sig_estado = []
        for agente in self.agentes:
            self.buscar_acciones(agente)
            accion = agente.turno()
            prolog.assertz("does("+agente.rol +","+accion+")")
        query = prolog.query("next(X)")
        for busqueda in query:
                sig_estado.append(busqueda["X"]+".\n")
        query.close()
        prolog.retractall("does(X,Y)")
        return sig_estado

    def generar_partida(self):
        """
        Este es el método que nos generará la partida, recibirá los agentes y simulará los turnos y acciones.
        """
        reglas = self.reglas
        estado_inicial = self.estado_inicial()
        inicio = []
        lista_reglas = []
        with open(self.partida, "w") as archivo:
            for linea in reglas:
                if "init" not in linea:
                    archivo.write(linea)
                    lista_reglas.append(linea)
            for estado in estado_inicial:
                archivo.write(estado+'.\n')
                inicio.append(estado)
        #return inicio, lista_reglas
        return
    def buscar_roles(self):
        """
        Este método busca los roles posibles y los asigna a los distintos agentes.
        """
        prolog.consult(self.partida, catcherrors=False)
        roles = []
        query = prolog.query("role(X)")
        for rol in query:
            roles.append(rol['X'])
        query.close()
        #for agente, rol in zip(self.agentes, roles):
         #   agente.rol = rol
        return roles

    def siguiente_turno(self,estados):
        with open(self.partida, "w") as partida:
            for regla in self.reglas:
                partida.write(regla)
            for estado in estados:
                partida.write(estado)
        return

    def actualizar_agentes(self):
        for agente in self.agentes:
            agente.reglas = self.ruta_reglas
            if hasattr(agente, 'reset'):
                agente.reset()



    def jugar_partida(self,muestra=False):
        self.generar_partida()
        print("Comienza la partida, el estado inicial es: ", self.estado_inicial())

        roles = self.buscar_roles()
        for agente in self.agentes:
            if hasattr(agente, 'reset'):
                agente.reset()
        prolog.consult(self.partida,catcherrors=False)
        X = (not bool(list(prolog.query("terminal"))))
        #X = True
        while X:
            estado = self.siguiente_estado()
            if muestra:
                print(estado)
            self.siguiente_turno(estado)
            prolog.consult(self.partida)
            X = (not bool(list(prolog.query("terminal"))))
        query = prolog.query("ganar(X)")
        for i in query:
            ganador = i["X"]
        #print(f"Ha ganado el jugador {ganador}, cuyo agente es {self.agentes[roles.index(ganador)]}") #Se podria mejorar poniendo tambien el nombre del agnte
        return ganador




#Antonio = Ansioso("Nim","uno")
#Raquel = Ansioso("Nim","dos") #Hay que mejorar el rol del jugador Anioso
A = Partida("Nim",agentes =["Ansioso","Ansioso"])

#A.generar_partida()
legal = 0
aleatorio = 0
for _ in range(10):
    x = A.jugar_partida(muestra=True)
    if x == "uno":
        legal +=1
    else:
        aleatorio +=1
print(f"El jugador uno  ha ganado {legal} veces y el otro {aleatorio}")



#prolog.consult(r"partidas/Nim.pl", catcherrors=True)
#X = bool(list(prolog.query("terminal")))
#Y = prolog.query("control(X)")

#print(((X)))


