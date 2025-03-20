import time
from collections import defaultdict

import pandas as pd
import re
import numpy as np
from clorm import Predicate, ConstantStr
from clorm import FactBase
from clorm.clingo import Control
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import Border, Side, Alignment


# Define unifiers for predicates
class Afstudeerder(Predicate):
    name: ConstantStr


class Docent(Predicate):
    name: ConstantStr


class Docentorder(Predicate):
    name: ConstantStr
    prio: int


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

# Define solution model
class Zitting(Predicate):
    student: ConstantStr
    coach: ConstantStr
    teacher1: ConstantStr
    teacher2: ConstantStr
    room: ConstantStr
    date: ConstantStr
    time: ConstantStr

class Zitting_required(Predicate):
    student: ConstantStr
    coach: ConstantStr
    teacher: ConstantStr


class Max_aantal_zitting_per_dag(Predicate):
    n: int

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

days_order = []
timeslotes_order = []

# Assumption: same number of rooms available each day
rooms = [f"room{i}" for i in range(1)]

rooms_order = rooms.copy()

availability = defaultdict(set)

zitting_constraints = []

people_constraints = set()

def show_schedule(schedule):
    # sort
    schedule.sort(key=lambda x: x["order"])

    df = pd.DataFrame(schedule)
    df = df.drop(columns=["order"])
    # # print(df)


    # Save to Excel first
    file_path = "schedule.xlsx"
    df.to_excel(file_path, index=False, engine='openpyxl')

    # Load the workbook and sheet
    wb = load_workbook(file_path)
    ws = wb.active

    # Adjusting column widths automatically based on the content
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)  # Add some padding
        ws.column_dimensions[column].width = adjusted_width

    # Save the Excel file with adjusted column widths
    wb.save(file_path)

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
        if timeslot not in timeslots:
            timeslots.add(timeslot)
            timeslotes_order.append(timeslot)

        for day, available in data.items():
            pattern = r"^[A-Za-z]+ \d{1,2} [A-Za-z]+$"
            # extract (valid) days
            if re.match(pattern, day):
                if day not in days:
                    days.add(day)
                    days_order.append(day)
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
            assert total_matches > 0, f"availability for {coach} does not match any of the other teachers"

        students.add(student)

        coach_student.append((coach, student))
        teacher_student.append((teacher, student))
        teacher_coach.append((teacher, coach))

        # add zitting to answer set
        zitting_constraints.append(Zitting_required(student=student, coach=coach, teacher=teacher))

        people_constraints.add((student, coach, teacher))

    print(zitting_constraints)

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



    # Create predicates from data
    instance_data = []
    instance_data += zitting_constraints

    instance_data += [Afstudeerder(name=n) for n in students]
    instance_data += [Docent(name=n) for n in teachers]
    instance_data += [Docentorder(name=n, prio=p) for p, n in enumerate(teachers)]
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

    restrict_empty_rooms = [f":- zitting(_, _, _, _, {rooms[i]}, D, T), not zitting(_, _, _, _, {rooms[i-1]}, D, T)." for i in range(1, len(rooms))]

    restrict_orders = [f":- zitting(_, _, _, B1, {rooms[i - 1]}, D, T), zitting(_, _, _, B2, {rooms[i]}, D, T), docent(B1), docent(B2), docentorder(B1, O1), docentorder(B2, O2), O1 > O2." for i in range(1, len(rooms))]

    instance = FactBase(instance_data)




    # Connect to clingo
    ctrl = Control(["0"], unifier=[Afstudeerder, Docent, Docentorder, Expertise, Begeleider, Coach, Bedrijfsbegeleider, Expertise, Tijdslot, Dag, Lokaal, Zitting, Zitting_required, Max_aantal_zitting_per_dag])
    ctrl.load("afstudeerplanning.lp")

    ctrl.add_facts(instance)

    for restrict_empty_room in restrict_empty_rooms:
        ctrl.add("base", [], restrict_empty_room)

    for restrict_order in restrict_orders:
        ctrl.add("base", [], restrict_order)

    ctrl.ground([("base", [])])

    start_time = time.time()
    count = 0
    with ctrl.solve(yield_=True) as handle:
        solution_found = False
        for model in handle:
            count += 1
            if count > 1:
                continue

            solution_found = True
            print("solution found")
            solution = model.facts(atoms=True)

            print(solution)

            query = solution.query(Max_aantal_zitting_per_dag)
            max_zittingen = list(query.all())
            print(f"Maximum per teacher per day: {max_zittingen[0].n}")

            query = solution.query(Zitting)
            moments = list(query.all())
            schedule = []
            for moment in moments:
                # print("===================================================")
                # print(f"{moment.date} {moment.time} ({moment.room})")
                # print(f"{moment.student} ({moment.coach})")
                # print(f"Voorzitter: {moment.teacher1} - expertise: {teacher_expertise[moment.teacher1]}")
                # print(f"Begeleider: {moment.teacher2} - expertise: {teacher_expertise[moment.teacher2]}")

                assert (moment.date, moment.time) in availability[moment.teacher1], f"wrong assignment for {moment.teacher1}"
                assert (moment.date, moment.time) in availability[moment.teacher2], f"wrong assignment for {moment.teacher2}"
                assert (moment.date, moment.time) in availability[moment.coach], f"wrong assignment for {moment.coach}"

                assert (moment.student, moment.coach, moment.teacher2) in people_constraints, f"wrong people selection: {(moment.student, moment.coach, moment.teacher2)}"

                schedule.append({
                    "dag": moment.date,
                    "tijdslot": moment.time,
                    "lokaal": moment.room,
                    "student": moment.student,
                    "bedrijfsbegeleider": moment.coach,
                    "voorzitter": moment.teacher1,
                    "begeleider": moment.teacher2,
                    "order": (days_order.index(moment.date), timeslotes_order.index(moment.time), rooms_order.index(moment.room))
                })

            print()
            print(f"Running time: {time.time() - start_time}")
            print()
            show_schedule(schedule)
            # exit()
        print(f"Number of solutions {count}")
        print(f"Running time: {time.time() - start_time}")

        if not solution_found:
            print("No solution possible")

