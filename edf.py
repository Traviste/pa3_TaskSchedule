from utils import ScheduleData, Task, ScheduleBlock, CLOCK_STATE_TO_FREQ_MAP


def update_task_deadlines(current_time: int, data: ScheduleData):
    for t in data.tasks:
        if current_time >= t.next_deadline:
            t.next_deadline = t.next_deadline + t.period
            t.time_remaining = t.wcet_by_clock_state[t.clock_state]


def find_earliest_incomplete_task(data: ScheduleData):
    earliest: None or Task = None

    for t in data.tasks:
        if t.time_remaining > 0:
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
            earliest.time_remaining = earliest.time_remaining - 1

            sched_vector.append(ScheduleBlock(earliest.name, 0, data.power_by_clock_state[earliest.clock_state]))
        else:
            sched_vector.append(ScheduleBlock("IDLE", 4, data.power_by_clock_state[4]))

        update_task_deadlines(i, data)

    last_block = sched_vector[0]
    time_count = 1
    time_started = 1

    for i in range(1, len(sched_vector)):
        if (sched_vector[i].task_name == last_block.task_name) and i != (len(sched_vector) - 1):
            time_count = time_count + 1
        else:
            power_used = (last_block.power_at_frequency * time_count) / 1000.0
            print(f"{time_started}\t{last_block.task_name}\t"
                  f"{CLOCK_STATE_TO_FREQ_MAP[last_block.frequency]}\t{time_count}\t{power_used} J")

            time_count = 1
            time_started = i + 1

        last_block = sched_vector[i]
