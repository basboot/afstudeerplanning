% Facts will be created in Python

% Generate
1 {zitting(BEDRIJF, VOORZITTER, BEGELEIDER, L, D, T): docent(VOORZITTER), docent(BEGELEIDER), lokaal(L), dag(D), tijdslot(T)} 1 :- bedrijfsbegeleider(BEDRIJF).

% Define
zitting_moment(DOCENT, L, D, T) :- zitting(_, DOCENT, _, L, D, T).
zitting_moment(DOCENT, L, D, T) :- zitting(_, _, DOCENT, L, D, T).

aantal_voorzitter_per_docent(VOORZITTER, N) :- docent(VOORZITTER), N = #count { BEDRIJF : zitting(BEDRIJF, VOORZITTER, _,_,_,_) }.
aantal_begeleider_per_docent(BEGELEIDER, N) :- docent(BEGELEIDER), N = #count { BEDRIJF : zitting(BEDRIJF, _, BEGELEIDER,_,_,_) }.

aantal_zitting_per_dag(DOCENT, D, N) :- docent(DOCENT), dag(D), N = #count { (DOCENT, L, D, T) : zitting_moment(DOCENT, L, D, T)}.

max_aantal_zitting_per_dag(MAX_N) :- MAX_N = #max { N, DOCENT, D : aantal_zitting_per_dag(DOCENT, D, N) }.

% Test
% voorzitter en begeleider verschillend
:- zitting(_, VOORZITTER, BEGELEIDER, _, _, _), VOORZITTER = BEGELEIDER.
% voorzitter is geen begeleider van afstudeerder
:- zitting(BEDRIJF, VOORZITTER, _, _, _, _), begeleider(VOORZITTER, BEDRIJF).
% begeleider moet begeleider zijn van afstudeerder
:- zitting(BEDRIJF, _, BEGELEIDER, _, _, _), not begeleider(BEGELEIDER, BEDRIJF).
% Iedereen beschikbaar
:- zitting(BEDRIJF, _, _, _, D, T), not beschikbaar(BEDRIJF, D, T).
:- zitting(_, VOORZITTER, _, _, D, T), not beschikbaar(VOORZITTER, D, T).
:- zitting(_, _, BEGELEIDER, _, D, T), not beschikbaar(BEGELEIDER, D, T).

% % aantal keer voorzitter en begeleider moet gelijk zijn
:- aantal_voorzitter_per_docent(D, N1), aantal_begeleider_per_docent(D, N2), N1 != N2.

% geen 2 zittingen op zelfde tijd in zelfde lokaal
:- zitting(A1, _, _, L, D, T), zitting(A2, _, _, L, D, T), A1 != A2.
% docent niet bij 2 zittingen (2 lokalen) tegelijkertijd
:- zitting_moment(DOCENT, L1, D, T), zitting_moment(DOCENT, L2, D, T), L1 != L2.



% #minimize{N:max_aantal_zitting_per_dag(N)}.

#show zitting/6.

% #show aantal_voorzitter_per_docent/2.
% #show aantal_begeleider_per_docent/2.

% #show aantal_zitting_per_dag/3.

% #show max_aantal_zitting_per_dag/1.

% aantal_zitting_per_dag(dieuwertje,d1,3)



