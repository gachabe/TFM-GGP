role(player).

init(cell(1, rana)).
init(cell(2, rana)).
init(cell(3, empty)).
init(cell(4, sapo)).
init(cell(5, sapo)).

% Definir qué sigue a cada posición para simplificar las reglas de movimiento.
con(1, 2).
con(2, 3).
con(3, 4).
con(4, 5).

% Definir los movimientos legales.
legal(player, move(X, Y)) :-
    (cell(X, rana)),
    con(X, Y),
    (cell(Y, empty)).
legal(player, move(X, Y)) :-
    (cell(X, rana)),
    con(X, Z),
    con(Z, Y),
    (cell(Z, sapo)),
    (cell(Y, empty)).
legal(player, move(X, Y)) :-
    (cell(X, sapo)),
    con(Y, X),
    (cell(Y, empty)).
legal(player, move(X, Y)) :-
    cell(X, sapo),
    con(Z, X),
    con(Y, Z),
    cell(Z, rana),
    cell(Y, empty).

% Definir cómo cambia el estado después de un movimiento.
next(cell(X, empty)) :-
    does(player, move(X, Y)).
next(cell(Y, SapORana)) :-
    does(player, move(X, Y)),
    cell(X, SapORana).

next(cell(X, SapORana)) :-
    (cell(X, SapORana)),
    \+ does(player, move(X, _)),
    \+ does(player, move(_, X)).

% Definir la condición de victoria.
goal(player, 100) :- cell(1, sapo), cell(2, sapo), cell(4, rana), cell(5, rana).


% Definir la condición de fin del juego.
terminal :-
    goal(player, 100).
terminal :- \+ legal(player,X).
