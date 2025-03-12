docent(bas; bob; dieuwertje; nathalie).

% aanname: student kan als bedrijfsbegeleider kan (zo niet dan toevoegen aan zitting, check beschikbaarheid + check gelijk met bedrijf)
bedrijfsbegeleider(a; b; c; d; e; f; g; h).

begeleider(bas, B) :- B = (a; b).
begeleider(nathalie, B) :- B = (e).
begeleider(bob, B) :- B = (f; g; h).
begeleider(dieuwertje, B) :- B = (c; d).

expertise(bas, ontwikkelen).
expertise(bob, ontwikkelen).
expertise(dieuwertje, ontwerpen).
expertise(dieuwertje, ontwikkelen).
expertise(nathalie, ontwerpen).

tijdslot(t1; t2; t3; t4).

dag(d1; d2).

lokaal(l1; l2;).

beschikbaar(bas, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(nathalie, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(bob, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(dieuwertje, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(a, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(b, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(c, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(d, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(e, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(f, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(g, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
beschikbaar(h, D, T) :- (D, T) = (d1, t1; d1, t2; d1, t3; d1, t4; d2, t1; d2, t2; d2, t3; d2, t4).
% Generate
1 {zitting(BEDRIJF, VOORZITTER, BEGELEIDER, L, D, T): docent(VOORZITTER), docent(BEGELEIDER), lokaal(L), dag(D), tijdslot(T)} 1 :- bedrijfsbegeleider(BEDRIJF).

% Define
zitting_moment(DOCENT, L, D, T) :- zitting(_, DOCENT, _, L, D, T).
zitting_moment(DOCENT, L, D, T) :- zitting(_, _, DOCENT, L, D, T).

% TODO: waarom werken wildcards (_) hier niet?
% UITZOEKEN!!!!
aantal_voorzitter_per_docent(VOORZITTER, N) :- docent(VOORZITTER), N = #count { (BEDRIJF, VOORZITTER, L, D, T) : zitting(BEDRIJF, VOORZITTER, BEGELEIDER, L, D, T) }.
aantal_begeleider_per_docent(BEGELEIDER, N) :- docent(BEGELEIDER), N = #count { (BEDRIJF, VOORZITTER, L, D, T) : zitting(BEDRIJF, VOORZITTER, BEGELEIDER, L, D, T) }.

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



#minimize{N:max_aantal_zitting_per_dag(N)}.

#show zitting/6.

% #show aantal_voorzitter_per_docent/2.
% #show aantal_begeleider_per_docent/2.

#show aantal_zitting_per_dag/3.

#show max_aantal_zitting_per_dag/1.

% aantal_zitting_per_dag(dieuwertje,d1,3)



