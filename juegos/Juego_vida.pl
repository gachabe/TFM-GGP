role(player).

% Definición de las coordenadas del tablero (un tablero de 3x3 para simplicidad)
cell(1, 1). cell(1, 2). cell(1, 3).
cell(2, 1). cell(2, 2). cell(2, 3).
cell(3, 1). cell(3, 2). cell(3, 3).

% Sucesores para definir las coordenadas vecinas
succ(1, 2). succ(2, 3).

% Estado inicial
init(alive(2, 2)).
init(alive(2, 3)).
init(alive(3, 2)).
init(dead(1,1)).
init(alive(1,2)).
init(dead(1,3)).
init(dead(2,1)).
init(dead(3,1)).
init(dead(3,3)).

% Reglas para determinar el estado de una celda en el siguiente turno

% Definimos el concepto vecino, usamos 8-vecindad
neighbour(X, Y, X1, Y1) :- succ(X, X1), succ(Y, Y1).
neighbour(X, Y, X1, Y) :- succ(X, X1).
neighbour(X, Y, X1, Y1) :- succ(X, X1), succ(Y1, Y).
neighbour(X, Y, X, Y1) :- succ(Y, Y1).
neighbour(X, Y, X1, Y1) :- succ(X1, X), succ(Y1, Y).
neighbour(X, Y, X1, Y) :- succ(X1, X).
neighbour(X, Y, X1, Y1) :- succ(X1, X), succ(Y, Y1).
neighbour(X, Y, X, Y1) :- succ(Y1, Y).

count_neighbours(X, Y, N) :- findall(cell(X1, Y1), (neighbour(X, Y, X1, Y1), (alive(X1, Y1))), L), length(L, N).

% Regla de supervivencia: Una celda viva con 2 o 3 vecinos vivos sigue viva
next(alive(X, Y)) :- alive(X,Y), count_neighbours(X, Y, N), (N = 2; N = 3).

% Regla de nacimiento: Una celda muerta con exactamente 3 vecinos vivos se vuelve viva
next(alive(X, Y)) :- dead(X, Y), count_neighbours(X, Y, 3).

% Una celda se mantiene muerta si no cumple con las reglas de nacimiento o supervivencia
next(dead(X, Y)) :- cell(X, Y), \+(next(alive(X, Y))).



% Condiciones de terminalidad del juego
terminal :- not((alive(_, _))).

% Recompensas (esto es solo una formalidad, ya que el Juego de la Vida no tiene ganadores o perdedores tradicionales)
goal(player, 50) :- terminal.
goal(player, 0) :- not(terminal).
