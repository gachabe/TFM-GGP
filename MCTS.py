from Agentes import Agentes
from time import time
from itertools import product
from random import choice
import pyswip

class MonteCarlo(Agentes):
    def __init__(self,rol=None,acciones=None,reglas=None,tiempo=None):
        super().__init__(rol, acciones)
        self.rol = rol
        self.acciones = acciones
        self.prolog = pyswip.Prolog()
        self.reglas = reglas
        self.prolog.consult(self.reglas,catcherrors=True) # Si tapo aqui sale en todas las funciones que funconan el mismo error q en la q nofunciona the more you know...
        self.roles = self.busca_roles()
        self.tiempo = tiempo
        self.arbol = None
        self.acciones_contrarias = None

    def busca_roles(self):
        query = self.prolog.query("role(X)")
        roles = []
        for rol in query:
            roles.append(rol["X"])
        query.close()
        return roles

    def reset(self):
        pass

    def turno(self, estado):
        if self.arbol is not None:
            try:
                self.arbol = self.arbol[2][self.acciones_contrarias]
            except KeyError as e:
                self.arbol = None
        self.arbol = self.generar_arbol(arbol = self.arbol,estado = estado) #Aqui ta el error
        dic = self.arbol[2]
        acciones = [(x,y[1]) for x,y in dic.items()]
        lista_ordenada = sorted(acciones, key=lambda x: x[1], reverse=True)
        turno = self.escoger_accion(lista_ordenada[0])
        return turno

    def escoger_accion(self, acciones):
        acciones = acciones[0]
        return [x for x in acciones if x[0] == self.rol][0][1]

    def conHecho(self,estado,f):
        try:
            for hecho in estado:
                self.prolog.assertz(hecho)
            return f()
        finally:
            for hecho in estado:
                self.prolog.retract(hecho)

    def generar_lista_acciones(self, estado = []):
        def aux():
            listaAcciones = self.prolog.query("legal(X,Y)")
            lista_acciones = []
            for jugador in listaAcciones:
                lista_acciones.append((jugador["X"], jugador["Y"]))
            listaAcciones.close()
            dic = {rol: [accion for accion in lista_acciones if accion[0] == rol] for rol in self.roles}
            valores = list(dic.values())
            lista_acciones = list(product(*valores))
            return lista_acciones
        return self.conHecho(estado,aux)

    def generar_arbol(self, arbol=None,estado=None):
        """
        Arbol -> (Estado,valor,{accion:Arbol})
        valor -> \sum valorHijos \div numHijos
        """
        def generar_hoja(arbol):
            est, valor, dic = arbol
            acciones = (self.generar_lista_acciones(est))

            if not acciones:  # Esa hoja era terminal

                return (est, self.generar_recompensa(est), {})
            else:
                accion = choice(acciones)
                estN = self.generar_estado(est, accion)
                if accion in dic.keys(): # Si la rama ya ha sido visitada
                    dic.update({accion: generar_hoja(dic[accion])})
                    return (est, self.generar_valor(dic), dic)
                else:
                    dic.update({accion: generar_hoja((estN, self.generar_valor(dic), {}))})
                    return (est, self.generar_valor(dic),dic)

        tinicio = time()
        while self.tiempo > time() - tinicio:
            if arbol is None: #Comienza el algoritmo
                if estado is None:
                    estado = []
                    inicio = self.prolog.query("init(X)")
                    for x in inicio:
                        estado.append(x["X"])
                arbol = (estado,0,{})

            else:
                generar_hoja(arbol)
        est,valor,dic = arbol
        arbol = (est,self.generar_valor(dic),dic)

        return arbol


    # def generar_estado(self, estado, accion):
    #     """
    #     Estado será una lista con una descripción de un estado y dada la lista de acciones devolverá el nuevo estado
    #     """
    #     estado_inicio = estado[:]
    #     self.prolog.consult(self.reglas, catcherrors=True)
    #     for hecho in estado:
    #         self.prolog.assertz(hecho)
    #     for hecho in accion:
    #         self.prolog.assertz(f"does({hecho[0]},{hecho[1]})")
    #     query = self.prolog.query("next(X)")
    #     estado = []
    #     for x in query:
    #         estado.append(x["X"])
    #         #print(estado)
    #     query.close()
    #     for hecho in estado_inicio:
    #         self.prolog.retract(hecho)
    #     for hecho in accion:
    #         self.prolog.retract(f"does({hecho[0]},{hecho[1]})")
    #     return estado

    def generar_estado(self,estado,accion):
        estado_inicio = estado[:]
        def aux():
            for hecho in accion:
                self.prolog.assertz(f"does({hecho[0]},{hecho[1]})")
            query = self.prolog.query("next(X)")
            estado = []
            for x in query:
                estado.append(x["X"])
            query.close()
            for hecho in accion:
                self.prolog.retract(f"does({hecho[0]},{hecho[1]})")
            return estado
        return self.conHecho(estado, aux)

    def generar_recompensa(self,estados):
        self.prolog.consult(self.reglas, catcherrors=True)
        def aux():
            query = self.prolog.query(f"goal({self.rol},X)")
            recompensa = 0
            for x in query:
                recompensa = x["X"]
            query.close()
            return recompensa
        return self.conHecho(estados,aux)



    def generar_valor(self,arboles):
        """
        Devuelve el valor asociado a un nodo del arbol dada la siguiente formula:
         valor -> \sum valorHijos/ numHijos
        """
        if arboles:
            suma = sum([y[1] for y in arboles.values()])
            valor = suma/(len(arboles))
        else:
            valor = 0
        return valor

def imprimir_arbol(arbol, nivel=0):
    """
    Imprime un árbol de forma estructurada.
    """
    estado, valor, hijos = arbol

    # Imprimir el estado y valor del nodo actual
    print("  " * nivel + f"Estado: {estado}, Valor: {valor}")

    # Imprimir los hijos recursivamente
    for accion, hijo in hijos.items():
        print("  " * (nivel + 1) + f"Accion: {accion}")
        imprimir_arbol(hijo, nivel + 2)



#paco = MonteCarlo(reglas="juegos/Nim", rol="uno")
#print(paco.generar_lista_acciones(estado = ['col(1, 1)', 'col(2, 0)', 'col(3, 0)', 'control(dos)'] ))
#print(paco.turno(['col(1, 1)', 'col(2, 0)', 'col(3, 0)', 'control(dos)']))
#print(paco.generar_estado(['col(1, 3)', 'col(2, 0)', 'col(3, 0)', 'control(uno)'],(("uno","take(1,1)"),("dos","noop"))))
#print(paco.generar_arbol())
#for i in (paco.encontrar_ramas(paco.generar_arbol())):
 #   print(i)
