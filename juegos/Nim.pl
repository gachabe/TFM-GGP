
role(uno).
role(dos).
valor(1).
valor(2).
valor(3).
cantidad(1).
cantidad(2).
cantidad(3).
base(col(M,_)) :- valor(M).
base(col(M,_)) :- valor(M).
base(col(M,_)) :- valor(M).
base(control(uno)).
base(control(dos)).
input(R, take(M,N)) :- role(R) , valor(M) , cantidad(N).
input(R, noop) :- role(R).
init(col(1,3)).
init(col(2,0)).
init(col(3,0)).
init(control(uno)).
legal(W, take(X,Y)) :- (col(X,C)) , cantidad(Y), (control(W)),Y =< C.
legal(uno, noop) :- (control(dos)).
legal(dos, noop) :- (control(uno)).
next(col(M,Z)) :- does(_,take(M,N)) , (col(M,Y)),cantidad(N),Z is Y-N.
next(col(M,N)) :- (col(M,N)),does(_,take(J,_)),(not(J = M)).
next(control(uno)) :- (control(dos)).
next(control(dos)) :- (control(uno)).
goal(uno, 100) :- ganar(uno) , \+ganar(dos).
goal(dos, 0) :-  ganar(uno) , \+ganar(dos).
goal(uno, 0) :-  ganar(dos) , \+ganar(uno).
goal(dos, 100) :-  ganar(dos) , \+ganar(uno).
ganar(W):-col(1,0),col(2,0),col(3,0),control(W).
terminal :- ganar(_).



