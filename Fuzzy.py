from Agentes import Agentes
from Fuzzy_aux import *
from functools import reduce
from itertools import product, chain, combinations
from pyswip import Prolog

class Fuzzy(Agentes):

    tau = 0.9

    def __init__(self, rol=None, acciones=None, reglas=None, tiempo=None, valor=None):
        super().__init__(rol, acciones,reglas)
        self.prolog = Prolog()
        self.rol = rol
        self.acciones = acciones
        self.prolog.consult(self.reglas, catcherrors=True)
        self.tiempo = tiempo
        self.acciones_contrarias = None
        self.t_norma = lambda x, y: x * y # Cambiarla cuando me entere de la disyuncion
        self.valor = valor if valor is not None else self.tau
        self.diccionario = list2dict(goal_rol(self.rol, self.reglas)[1])

    def turno(self, estado):
        valores = self.generar_valores_estados(estado)
        acciones = max(valores, key=valores.get)
        for rol, accion in acciones:
            if rol == self.rol:
                return accion


    def calcula_valor_estado(self, estado, calculo): # Mejorar cuando entienda la disyuncion con t-normas
        if calculo.startswith("\\+"):
            return 1 - self.calcula_valor_estado(estado, calculo[2:])
        imagen = busca_funciones(calculo, self.diccionario)
        if not imagen:

            return self.tau if calculo in estado else 1 - self.tau

        else:
            if len(imagen) == 1:
                lista = [self.calcula_valor_estado(estado,x) for x in imagen[0]]
                return reduce(self.t_norma, lista)

            else:
                acum = 1
                for unificado in imagen:
                    lista = [self.calcula_valor_estado(estado, x) for x in unificado]
                    acum *= (1 - reduce(self.t_norma, lista))
                return 1 - acum

    def valor_esperado_puntuacion(self, estado):
        def calcular_valor_esperado(tupla):
            valores = [int(parse_funcion(valor)[1][-1])/100 for valor in tupla]
            acum = 1
            for valor in valores:
                acum *= valor
            return acum
        def calcular_probabilidad(tupla):
            probabilidades = [self.calcula_valor_estado(estado, elemento) for elemento in tupla]
            acum = 1
            for probabilidad in probabilidades:
                acum *= probabilidad
            return acum
        recompensas = goal_rol(self.rol, self.reglas)[0]
        recompensas = [recompensa for recompensa in recompensas if parse_funcion(recompensa)[1][-1] != "0"]
        combinaciones = list(chain(*[[combinacion for combinacion in combinations(recompensas, r)] for r in range(1, len(recompensas)+1)]))
        #print([(calcular_probabilidad(tupla) ,calcular_valor_esperado(tupla)) for tupla in combinaciones])
        valor_esperado =100* sum([((-1)**(1+len(tupla)))*calcular_probabilidad(tupla)*calcular_valor_esperado(tupla) for tupla in combinaciones])

        return valor_esperado

    def generar_valores_estados(self, estado = []):
        acciones = self.generar_lista_acciones(estado)
        estados_alcanzables = [self.generar_estado(estado, accion) for accion in acciones]
        return {accion:self.valor_esperado_puntuacion(estadoN) for accion,estadoN in zip(acciones,estados_alcanzables)}





#prueba = Fuzzy("white","asione","juegos/tic-tac-toe.pl","tiempo")
# print(prueba.calcula_valor_estado(["cell(2, 2, x)"],"goal(white,100)"))
# print(prueba.valor_esperado_puntuacion(["cell(2, 2, x)"]))
estado_inicial =[
  "cell(1,1,b)",
  "cell(1,2,b)",
  "cell(1,3,b)",
  "cell(2,1,b)",
  "cell(2,2,b)",
  "cell(2,3,b)",
  "cell(3,1,b)",
  "cell(3,2,b)",
  "cell(3,3,b)",
  "control(white)"
]


#print(prueba.generar_estado(estado_inicial,(('white', 'mark(1, 1)'), ('black', 'noop'))))
#print((prueba.turno(estado_inicial)))