% Facts will be created in Python

% Generate
1 { zitting(AFSTUDEERDER, BEDRIJF, VOORZITTER, BEGELEIDER, L, D, T) : docent(VOORZITTER), lokaal(L), dag(D), tijdslot(T) } 1 :- zitting_required(AFSTUDEERDER, BEDRIJF, BEGELEIDER).

% Define
zitting_moment(DOCENT, L, D, T) :- zitting(_, _, DOCENT, _, L, D, T).
zitting_moment(DOCENT, L, D, T) :- zitting(_, _, _, DOCENT, L, D, T).

zitting_moment(DAG_TIJD) :- zitting(_, _, _, _, _, DAG, TIJD), DAG_TIJD = (DAG, TIJD).

duo(D1, D2, D, T) :- zitting(_, _, D1, D2, _, D, T).
duo(D1, D2, D, T) :- zitting(_, _, D2, D1, _, D, T).

% idee:
% zet duo's op volgorde zodat A, B en B, A niet als verschillend worden gezien
duo_zonder_dubbelen(D1, D2, D, T) :- duo(D1, D2, D, T), docentorder(D1, O1), docentorder(D2, O2), O1 > O2.

% aantal keer dat een duo voorkomt
aantal_duo(D1, D2, N) :- docent(D1), docent(D2), N = #count { (DAG, T) : duo_zonder_dubbelen(D1, D2, DAG, T) }.

% aantal niet unieke duo's. Alleen OF een niet uniek duo voorkomt. Als A, B 3 keer voorkomt telt dat als 1 niet unieke
niet_unieke_duo(N) :- N = #count { D1, D2 : aantal_duo(D1, D2, COUNT), COUNT > 1 }.

% aantal niet unieke duo's. Kijk ook naar hoe vaak het voorkomt. Als A, B 3 keer voorkomt telt dat als 2 niet unieke
%niet_unieke_duo(N) :- N = #sum { COUNT, D1, D2 : aantal_duo(D1, D2, COUNT), COUNT > 1 }.

% slechte combinaties worden gedefinieerd in Python (2 zittingen direct na elkaar, of juist 2x geen zitting ertussen)
aantal_slechte_combinaties(COUNT) :- COUNT = #count { DOCENT, D: bad_combination(T1, T2), zitting_moment(DOCENT, _, D, T1), zitting_moment(DOCENT, _, D, T2) }.

aantal_voorzitter_per_docent(VOORZITTER, N) :- docent(VOORZITTER), N = #count { AFSTUDEERDER : zitting(AFSTUDEERDER, _, VOORZITTER, _,_,_,_) }.
aantal_begeleider_per_docent(BEGELEIDER, N) :- docent(BEGELEIDER), N = #count { AFSTUDEERDER : zitting(AFSTUDEERDER, _, _, BEGELEIDER,_,_,_) }.

aantal_zitting_per_dag(DOCENT, D, N) :- docent(DOCENT), dag(D), N = #count { T : zitting_moment(DOCENT, _, D, T) }.
aantal_zitting_per_dag(BEDRIJF, D, N) :- bedrijfsbegeleider(BEDRIJF), dag(D), N = #count { T : zitting(_, BEDRIJF, _, _, _, D, T) }.

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
% bedrijfsbegeleider niet bij 2 zittingen (2 lokalen) tegelijkertijd
:- zitting(_, BEDRIJF, _, _, L1, D, T), zitting(_, BEDRIJF, _, _, L2, D, T), L1 != L2.

% expertise ontwikkelen moet bij elke zitting zijn
%:- not expertise_tijdens_zitting(A, ontwikkelen), afstudeerder(A).

% max 1 ontwikkelaar bij zitting
:- duo_zonder_dubbelen(D1, D2, _, _), expertise(D1, ontwikkelen),  expertise(D2, ontwikkelen).

% hoe vaak een specifiek duo maximaal voor mag komen
:- aantal_duo(D1, D2, N), N > 2.

% hoeveel niet unieke duo's voor mogen komen
:- niet_unieke_duo(COUNT), COUNT > 2.

% voorkom dubbele duo's
%:- duo_zonder_dubbelen(D1, D2, DAG1, T1), duo_zonder_dubbelen(D1, D2, DAG2, T2), (DAG1, T1) != (DAG2, T2).

% Voorkom zovaak mogelijk 2 zittingen achter elkaar of begin en eind van de dag
#minimize { COUNT: aantal_slechte_combinaties(COUNT) }.

% aantal keer dat een slechte combi mag
%:- aantal_slechte_combinaties(COUNT), COUNT > 1.

% Max aantal zittingen per dag voor een docent
:- aantal_zitting_per_dag(_, _, N), N > 2.

% #minimize { N : aantal_zitting_per_dag(_, _, N) }.



% #show zitting/7.

% #show aantal_voorzitter_per_docent/2.
% #show aantal_begeleider_per_docent/2.

% #show aantal_zitting_per_dag/3.

% #show max_aantal_zitting_per_dag/1.

% aantal_zitting_per_dag(dieuwertje,d1,3)



