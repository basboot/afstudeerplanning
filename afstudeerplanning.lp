% Facts will be created in Python

% Generate
1 { zitting(AFSTUDEERDER, BEDRIJF, VOORZITTER, BEGELEIDER, L, D, T) : docent(VOORZITTER), lokaal(L), dag(D), tijdslot(T) } 1 :- zitting_required(AFSTUDEERDER, BEDRIJF, BEGELEIDER).
%1 {zitting(AFSTUDEERDER, BEDRIJF, VOORZITTER, BEGELEIDER, L, D, T): bedrijfsbegeleider(BEDRIJF), docent(VOORZITTER), docent(BEGELEIDER), lokaal(L), dag(D), tijdslot(T)} 1 :- afstudeerder(AFSTUDEERDER).

% Define
zitting_moment(DOCENT, L, D, T) :- zitting(_, _, DOCENT, _, L, D, T).
zitting_moment(DOCENT, L, D, T) :- zitting(_, _, _, DOCENT, L, D, T).

aantal_voorzitter_per_docent(VOORZITTER, N) :- docent(VOORZITTER), N = #count { AFSTUDEERDER : zitting(AFSTUDEERDER, _, VOORZITTER, _,_,_,_) }.
aantal_begeleider_per_docent(BEGELEIDER, N) :- docent(BEGELEIDER), N = #count { AFSTUDEERDER : zitting(AFSTUDEERDER, _, _, BEGELEIDER,_,_,_) }.

aantal_zitting_per_dag(DOCENT, D, N) :- docent(DOCENT), dag(D), N = #count { T : zitting_moment(DOCENT, _, D, T) }.

max_aantal_zitting_per_dag(MAX_N) :- MAX_N = #max { N : aantal_zitting_per_dag(_, _, N) }.


expertise_tijdens_zitting(A, E) :- zitting(A, _, V, _, _, _, _), expertise(V, E).
expertise_tijdens_zitting(A, E) :- zitting(A, _, _, B, _, _, _), expertise(B, E).

% Test
% voorzitter en begeleider verschillend
:- zitting(_, _, VOORZITTER, BEGELEIDER, _, _, _), VOORZITTER = BEGELEIDER.
% voorzitter en bedrijfsbegeleider verschillend (mogelijk bij startup coach)
:- zitting(_, BEDRIJF, VOORZITTER, _, _, _, _), VOORZITTER = BEDRIJF.
% voorzitter is geen begeleider van afstudeerder
:- zitting(AFSTUDEERDER, _, VOORZITTER, _, _, _, _), begeleider(VOORZITTER, AFSTUDEERDER).
% begeleider moet begeleider zijn van afstudeerder
:- zitting(AFSTUDEERDER, _, _, BEGELEIDER, _, _, _), not begeleider(BEGELEIDER, AFSTUDEERDER).
% bedrijf moet bedrijf zijn van afstudeerder
:- zitting(AFSTUDEERDER, BEDRIJF, _, _, _, _, _), not coach(BEDRIJF, AFSTUDEERDER).
% Iedereen beschikbaar
:- zitting(_, BEDRIJF, _, _, _, D, T), not beschikbaar(BEDRIJF, D, T).
:- zitting(_, _, VOORZITTER, _, _, D, T), not beschikbaar(VOORZITTER, D, T).
:- zitting(_, _, _, BEGELEIDER, _, D, T), not beschikbaar(BEGELEIDER, D, T).

% % aantal keer voorzitter en begeleider moet gelijk zijn
:- aantal_voorzitter_per_docent(D, N1), aantal_begeleider_per_docent(D, N2), N1 != N2.

% geen 2 zittingen op zelfde tijd in zelfde lokaal
:- zitting(A1, _, _, _, L, D, T), zitting(A2, _, _, _, L, D, T), A1 != A2.
% docent niet bij 2 zittingen (2 lokalen) tegelijkertijd
:- zitting_moment(DOCENT, L1, D, T), zitting_moment(DOCENT, L2, D, T), L1 != L2.

% expertise ontwikkelen moet bij elke zitting zijn
%:- not expertise_tijdens_zitting(A, ontwikkelen), afstudeerder(A).

#minimize { N : aantal_zitting_per_dag(_, _, N) }.

% #show zitting/7.

% #show aantal_voorzitter_per_docent/2.
% #show aantal_begeleider_per_docent/2.

% #show aantal_zitting_per_dag/3.

% #show max_aantal_zitting_per_dag/1.

% aantal_zitting_per_dag(dieuwertje,d1,3)



