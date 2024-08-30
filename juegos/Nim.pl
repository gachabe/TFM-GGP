role(uno).
role(dos).
columna(1).
columna(2).
columna(3).
cantidad(1).
cantidad(2).
cantidad(3).
base(col(M,_)) :- columna(M).
base(control(uno)).
base(control(dos)).
input(R, take(M,N)) :- role(R) , columna(M) , cantidad(N).
input(R, noop) :- role(R).
init(col(1, 4)).
init(col(2, 2)).
init(col(3, 1)).
init(control(uno)).
legal(W, take(X,Y)) :- (col(X,C)), cantidad(Y), (control(W)),Y =< C.
legal(uno, noop) :- (control(dos)).
legal(dos, noop) :- (control(uno)).
next(col(M,Z)) :- does(_,take(M,N)) , (col(M,Y)),cantidad(N),Z is Y-N.
next(col(M,N)) :- (col(M,N)), does(_,take(J,_)), (not(J = M)).
next(control(uno)) :- (control(dos)).
next(control(dos)) :- (control(uno)).
goal(uno, 100) :- ganar(uno).
goal(dos, 0) :-  ganar(uno).
goal(uno, 0) :-  ganar(dos).
goal(dos, 100) :-  ganar(dos).
ganar(W):-col(1, 0),col(2, 0),col(3, 0),control(W).
terminal :- ganar(_).





