role(player).
% Estado inicial
init(bombilla(1, apagada)).
init(bombilla(2, apagada)).
init(bombilla(3, apagada)).
init(bombilla(4, apagada)).
init(bombilla(5, apagada)).

% Predicados auxiliares
succ(1, 2).
succ(2, 3).
succ(3, 4).
succ(4, 5).

cambio(apagada, encendida).
cambio(encendida, apagada).

% Acciones legales
legal(player, accionar(X)) :- bombilla(X, _).

% Estados sucesores
next(bombilla(X, EstadoN)) :-
    does(player, accionar(X)),
    bombilla(X, Estado),
    cambio(Estado, EstadoN).

next(bombilla(X, EstadoN)) :-
    does(player, accionar(Y)),
    succ(X, Y),
    bombilla(X, Estado),
    cambio(Estado, EstadoN).

next(bombilla(X, EstadoN)) :-
    does(player, accionar(Y)),
    succ(Y, X),
    bombilla(X, Estado),
    cambio(Estado, EstadoN).

next(bombilla(X, Estado)) :-
    bombilla(X, Estado),        % Mantener el estado de X
    \+ does(player, accionar(X)),   % Si el jugador no acciona X
    \+ (does(player, accionar(Y)), (succ(X, Y) ; succ(Y, X))).  % y tampoco acciona Y que sea adyacente a X

% Recompensas
goal(player, 100) :- bombilla(1, encendida), bombilla(2, encendida), bombilla(3, encendida), bombilla(4, encendida), bombilla(5, encendida).


% Estado terminal
terminal :- goal(_, _).