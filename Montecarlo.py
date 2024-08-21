from Agentes import Agentes
from time import time
from random import choice
import pyswip
"""
El arbol sera (estado, valor, diccionario)
estado : Lista de hechos
valor = (numero de ganadas, numero de visitadas)
diccionario = {accion1:arbol1,..., accionN:arbolN}
"""

class MonteCarlo(Agentes):
    def __init__(self, rol=None, acciones=None, reglas=None, tiempo=None):
        super().__init__(rol, acciones,reglas)
        self.rol = rol
        self.acciones = acciones
        self.prolog = pyswip.Prolog()
        self.prolog.consult(self.reglas, catcherrors=True)
        self.roles = self.busca_roles()
        self.tiempo = tiempo
        self.arbol = None
        self.acciones_contrarias = None

    def reset(self):
        self.arbol = None

    def turno(self,estado):
        """
        Esta función gestiona el turno del agente, primero comprueba si existe un árbol, en ese caso si ha
        habido un turno previo intenta ir a ese subarbol para seguir generando pruebas de forma aleatoria.
        Seguidamente procede como el agente ansioso, devuelve la acción que mayor valor da su camino mediante
        la media aritmética.
        """
        if self.arbol is not None:
            try:
                self.arbol = self.arbol[2][self.acciones_contrarias]
            except KeyError as e:
                self.arbol = None
        self.arbol = self.generar_arbol(arbol = self.arbol)
        dic = self.arbol[2]
        acciones = [(x, y[1]) for x, y in dic.items() if y[1][1] != 0]
        lista_ordenada = sorted(acciones, key=lambda x: (-x[1][0]/x[1][1], x[1][1]))
        print(lista_ordenada)
        eleccion = lista_ordenada[0]
        turno = [x for x in eleccion[0] if x[0] == self.rol][0][1]
        return turno


    # ALGORITMO Montecarlo
    # Selección y expansión: Se busca una hoja y se generan todos los hijos posibles, de ellos se elige uno para la simulacion
    def sel_exp(self, arbol):
        est, valor, dicc = arbol
        contador, visitadas = valor
        if not dicc:  # Era una hoja
            acciones = self.generar_lista_acciones(est)
            estados = [self.generar_estado(est, accion) for accion in acciones]
            nuevo_nivel = zip(acciones, estados)
            if estados: # Esa hoja no era terminal
                eleccion = choice(estados)
                simulado = self.simula_partida(eleccion)
                dicc = {accion:(estado, (0,0), {}) if estado != eleccion else (estado,(simulado,1),{})
                        for  accion,estado in nuevo_nivel }
            else:
                contador += self.generar_recompensa(est)
        else: # No era una hoja
            accion = choice(list(dicc.keys()))
            dicc.update({accion: self.sel_exp(dicc[accion])})
        return est, (contador, visitadas + 1), dicc


    # Simulación: Dado un estado se simula una partida
    def simula_partida(self, estado):
        def final(estado):
            """
            Calcula si un estado es terminal
            """
            def aux():
                return not bool(list(self.prolog.query("terminal")))
            return self.conHecho(estado, aux)
        terminal = final(estado)
        if not terminal:
            return self.generar_recompensa(estado)

        else:
            acciones = choice(self.generar_lista_acciones(estado))
            estadoN = self.generar_estado(estado, acciones)
            return self.simula_partida(estadoN)

    # Retropropagación: se actualiza el valor de las duplas en función de los hijos
    def retropropagacion(self, arbol):
        est, valor, dicc = arbol
        contador, visitados = valor
        if not dicc:
            return arbol
        else:
            lista_sub = [self.retropropagacion(sub_arbol) for sub_arbol in dicc.values()]
            lista = [elemento[1][0] if isinstance(elemento, tuple) else elemento for elemento in lista_sub]
            contador = sum(lista)
            dicc.update({accion:sub_arbol for accion,sub_arbol in zip(dicc,lista_sub)})
            return est, (contador, visitados), dicc

    def generar_arbol(self, arbol=None):
        if self.arbol is None:
            estado = []
            inicio = self.prolog.query("init(X)")
            for x in inicio:
                estado.append(x["X"])
            arbol = (estado, (0, 0), {})
        tinicio = time()
        while self.tiempo > time() - tinicio:
                arbol = self.sel_exp(arbol)
                arbol = self.retropropagacion(arbol)
        return arbol

    def generar_recompensa(self, estados):
        def aux():
            query = self.prolog.query(f"goal({self.rol},X)")
            recompensa = 0
            for x in query:
                recompensa = x["X"]
            query.close()
            return recompensa
        return self.conHecho(estados, aux)

Alberto = MonteCarlo("white",reglas="juegos/tic-tac-toe.pl",tiempo=0.25)
#print(Alberto.simula_partida(["col(1,1)","col(2,1)","col(3,0)","control(uno)"]))
#A = Alberto.sel_exp((['col(1, 3)', 'col(2, 2)', 'col(3, 1)', 'control(uno)'], (0, 1), {(('uno', 'take(1, 1)'), ('dos', 'noop')): (['col(1, 2)', 'col(2, 2)', 'col(3, 1)', 'control(dos)'], (0, 0), {}), (('uno', 'take(1, 2)'), ('dos', 'noop')): (['col(1, 1)', 'col(2, 2)', 'col(3, 1)', 'control(dos)'], (0, 1), {}), (('uno', 'take(1, 3)'), ('dos', 'noop')): (['col(1, 0)', 'col(2, 2)', 'col(3, 1)', 'control(dos)'], (0, 0), {}), (('uno', 'take(2, 1)'), ('dos', 'noop')): (['col(2, 1)', 'col(1, 3)', 'col(3, 1)', 'control(dos)'], (0, 0), {}), (('uno', 'take(2, 2)'), ('dos', 'noop')): (['col(2, 0)', 'col(1, 3)', 'col(3, 1)', 'control(dos)'], (0, 0), {}), (('uno', 'take(3, 1)'), ('dos', 'noop')): (['col(3, 0)', 'col(1, 3)', 'col(2, 2)', 'control(dos)'], (0, 0), {})}))
#print(Alberto.retropropagacion(A))
print(Alberto.turno(['col(1, 3)', 'col(2, 2)', 'col(3, 1)', 'control(uno)']))