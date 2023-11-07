from utils import ScheduleData, Task, ScheduleBlock, CLOCK_STATE_TO_FREQ_MAP


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
    sched_vector: list[ScheduleBlock] = []

    for i in range(0, data.exec_time):
        earliest = find_earliest_incomplete_task(data)

        if earliest is not None:
            earliest.percent_complete += 1.0 / earliest.wcet_by_clock_state[0]

            if earliest.percent_complete >= 1.0:
                earliest.percent_complete = 1.0
                earliest.complete = True

            sched_vector.append(ScheduleBlock(earliest.name, 0, data.power_by_clock_state[0], idle=False))
        else:
            sched_vector.append(ScheduleBlock("IDLE", 4, data.power_by_clock_state[4], idle=True))

        update_task_deadlines(i, data)

    last_block = sched_vector[0]
    time_count = 0
    time_started = 0

    for i in range(1, len(sched_vector)):
        if sched_vector[i].task_name == last_block.task_name:
            time_count = time_count + 1
        else:
            print(f"{time_started}\t{last_block.task_name}\t{CLOCK_STATE_TO_FREQ_MAP[last_block.frequency]}\t{time_count}\t{1}")

            time_count = 0
            time_started = i

        last_block = sched_vector[i]
