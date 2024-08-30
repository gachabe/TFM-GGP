% Definición del rol
role(granjero).

% Definición de los objetos
objeto(lobo).
objeto(cabra).
objeto(coles).

% Definir las orillas del río
ubicacion(orilla_izquierda).
ubicacion(orilla_derecha).

% Estado inicial del juego: todos en la orilla izquierda
init(en(granjero, orilla_izquierda)).
init(en(lobo, orilla_izquierda)).
init(en(cabra, orilla_izquierda)).
init(en(coles, orilla_izquierda)).

% Movimientos legales del granjero
% El granjero puede moverse solo
legal(granjero, mover_solo(granjero, Destino)) :-
  (en(granjero, Origen)),
    ubicacion(Origen),
    ubicacion(Destino),
    Origen \= Destino.

% El granjero puede llevar al lobo, cabra o coles
legal(granjero, mover(granjero, Obj, Destino)) :-
    objeto(Obj),
  (en(granjero, Origen)),
  (en(Obj, Origen)),
    ubicacion(Origen),
    ubicacion(Destino),
    Origen \= Destino.

% Transiciones de estado
% Si el granjero se mueve solo
next(en(granjero, Destino)) :-
    does(granjero, mover_solo(granjero, Destino)).

% Si el granjero se mueve con otro objeto
next(en(Obj, Destino)) :-
    does(granjero, mover(granjero, Obj, Destino)),
    objeto(Obj).

next(en(granjero, Destino)) :-
    does(granjero, mover(granjero, Obj, Destino)),
    objeto(Obj).

% Mantener los objetos en su lugar si no se mueven
next(en(Obj, Ubicacion)) :-
  (en(Obj, Ubicacion)),
    objeto(Obj),
    \+ does(granjero, mover(granjero, Obj, _)).

next(en(granjero, Ubicacion)) :-
  (en(granjero, Ubicacion)),
    \+ does(granjero, mover_solo(granjero, _)).



% Condición de victoria: todo y todos están en la orilla derecha
goal(granjero, 100) :-
  (en(granjero, orilla_derecha)),
  (en(lobo, orilla_derecha)),
  (en(cabra, orilla_derecha)),
  (en(coles, orilla_derecha)).

goal(granjero, 0) :-
    en(lobo,Ubicacion),
    en(oveja,Ubicacion),
    en(granjero,OtraUbicacion).

objetivo(granjero, 0) :-
    en(oveja,Ubicacion),
    en(oveja,Ubicacion),
    en(granjero,OtraUbicacion).

% Condición de fin del juego
terminal :- objetivo(granjero,_).


