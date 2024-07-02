import pyswip as ps
from Agentes import Legal, Aleatorio, Ansioso
from MCTS import MonteCarlo


class Partida:
    """
    Esta clase recibirá una lista de agentes, el nombre del juego que se quiera jugar y creará una nueva instancia de
    partida. Esta clase se encargará de gestionar toda la partida, conectado el archivo 'reglas.pl' con 'partida.pl'
    El funcionamiento será copiar las reglas y el estado inicial de la partida en un archivo aparte y después, mediante
    prolog, lanzar las consultas y usar assertz para y generando los nuevos estados.
    """
    def __init__(self, juego, tiempo_turno=None, agentes=None):
        self. prolog = ps.Prolog()
        self.juego = juego
        self.tiempo_turno = tiempo_turno
        self.ruta_reglas = r"juegos/" + juego + ".pl"
        self.prolog.consult(self.ruta_reglas, catcherrors=False)
        self.agentes = self.crear_agentes(agentes)
        self.estado_inicio = self.estado_inicial()
        self.prolog.consult(self.ruta_reglas, catcherrors=False)

    def __str__(self):
        return f"Una partida de {self.juego} y juegan {self.agentes}"

    def crear_agentes(self, lista):  # Por mejorar
        def crear_instancias(lista, roles):
            instancias = []
            for elemento, rol in zip(lista, roles):
                instancia = None
                match elemento:
                    case "Ansioso":
                        instancia = Ansioso(reglas=self.ruta_reglas, rol=rol)
                    case "Legal":
                        instancia = Legal(rol=rol)
                    case "Aleatorio":
                        instancia = Aleatorio(rol=rol)
                    case "MonteCarlo":
                        instancia = MonteCarlo(reglas=self.ruta_reglas, rol="uno", tiempo=self.tiempo_turno)
                    case _:
                        print(f"Error: Elemento desconocido '{elemento}'")
                if instancia is not None:
                    instancias.append(instancia)
            return instancias
        query = self.prolog.query("role(X)")
        roles = [rol['X'] for rol in query]
        return crear_instancias(lista,roles)

    def estado_inicial(self):
        self.prolog.consult(self.ruta_reglas, catcherrors=False)
        estados = self.prolog.query("init(X)")
        aux = []
        for estado in estados:
            aux.append(estado["X"])
        estados.close()
        return aux

    def conHecho(self,estado,f):
        try:
            for hecho in estado:
                self.prolog.assertz(hecho)
            return f()
        finally:
            for hecho in estado:
                self.prolog.retract(hecho)

    def buscar_acciones(self, estado, agente):
        """
        Le pasa a cada agente las acciones legales que pueden realizar
        """
        def aux():
            acciones = []
            query = self.prolog.query("legal("+agente.rol+",X)")
            for busqueda in query:
                acciones.append(busqueda["X"])
            query.close()
            agente.accionesLegales(acciones)
            return acciones
        return self.conHecho(estado, aux)

    def siguiente_estado(self, estado, muestra = False):
        acciones = []
        for agente in self.agentes:
            self.buscar_acciones(estado, agente)
            accion = agente.turno(estado)
            if muestra:
                print(f"El agente {agente} hizo {accion}")
            acciones.append(accion)
        def aux():
            sig_estado = []
            for agente, accion in zip(self.agentes, acciones):
                self.prolog.assertz("does(" + agente.rol + "," + accion + ")")
                agente.acciones_contrarias = tuple((agente.rol, accion) for agente, accion in zip(self.agentes, acciones))
            query = self.prolog.query("next(X)")
            for busqueda in query:
                sig_estado.append(busqueda["X"])
            query.close()
            self.prolog.retractall("does(X,Y)")

            return sig_estado
        return self.conHecho(estado, aux)

    def final(self,estado):
        def aux():
            return not bool(list(self.prolog.query("terminal")))
        return self.conHecho(estado, aux)

    def ganador(self,estado):
        def aux():
            query = self.prolog.query("ganar(X)")
            for i in query:
                ganador = i["X"]
            return ganador
        return self.conHecho(estado,aux)

    def jugar_partida(self, muestra=False):
        #self.generar_partida()
        print("Comienza la partida, el estado inicial es: ", self.estado_inicio)
        for agente in self.agentes:
            agente.reset()
        estado = self.estado_inicio
        final = self.final(estado)
        while final:
            estado = self.siguiente_estado(estado, muestra)
            if muestra:
                print(estado)
            #self.siguiente_turno(estado)
            final = self.final(estado)
        ganador = self.ganador(estado)
        #print(f"Ha ganado el jugador {ganador}, cuyo agente es {self.agentes[roles.index(ganador)]}") #Se podria mejorar poniendo tambien el nombre del agnte
        return ganador

A = Partida("Nim",agentes =["Legal","MonteCarlo"], tiempo_turno=0.5)
uno = 0
dos = 0
for _ in range(1):
    x = A.jugar_partida(muestra=True)
    if x == "uno":
        uno +=1
    else:
        dos +=1

print(f"El jugador uno  ha ganado {uno} veces y el otro {dos}")
#print(A.siguiente_estado(['col(1, 1)', 'col(2, 0)', 'col(3, 0)', 'control(dos)']))