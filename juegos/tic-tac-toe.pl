role(white).
role(black).

index(1).
index(2).
index(3).

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



legal(W, mark(X,Y)) :- (cell(X,Y,b)) , (control(W)).
legal(white, noop) :- (control(black)).
legal(black, noop) :- (control(white)).

next(cell(M,N,x)) :- (cell(M,N,x)).
next(cell(M,N,x)) :- does(white,mark(M,N)) , (cell(M,N,b)).
next(cell(M,N,o)) :- (cell(M,N,o)).
next(cell(M,N,o)) :- does(black,mark(M,N)) , (cell(M,N,b)).
next(cell(M, N, b)) :- cell(M, N, b), not(does(_, mark(M, N))).
next(control(white)) :- (control(black)).
next(control(black)) :- (control(white)).

goal(white, 100) :- line(white) , \+line(black).
goal(white, 50) :- \+line(white) , \+line(black).
goal(white, 0) :- \+line(white) , line(black).
goal(black, 0) :- goal(white, 100).
goal(black, 50) :- goal(white, 50).
goal(black, 100) :- goal(white, 0).

line(W) :- row(W).
line(W) :- column(W).
line(W) :- diagonal(W).

row(white) :- (cell(M,1,x)) , (cell(M,2,x)) , (cell(M,3,x)).
row(black) :- (cell(M,1,o)) , (cell(M,2,o)) , (cell(M,3,o)).
column(white) :- (cell(1,N,x)) , (cell(2,N,x)) , (cell(3,N,x)).
column(black) :- (cell(1,N,o)) , (cell(2,N,o)) , (cell(3,N,o)).
diagonal(white) :- (cell(1,1,x)) , (cell(2,2,x)) , (cell(3,3,x)).
diagonal(white) :- (cell(3,1,x)) , (cell(2,2,x)) , (cell(1,3,x)).
diagonal(black) :- (cell(1,1,o)) , (cell(2,2,o)) , (cell(3,3,o)).
diagonal(black) :- (cell(3,1,o)) , (cell(2,2,o)) , (cell(1,3,o)).


terminal :- line(_).
terminal :- \+open.

open :- (cell(_,_,b)).