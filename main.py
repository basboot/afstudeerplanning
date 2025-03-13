from collections import defaultdict

import pandas as pd
import re
import numpy as np
from clorm import Predicate, ConstantStr
from clorm import FactBase
from clorm.clingo import Control

DEBUG = True

teacher_availability_file = "BeschikbaarheidDocentenJuli25.xlsx"
coach_availability_file = "Beschikbaarheid bedrijfsbegeleider.xlsx"
teacher_student_coach_file = "Afstudeerders 2024-2025.xlsx"
teacher_expertise_file = "Expertises.xlsx"

# Assumption: teacher names are unique
teachers = set()
coaches = set()

# Assumption: timeslots are the same on each day
timeslots = set()
days = set()

# Assumption: same number of rooms available each day
rooms = [f"room{i}" for i in range(2)]

availability = defaultdict(set)

if __name__ == '__main__':
    # Read data from Excel files

    # Teacher availability
    df = pd.read_excel(teacher_availability_file).replace(np.nan, '')

    teacher = ""
    for i in range(df.shape[0]):
        data = df.iloc[i].to_dict()

        if data['Docent'] != "":
            teacher = data['Docent']
            teachers.add(teacher)
        if teacher == "":
            continue # skip first line

        timeslot = data['Tijdslot']
        timeslots.add(timeslot)

        for day, available in data.items():
            pattern = r"^[A-Za-z]+ \d{1,2} [A-Za-z]+$"
            # extract (valid) days
            if re.match(pattern, day):
                days.add(day)
                match(available):
                    case "v":
                        availability[teacher].add((day, timeslot))
                    case "x":
                        pass
                    case _:
                        assert False, f"Illegal input {teacher} {day} {timeslot}"

    # Coach availability
    df = pd.read_excel(coach_availability_file).replace(np.nan, '')

    for i in range(df.shape[0]):
        data = df.iloc[i].to_dict()

        coach = data['Voornaam'] + " " + data['Achternaam']
        coaches.add(coach)
        if DEBUG:
            print(f"INFO: reading availability for {coach}")

        for day, available in data.items():
            day = day.replace(" beschikbaar op:", "")
            pattern = r"^[A-Za-z]+ \d{1,2} [A-Za-z]+$"
            # extract (valid) days
            if re.match(pattern, day):
                assert day in days, f"Illegal day {day} in coach availability"
                for timeslot in available.split(";"):
                    if timeslot == "" or timeslot == "Niet":
                        continue # only process available slots
                    assert timeslot in timeslots, f"Illegal timeslot {timeslot} in coach availability"

                    availability[coach].add((day, timeslot))

    # Students + connections
    df = pd.read_excel(teacher_student_coach_file, sheet_name='Sem. 2').replace(np.nan, '')

    teacher_student = []
    teacher_coach = []
    coach_student = []

    students = set()

    for i in range(df.shape[0]):
        data = df.iloc[i].to_dict()
        # print(data)

        teacher = data['Afstudeerbegeleider']
        coach = data['Bedrijfsbegeleider']
        student = data['Voornaam student'] + " " + data['Achternaam']

        assert teacher in teachers, f"{teacher} unknown"

        # coach can be a teacher
        if coach in teachers:
            coaches.add(coach)

        if DEBUG:
            pass
            if coach not in coaches:
                print(f"WARNING: availability for {coach} unknown, cannot plan for student {student}")
                continue
        else:
            assert coach in coaches, f"{coach} unknown"

        # reduce availability of coach, to moments the teacher is also available
        availability[coach] = availability[coach].intersection(availability[teacher])

        if DEBUG:
            if len(availability[coach]) == 0:
                print(f"ERROR: availability for {teacher} and {coach} does not match, not planning for student {student}")
                continue
            else:
                print(f"INFO: availability for {teacher} and {coach} at { len(availability[coach]) } timeslots for student {student}")
        else:
            assert len(availability[coach]) > 0, f"availability for {teacher} and {coach} does not match"

        total_matches = 0
        for teacher2 in teachers:
            if teacher == teacher2:
                continue # skip self
            total_matches += len(availability[coach].intersection(availability[teacher2]))

        if DEBUG:
            if total_matches == 0:
                print(f"ERROR: availability for {coach} does not match any of the other teachers, not planning for student {student}")
                continue
            else:
                print(
                    f"INFO: availability for {teacher} and {coach} at {len(availability[coach])} timeslots for student {student}")
        else:
            assert total_matches > 0, f"availability for {coach} does not match any of the other teachers"

        students.add(student)

        coach_student.append((coach, student))
        teacher_student.append((teacher, student))
        teacher_coach.append((teacher, coach))

    print(f"rooms: {len(rooms)}")
    print(f"days: {len(days)}")
    print(f"timeslots: {len(timeslots)}")
    print(f"teachers: {len(teachers)}")
    print(f"students: {len(students)}")
    print(f"coaches: {len(coaches)}")

    teacher_expertise = {}
    df = pd.read_excel(teacher_expertise_file).replace(np.nan, '')
    for i in range(df.shape[0]):
        data = df.iloc[i].to_dict()

        teacher = data['Naam']
        expertise = data['Expertise']
        teacher_expertise[teacher] = expertise

    # Define unifiers for predicates
    class Afstudeerder(Predicate):
        name: ConstantStr

    class Docent(Predicate):
        name: ConstantStr

    class Begeleider(Predicate):
        name: ConstantStr
        student: ConstantStr

    class Coach(Predicate):
        name: ConstantStr
        student: ConstantStr

    class Bedrijfsbegeleider(Predicate):
        name: ConstantStr

    class Expertise(Predicate):
        name: ConstantStr
        type: ConstantStr

    class Tijdslot(Predicate):
        time: ConstantStr

    class Dag(Predicate):
        date: ConstantStr

    class Lokaal(Predicate):
        room: ConstantStr

    class Beschikbaar(Predicate):
        name: ConstantStr
        date: ConstantStr
        time: ConstantStr

    # Create predicates from data
    instance_data = []

    instance_data += [Afstudeerder(name=n) for n in students]
    instance_data += [Docent(name=n) for n in teachers]
    instance_data += [Expertise(name=n, type=teacher_expertise[n]) for n in teachers]
    instance_data += [Begeleider(name=n, student=s) for n, s in teacher_student]
    instance_data += [Coach(name=n, student=s) for n, s in coach_student]
    instance_data += [Bedrijfsbegeleider(name=n) for n in coaches]
    instance_data += [Tijdslot(time=t) for t in timeslots]
    instance_data += [Dag(date=d) for d in days]
    instance_data += [Lokaal(room=r) for r in rooms]

    for person, available in availability.items():
        instance_data += [Beschikbaar(name=person, date=d, time=t) for d, t in available]

    print(instance_data)

    instance = FactBase(instance_data)

    # Define solution model
    class Zitting(Predicate):
        student: ConstantStr
        coach: ConstantStr
        teacher1: ConstantStr
        teacher2: ConstantStr
        room: ConstantStr
        date: ConstantStr
        time: ConstantStr


    class Max_aantal_zitting_per_dag(Predicate):
        n: int


    # Connect to clingo
    ctrl = Control(["0"], unifier=[Afstudeerder, Docent, Expertise, Begeleider, Coach, Bedrijfsbegeleider, Expertise, Tijdslot, Dag, Lokaal, Zitting, Max_aantal_zitting_per_dag])
    ctrl.load("afstudeerplanning.lp")

    ctrl.add_facts(instance)
    ctrl.ground([("base", [])])


    with ctrl.solve(yield_=True) as handle:
        solution_found = False
        for model in handle:
            solution_found = True
            print("solution found")
            solution = model.facts(atoms=True)

            print(solution)

            query = solution.query(Max_aantal_zitting_per_dag)
            max_zittingen = list(query.all())
            print(f"Maximum per teacher per day: {max_zittingen[0].n}")

            query = solution.query(Zitting)
            moments = list(query.all())
            for moment in moments:
                print("===================================================")
                print(f"{moment.date} {moment.time} ({moment.room})")
                print(f"{moment.student} ({moment.coach})")
                print(f"Voorzitter: {moment.teacher1} - expertise: {teacher_expertise[moment.teacher1]}")
                print(f"Begeleider: {moment.teacher2} - expertise: {teacher_expertise[moment.teacher2]}")

                assert (moment.date, moment.time) in availability[moment.teacher1], f"wrong assignment for {moment.teacher1}"
                assert (moment.date, moment.time) in availability[moment.teacher2], f"wrong assignment for {moment.teacher2}"
                assert (moment.date, moment.time) in availability[moment.coach], f"wrong assignment for {moment.coach}"




            print()
            print()
            exit()

        if not solution_found:
            print("No solution possible")

