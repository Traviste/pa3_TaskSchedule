from utils import ScheduleData, Task


def update_task_deadlines(current_time: int, data: ScheduleData):
    for t in data.tasks:
        if current_time >= t.next_deadline:
            t.next_deadline = t.next_deadline + t.period
            t.percent_complete = 0.0
            t.complete = False


def find_earliest_incomplete_task(data: ScheduleData):
    earliest: None or Task = None

    for t in data.tasks:
        if not t.complete:
            if earliest is None:
                earliest = t
            else:
                if t.next_deadline < earliest.next_deadline:
                    earliest = t

    return earliest


def run_edf(data: ScheduleData):
    vector = []

    for i in range(0, data.exec_time):
        earliest = find_earliest_incomplete_task(data)

        if earliest is not None:
            earliest.percent_complete += 1.0 / earliest.wcet_by_clock_state[0]

            if earliest.percent_complete >= 1.0:
                earliest.percent_complete = 1.0
                earliest.complete = True

            print(earliest)
        else:
            print("IDLE")

        update_task_deadlines(i, data)
