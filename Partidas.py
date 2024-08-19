import pyswip as ps
from Agentes import Legal, Aleatorio, Ansioso
from Montecarlo import MonteCarlo
from Fuzzy import Fuzzy


class Partida:
    """
    Esta clase recibirá una lista de agentes, el nombre del juego que se quiera jugar y creará una nueva instancia de
    partida. Se encargará de gestionar toda la partida, haciendo las consultas en el archivo 'reglas.pl'.
    """
    def __init__(self, juego, tiempo_turno=None, agentes=None):
        self. prolog = ps.Prolog()
        self.juego = juego
        self.tiempo_turno = tiempo_turno
        self.ruta_reglas = r"juegos/" + juego + ".pl"
        self.prolog.consult(self.ruta_reglas, catcherrors=False)
        self.agentes = self.crear_agentes(agentes)
        self.estado_inicial = self.crear_estado_inicial()

    def __str__(self):
        return f"Una partida de {self.juego} y juegan {self.agentes}"

    def crear_agentes(self, lista):
        def crear_instancias(lista, roles):
            instancias = []
            for elemento, rol in zip(lista, roles):
                match elemento:
                    case "Ansioso":
                        instancia = Ansioso(reglas=self.ruta_reglas, rol=rol)
                    case "Legal":
                        instancia = Legal(rol=rol, reglas=self.ruta_reglas)
                    case "Aleatorio":
                        instancia = Aleatorio(rol=rol, reglas=self.ruta_reglas)
                    case "MonteCarlo":
                        instancia = MonteCarlo(reglas=self.ruta_reglas, rol=rol, tiempo=self.tiempo_turno)
                    case "Fuzzy":
                        instancia = Fuzzy(reglas=self.ruta_reglas, rol=rol, tiempo=self.tiempo_turno)
                    case _:
                        raise Exception(f"Error: Elemento desconocido '{elemento}'")
                if instancia is not None:
                    instancias.append(instancia)
            return instancias
        query = self.prolog.query("role(X)")
        roles = [rol['X'] for rol in query]
        return crear_instancias(lista, roles)

    def crear_estado_inicial(self):
        """
        Calcula el estado inicial de las partidas utilizando el predicado init()
        """
        estados = self.prolog.query("init(X)")
        estado_inicial = [estado["X"] for estado in estados]
        estados.close()
        return estado_inicial

    def conHecho(self, estado, f):
        """
        Funcion auxiliar, actua simulando un estado para otra funcion
        """
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
            query = self.prolog.query("legal("+agente.rol+",X)")
            acciones = [busqueda["X"] for busqueda in query]
            query.close()
            agente.accionesLegales(acciones)
            return acciones
        return self.conHecho(estado, aux)

    def siguiente_estado(self, estado, muestra=False):
        """
            Funcion que lleva el bucle principal de juego, dado un estado recibe las acciones de los jugadores
        las simula con assert y retract y con next calcula el siguiente estado
        """
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

    def final(self, estado):
        """
        Calcula si un estado es terminal
        """
        def aux():
            return not bool(list(self.prolog.query("terminal")))
        return self.conHecho(estado, aux)

    def ganador(self, estado):
        """
        Calcula el rol ganador de una partida
        """
        def aux():
            query = self.prolog.query("goal(X,Y)")
            puntuaciones = [(puntuacion["X"], puntuacion["Y"]) for puntuacion in query]
            query.close()
            ganador = max(puntuaciones, key=lambda x: x[1])[0]
            return ganador
        return self.conHecho(estado, aux)

    def jugar_partida(self, muestra=False, n_partidas=1):
        cuentas = {agente.rol: 0 for agente in self.agentes}
        for i in range(1, n_partidas+1):
            print(f"Comienza la partida {i}, el estado inicial es:  {self.estado_inicial}")
            for agente in self.agentes:
                agente.reset()
            estado = self.estado_inicial
            final = self.final(estado)
            while final:
                estado = self.siguiente_estado(estado, muestra)
                if muestra:
                    print(estado)
                final = self.final(estado)
            ganador = self.ganador(estado)
            try:
                cuentas[ganador] += 1
            except:
                pass
        print("Las puntuaciones han sido: ")
        for agente in cuentas:
            print(f"{agente} ha ganado {cuentas[agente]}")
        return


A = Partida("tic-tac-toe", agentes=["Legal", "MonteCarlo"], tiempo_turno=0.25)


#A = Partida("Juego_vida", agentes=[], tiempo_turno=0.25)

A.jugar_partida(muestra=False, n_partidas=2)
