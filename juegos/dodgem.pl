% Definición básica del juego de mesa Dodgem

% Hechos básicos
role(uno).
role(dos).

% predicados auxiliares

index(1).
index(2).
index(3).

pertenece(uno,coche1).
pertenece(uno,coche2).
pertenece(dos,coche3).
pertenece(dos,coche4).

abs_diff_one(X1, X2) :- % diferencia absoluta
    Diff is abs(X1 - X2),
    Diff =:= 1.

fuera(Coche) :- \+ cell(_, _, Coche).

% Inicio

init(cell(1,1,coche1)).
init(cell(1,2,b)).
init(cell(1,3,b)).
init(cell(2,1,coche2)).
init(cell(2,2,b)).
init(cell(2,3,b)).
init(cell(3,2,coche3)).
init(cell(3,3,coche4)).
init(control(uno)).

% Acciones legales

legal(uno,mover(X,Y1,X,Y2)) :- control(uno), cell(X,Y1,Coche1), \+ (fuera(Coche1)),
        pertenece(uno,Coche1), cell(X,Y2,b), index(Y2), Y2 is Y1 + 1.

legal(uno,mover(X1,Y,X2,Y)) :- control(uno), cell(X1,Y,Coche1), \+ (fuera(Coche1)),
        pertenece(uno,Coche1), cell(X2,Y,b), index(X2), abs_diff_one(X1,X2).

legal(uno,sacar(X,3,Coche)) :- control(uno), cell(X,3,Coche), \+ (fuera(Coche)),
        pertenece(uno, Coche).

legal(dos,mover(X1,Y,X2,Y)) :- control(dos), cell(X1,Y,Coche1), \+ (fuera(Coche1)),
        pertenece(dos,Coche1), cell(X2,Y, b), index(X2), X2 is X1 - 1.

legal(dos,mover(X,Y1,X,Y2)) :- control(dos), cell(X,Y1,Coche1), \+ (fuera(Coche1)),
        pertenece(dos,Coche1), cell(X, Y2, b), index(Y2), abs_diff_one(Y1,Y2).

legal(dos,sacar(1,Y,Coche)) :- control(dos), cell(1,Y,Coche), \+ (fuera(Coche)),
        pertenece(dos, Coche).

legal(uno, noop) :- (control(dos)).
legal(dos, noop) :- (control(uno)).

% Consecuencia de acciones

next(cell(X2,Y2,Coche)) :- does(_, mover(X1, Y1, X2, Y2)), cell(X1, Y1, Coche).
next(cell(X1,Y1,b)) :- does(_, mover(X1, Y1, _, _)), cell(X1, Y1, _).
next(cell(X, Y, Elemento)) :- cell(X, Y, Elemento), not(does(_, sacar(X, Y, Elemento))),
                not(does(_, mover(X, Y, _, _))), not(does(_, mover(_, _, X, Y))).
next(cell(X, Y, b)) :-  does(_, sacar(X, Y, Coche)), cell(X, Y, Coche).

next(control(uno)) :- (control(dos)).
next(control(dos)) :- (control(uno)).

% Recompensas

goal(uno,100) :- fuera(coche1), fuera(coche2).
goal(uno,100) :- \+ legal(uno, _), control(uno).
goal(dos,0) :- fuera(coche1), fuera(coche2).
goal(dos,0) :- \+ legal(uno, _), control(uno).

goal(dos,100) :- fuera(coche3), fuera(coche4).
goal(dos,100) :- \+ legal(dos, _), control(dos).
goal(uno,0) :- fuera(coche3), fuera(coche4).
goal(uno,0) :- \+ legal(dos, _), control(dos).

% Estados terminales

terminal :- fuera(coche1), fuera(coche2).
terminal :- fuera(coche3), fuera(coche4).
terminal :- control(Jugador), \+ legal(Jugador, _).