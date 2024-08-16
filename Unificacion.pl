% Caso base: dos listas vacías unifican sin necesidad de sustituciones.
unificar([], [], []).

% Unificar la cabeza de las listas y luego recursivamente unificar las colas.
unificar([X|Xs], [Y|Ys], Sustituciones) :-
    unificar_terminos(X, Y, SustitucionesCabeza),
    unificar(Xs, Ys, SustitucionesCola),
    append(SustitucionesCabeza, SustitucionesCola, Sustituciones).

% Unificar dos términos individuales.
unificar_terminos(X, Y, []) :-
    X == Y. % Si son iguales, no se necesitan sustituciones.

unificar_terminos(X, Y, [X = Y]) :-
    var(X), !. % Si X es una variable, unificamos X con Y.

unificar_terminos(X, Y, [Y = X]) :-
    var(Y), !. % Si Y es una variable, unificamos Y con X.

unificar_terminos(X, Y, []) :-
    \+ var(X),
    \+ var(Y),
    X == Y. % Si ambos son constantes e iguales.

% Predicado principal para unificar dos funciones.
unificar_funciones(f(NombreFuncion1, Args1), f(NombreFuncion2, Args2), Sustituciones) :-
    NombreFuncion1 == NombreFuncion2, % Los nombres de las funciones deben ser iguales.
    unificar(Args1, Args2, Sustituciones).
