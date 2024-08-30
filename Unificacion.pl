% Unificar el inicio de las listas y luego recursivamente unificar el final.
unificar([], [], []).
unificar([X|Xs], [Y|Ys], Sustituciones) :-
    unificar_terminos(X, Y, SustitucionesInicio),
    unificar(Xs, Ys, SustitucionesFinal),
    append(SustitucionesInicio, SustitucionesFinal, Sustituciones).


unificar_terminos(X, Y, [X = Y]) :-
    var(X), !. % Si X es una variable, unificamos X con Y.

unificar_terminos(X, Y, [Y = X]) :-
    var(Y), !. % Caso contrario.

unificar_terminos(X, Y, []) :-
    X == Y. % En cualquier otro caso.

% Predicado principal para unificar dos funciones.
unificar_funciones(f(NombreFuncion1, Args1), f(NombreFuncion2, Args2), Sustituciones) :-
    NombreFuncion1 == NombreFuncion2,
    unificar(Args1, Args2, Sustituciones).
