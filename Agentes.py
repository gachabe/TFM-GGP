from random import choice
import pyswip as ps
from itertools import product
from copy import deepcopy
"""
La clase agentes sera la clase padre, estos recibirán un rol por partida y en cada turno recibirán una lista de posibles
acciones, dependiendo del agente se seleccionará una u otra y enviará esta a la clase partida.
 Cada agente sera creado particularmente según su método de juego
"""

class Agentes:
    def __init__(self,rol=None,acciones=None, reglas=None):
        self.rol = rol
        self.acciones = acciones
        self.reglas  = reglas

    def accionesLegales(self,acciones):
        self.acciones = acciones

    def __str__(self):
        return f"Clase: {type(self).__name__}"

class Legal(Agentes):
    """
    El agente legal jugará siempre la primera acción posible.
    """
    def __init__(self, rol=None, acciones=None):
        super().__init__(rol, acciones)

    def turno(self):
        return self.acciones[0]

class Aleatorio(Agentes):
    """
    El agente aleatorio jugará siempre una acción aleatoria
    """
    def __init__(self, rol=None, acciones=None):
        super().__init__(rol, acciones)

    def turno(self):
        return choice(self.acciones)

class Ansioso(Agentes):
    """
    Este agente creará todo el árbol de posibles estados y buscará si tiene una ruta óptima.
    Solo será viable en juegos pequeños. En lista_acciones guardaremos todas las posibles acciones
    que podrán realizar los jugadores. Cuando el juego sea simétrico coincidirá con acciones.
    Es mejorable puesto que solo ordena las politicas en ganable y no ganables pero no prioriza las fuertemente ganables
    """
    def __init__(self,reglas =None,rol=None,acciones =None):
        super().__init__(rol, acciones)
        self.prolog = ps.Prolog()
        self.reglas = reglas
        self.roles = self.busca_roles()
        self.rama = self.ramas()
        self.lista_acciones = self.generar_lista_acciones()  # Acciones por rol para un estado dado
        self.lista_politica = self.generar_politica()
        self.politica_actual = self.lista_politica[0]
        self.copia1 = deepcopy(self.lista_politica)
        self.copia2 = deepcopy(self.politica_actual)




    def reset(self):

        self.lista_politica = deepcopy(self.copia1)
        self.politica_actual = deepcopy(self.copia2)



    def turno(self):
        """
        Comprobará si la siguiente acción de su politica actual está entre sus acciones legales y la realizará eliminando
        el primer miembro de su politica actual, de no ser así contará cuantos turnos lleva con esta política,
         restando la longitud de la política actual a su copia en la lista de políticas, despues eliminará esta
         de la lista y comenzará la siguiente.
        """
        if len(self.politica_actual) != 0 and self.escoger_accion(self.politica_actual[0]) in self.acciones:
            print("soy", self.rol)
            print("mi politica es:", self.politica_actual)
            turno = self.escoger_accion(self.politica_actual[0])
            self.politica_actual = self.politica_actual[1:]
            print("voy a hacer: ", turno)
            return turno
        else:
            print("Soy", self.rol, " y cambio de politica")
            numero_turnos =len(self.politica_actual)- len(self.lista_politica[0])
            self.lista_politica = self.lista_politica[1:]
            self.politica_actual = self.lista_politica[0][numero_turnos:]
            return self.turno()

    def escoger_accion(self, acciones):
        return [x for x in acciones if x[0] == self.rol][0][1]

    def busca_roles(self):
        self.prolog.consult(self.reglas, catcherrors=True)
        query = self.prolog.query("role(X)")
        roles = []
        for rol in query:
            roles.append(rol["X"])
        query.close()
        return roles

    def generar_lista_acciones(self, estado = []):
        """
        Devuelve un diccionario cuyas claves son los roles posibles y los valores las acciones para cada rol dado un
        estado
        """
        self.prolog.consult(self.reglas, catcherrors=True)
        if estado == []:
            inicio = self.prolog.query("init(X)")
            for x in inicio:
                estado.append(x["X"])
            inicio.close()
        for x in estado:
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

    def generar_recompensa(self,estados):
        self.prolog.consult(self.reglas, catcherrors=True)
        for estado in estados:
            self.prolog.assertz(estado)
        recompensa = []
        for roles in self.roles:
            query = self.prolog.query(f"goal({roles},X)")
            for x in query:
                recompensa.append({roles: x["X"]})
            query.close()
        for estado in estados:
            self.prolog.retract(estado)
        return recompensa

    def generar_arbol(self, est = []):
        self.prolog.consult(self.reglas, catcherrors=True)
        if est == []:
            inicio = self.prolog.query("init(X)")
            for x in inicio:
                est.append(x["X"])
            inicio.close()
        #print("acciones,",self.generar_lista_acciones(est))
        if self.generar_lista_acciones(est) == []:

            #return (est,self.generar_recompensa(est))
            return self.generar_recompensa(est)
        else:
            #return (est, {accion: self.generar_arbol(self.generar_estado(est, accion)) for accion in self.generar_lista_acciones(est)})
            return {accion: self.generar_arbol(self.generar_estado(est, accion))
                    for accion in self.generar_lista_acciones(est)}

    def ramas(self,arbol=None, keys=None, result=None):
        """
        Recibe un arbol y devuelve una lista de listas donde cada sublista es una posible política
        """
        if arbol is None:
            arbol = self.generar_arbol()
        if keys is None:
            keys = []
        if result is None:
            result = []
        if isinstance(arbol, dict):
            for key, value in arbol.items():
                self.ramas(value, keys + [key], result)
        else:
            result.append(keys + [arbol])
        return result

    def generar_politica(self):
        def merge_dicts(list_of_dicts):
            merged_dict = {}
            for d in list_of_dicts:
                merged_dict.update(d)
            return merged_dict
        orden = (lambda x: merge_dicts(x[-1])[self.rol])
        lista = self.ramas()
        lista.sort(key=orden,reverse=True)
        for politica in lista:
            del politica[-1]
        return lista


def visualize(root, indent=0):
    if type(root) == dict:
        for k, v in root.items():
            print(" "*indent + f"{k}:")
            visualize(v, indent+2)
    else:
        print(" "*indent + repr(root))
str = {(('uno', 'take(1, 1)'), ('dos', 'noop')): {(('uno', 'noop'), ('dos', 'take(1, 1)')): {(('uno', 'take(1, 1)'), ('dos', 'noop')): [('uno', 100), ('dos', 0)]}, (('uno', 'noop'), ('dos', 'take(1, 2)')): [('uno', 0), ('dos', 100)]}, (('uno', 'take(1, 2)'), ('dos', 'noop')): {(('uno', 'noop'), ('dos', 'take(1, 1)')): [('uno', 0), ('dos', 100)]}, (('uno', 'take(1, 3)'), ('dos', 'noop')): [('uno', 100), ('dos', 0)]}

#paco = Ansioso("Nim",rol="uno")
#print(paco.generar_estado(["control(uno)","col(1,1)","col(2,3)","col(3,5)"],(('uno', 'take(1, 1)'), ('dos', 'noop'))))
#print(paco.generar_recompensa(["control(uno)","col(1,0)","col(2,0)","col(3,0)"]))
#print(paco.generar_arbol())

#print(paco.politica_actual[1])



