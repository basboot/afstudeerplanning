from collections import defaultdict

import pandas as pd
import re
import numpy as np
from clorm import Predicate, ConstantStr

teacher_availability_file = "BeschikbaarheidDocentenJuli25.xlsx"
coach_availability_file = "Beschikbaarheid bedrijfsbegeleider.xlsx"
teacher_student_coach_file = "Afstudeerders 2024-2025.xlsx"

# Assumption: teacher names are unique
teachers = set()
coaches = set()

# Assumption: timeslots are the same on each day
timeslots = set()
days = set()

# Assumption: same number of rooms available each day
rooms = [f"room{i}" for i in range(3)]

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
            print("skip until teach found")
            continue

        timeslot = data['Tijdslot']
        timeslots.add(timeslot)

        for day, available in data.items():
            print(day)
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

        print(coach)

        for day, available in data.items():
            day = day.replace(" beschikbaar op:", "")
            print(day)
            pattern = r"^[A-Za-z]+ \d{1,2} [A-Za-z]+$"
            # extract (valid) days
            if re.match(pattern, day):
                assert day in days, f"Illegal day {day} in coach availability"
                for timeslot in available.split(";"):
                    if timeslot == "" or timeslot == "Niet":
                        continue # only process available slots
                    assert timeslot in timeslots, f"Illegal timeslot {timeslot} in coach availability"
                    print(timeslot)

                    availability[coach].add((day, timeslot))

    # Students + connections
    df = pd.read_excel(teacher_student_coach_file).replace(np.nan, '')


    teacher_student = []
    teacher_coach = []
    coach_student = []

    students = set()
    coaches = set()

    print(teachers)

    for i in range(df.shape[0]):
        data = df.iloc[i].to_dict()

        teacher = data['Afstudeerbegeleider']
        coach = data['Bedrijfsbegeleider']
        student = data['Voornaam student'] + " " + data['Achternaam']

        assert teacher in teachers, f"{teacher} unknown"
        # TODO: ignore until we have all data
        # assert coach in coaches, f"{coach} unknown"

        coaches.add(coach)
        students.add(student)

        coach_student.append((coach, student))
        teacher_student.append((teacher, student))
        teacher_coach.append((teacher, coach))


    print(availability)
    print(f"#timeslots: {len(timeslots)}")
    print(f"#days: {len(days)}")
    print(f"#students: {len(students)}")
    print(f"#coaches: {len(coaches)}")

