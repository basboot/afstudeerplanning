from collections import defaultdict

import pandas as pd
import re
import numpy as np

teacher_availability_file = "BeschikbaarheidDocentenJuli25.xlsx"

# Assumption: teacher names are unique
teachers = set()

# Assumption: timeslots are the same on each day
timeslots = set()
days = set()

# Assumption: same number of rooms available each day
rooms = [f"room{i}" for i in range(3)]


availability = defaultdict(set)

if __name__ == '__main__':
    # Read Excel
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
            pattern = r"^[A-Za-z]{2} \d{1,2} [A-Za-z]+$"
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



