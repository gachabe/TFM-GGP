role(white).
role(black).

index(1).
index(2).
index(3).
value(x).
value(o).

base(cell(M,N,x)) :- index(M) , index(N).
base(cell(M,N,o)) :- index(M) , index(N).
base(cell(M,N,b)) :- index(M) , index(N).
base(control(white)).
base(control(black)).

input(R, mark(M,N)) :- role(R) , index(M) , index(N).
input(R, noop) :- role(R).


init(cell(1,1,b)).
init(cell(1,2,b)).
init(cell(1,3,b)).
init(cell(2,1,b)).
init(cell(2,2,b)).
init(cell(2,3,b)).
init(cell(3,1,b)).
init(cell(3,2,b)).
init(cell(3,3,b)).
init(control(white)).



legal(W, mark(X,Y)) :- cell(X,Y,b) , control(W).
legal(white, noop) :- (control(black)).
legal(black, noop) :- (control(white)).

next(cell(M,N,x)) :- (cell(M,N,x)).
next(cell(M,N,x)) :- does(white,mark(M,N)) , (cell(M,N,b)).
next(cell(M,N,o)) :- (cell(M,N,o)).
next(cell(M,N,o)) :- does(black,mark(M,N)) , (cell(M,N,b)).
next(cell(M, N, b)) :- cell(M, N, b), not(does(_, mark(M, N))).
next(control(white)) :- (control(black)).
next(control(black)) :- (control(white)).

goal(white, 100) :- line(x), \+line(o).
goal(white, 50) :- \+line(x), \+line(o).
goal(white, 0) :- \+line(x), line(o).
goal(black, 0) :- line(x), \+line(o).
goal(black, 50) :- \+line(x), \+line(o).
goal(black, 100) :- \+line(x), line(o).

line(Z) :- row(_,Z), value(Z).
line(Z) :- column(_,Z), value(Z).
line(Z) :- diagonal(Z), value(Z).

row(M, Z) :- cell(M, 1, Z), cell(M, 2, Z), cell(M, 3, Z).
column(N, Z) :- cell(1, N, Z), cell(2, N, Z), cell(3, N, Z).
diagonal(Z) :- cell(1, 1, Z), cell(2, 2, Z), cell(3, 3, Z).
diagonal(Z) :- cell(1, 3, Z), cell(2, 2, Z), cell(3, 1, Z).

terminal :- line(_).
terminal :- \+(cell(_,_,b)).

open :- (cell(_,_,b)).