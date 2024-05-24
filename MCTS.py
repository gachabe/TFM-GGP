from Agentes import *
from time import time
from itertools import product
from random import choice
import pyswip

class MonteCarlo(Ansioso):
    def __init__(self,rol=None,acciones=None,reglas=None,tiempo=None):

        self.rol = rol
        self.acciones = acciones
        self.prolog = pyswip.Prolog()
        self.reglas = reglas
        self.roles = self.busca_roles()
        self.tiempo = tiempo

    def reset(self):
        pass

    def turno(self,estado):
        arbol = self.generar_arbol(estado = estado) #Aqui ta el error
        dic = arbol[2]
        acciones = [(x,y[1]) for x,y in dic.items()]
        lista_ordenada = sorted(acciones, key=lambda x: x[1], reverse=True)
        turno = self.escoger_accion(lista_ordenada[0])
        return turno

    def escoger_accion(self, acciones):
        acciones = acciones[0]
        return [x for x in acciones if x[0] == self.rol][0][1]

    def generar_lista_acciones(self, estado = []):
        """
        Devuelve una lista de duplas, cada elemento de la dupla es un rol y una accion posible
        [((rol1,accion1),(rol2,accion2)),...]
        """
        self.prolog.consult(self.reglas, catcherrors=True)

        for x in estado:
            print(x)
            self.prolog.assertz(x)
        listaAcciones = self.prolog.query("legal(X,Y)")
        lista_acciones = []
        for jugador in listaAcciones:
            lista_acciones.append((jugador["X"], jugador["Y"]))
        listaAcciones.close()
        dic = {rol:[accion for accion in lista_acciones if accion[0]== rol] for rol in self.roles }
        valores = list(dic.values())
        lista_acciones = list(product(*valores))
        for x in estado:
            self.prolog.retract(x)
        return lista_acciones


    def generar_arbol(self, arbol = None, estado =None):
        """
        Arbol -> (Estado,valor,{accion:Arbol})
        valor -> \sum valorHijos \div numHijos
        """
        def generar_hoja(arbol):
            if self.generar_lista_acciones(arbol[0]) == []:  # Esa hoja era terminal

                return (arbol[0], self.generar_recompensa(arbol[0]), {})
            else:

                est, valor, dic = arbol
                acciones = (self.generar_lista_acciones(estado = est))

                accion = choice(acciones)
                estN = self.generar_estado(est, accion)

                if accion in dic.keys(): # Si la rama ya ha sido visitada

                    dic.update({accion: generar_hoja(dic[accion])})

                    return (est, self.generar_valor(dic), dic)

                else:
                    dic.update({accion: generar_hoja((estN, self.generar_valor(dic), {}))})
                    return (est, self.generar_valor(dic),dic)

        tinicio = time()


        for i in range(4):


            if arbol is None: #Comienza el algoritmo
                #if not estado is None:
                    #est = []
                   # inicio = self.prolog.query("init(X)")
                   # for x in inicio:
                  #      est.append(x["X"])
                 #   inicio.close()
                #    arbol = (est,0,{})
                #else:
                arbol = (estado,0,{})

            else:
                generar_hoja(arbol)


        est,valor,dic = arbol
        arbol = (est,self.generar_valor(dic),dic)

        return arbol


    def generar_estado(self,estado,accion):
        """
        Estado será una lista con una descripción de un estado y dada la lista de acciones devolverá el nuevo estado
        """
        estado_inicio = estado[:]
        self.prolog.consult(self.reglas, catcherrors=True)
        for hecho in estado:
            self.prolog.assertz(hecho)
        for hecho in accion:
            self.prolog.assertz(f"does({hecho[0]},{hecho[1]})")
        query = self.prolog.query("next(X)")
        estado = []
        for x in query:
            estado.append(x["X"])
            #print(estado)
        query.close()

        for hecho in estado_inicio:
            self.prolog.retract(hecho)
        for hecho in accion:
            self.prolog.retract(f"does({hecho[0]},{hecho[1]})")
        return estado

    def generar_recompensa(self, estados):
        self.prolog.consult(self.reglas, catcherrors=True)
        for estado in estados:
            self.prolog.assertz(estado)
        query = self.prolog.query(f"goal({self.rol},X)")
        recompensa = 0
        for x in query:
            recompensa = x["X"]
        query.close()
        for estado in estados:
            self.prolog.retract(estado)
        return recompensa

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



#paco = MonteCarlo(reglas="juegos/Nim.pl",rol="uno")
#print(paco.generar_lista_acciones(estado = ['col(1, 3)', 'col(2, 0)', 'col(3, 0)', 'control(uno)']))
#for i in (paco.encontrar_ramas(paco.generar_arbol())[):
 #   print(i)