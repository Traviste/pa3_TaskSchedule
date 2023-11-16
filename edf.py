from utils import ScheduleData, Task, ScheduleBlock, CLOCK_STATE_TO_FREQ_MAP, IDLE_STATE
from itertools import product
from math import gcd
from functools import reduce
import copy


def print_schedule_summary(data: ScheduleData, sched_vector: list[ScheduleBlock]):
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

        if sched_vector[i].frequency == IDLE_STATE:
            data.exec_time_used += 1

        last_block = sched_vector[i]

    data.idle_rate = (data.exec_time_used / data.exec_time)
    data.exec_time_used = data.exec_time - data.exec_time_used
    data.total_energy = compute_power_usage(sched_vector)

    print(
        f"Idle Rate = {data.idle_rate * 100.0} %\tTotal Energy = {data.total_energy} J\tExec Time Used = {data.exec_time_used} s")


def update_task_deadlines(current_time: int, data: ScheduleData):
    valid = True

    for t in data.tasks:
        if current_time == t.next_deadline:
            if t.time_remaining > 0:
                valid = False
            t.next_deadline = t.next_deadline + t.period
            t.time_remaining = t.wcet_by_clock_state[t.clock_state]

    return valid


def calculate_hyperperiod(tasks: list[Task]):
    periods = [task.period for task in tasks]
    return reduce((lambda a, b: a * b // gcd(a, b)), periods, 1)


def compute_power_usage(sched_vector: list[ScheduleBlock], n_iterations_inclusive=1000):
    power = 0.0

    for i, b in enumerate(sched_vector):
        if i == n_iterations_inclusive:
            break
        power += b.power_at_frequency

    return power / 1000.0


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


def find_optimal_edf_ee(base_data: ScheduleData):

    # Generate all possible combinations of clock states for the given tasks
    state_combinations = product(range(4), repeat=len(base_data.tasks))

    most_efficient: None or ScheduleData = None
    eff_vector: None or list[ScheduleBlock] = None

    h = calculate_hyperperiod(base_data.tasks)

    # Run every possible state
    for k, state in enumerate(state_combinations):
        # At this point we are trying to run 1 possible schedule
        data = copy.deepcopy(base_data)
        valid = True

        # Apply each combination of states to the tasks
        for i, task in enumerate(data.tasks):
            task.clock_state = state[i]

        sched_vector: list[ScheduleBlock] = []

        # Simulate the schedule
        for t in range(1, h + 1):
            # update deadlines based on current time
            valid = update_task_deadlines(t, data)

            if not valid:
                break

            earliest = find_earliest_incomplete_task(data)

            if earliest is not None:
                earliest.time_remaining = earliest.time_remaining - 1

                if t <= data.exec_time:
                    sched_vector.append(
                        ScheduleBlock(earliest.name, earliest.clock_state,
                                      data.power_by_clock_state[earliest.clock_state]))
            else:
                if t <= data.exec_time:
                    sched_vector.append(ScheduleBlock("IDLE", 4, data.power_by_clock_state[4]))

        if not valid:
            print(f"{k}\t : Invalid Schedule")
            continue

        data.total_energy = compute_power_usage(sched_vector, n_iterations_inclusive=1000)

        # Find schedule with least energy usage
        if most_efficient is None:
            most_efficient = data
            eff_vector = sched_vector
        elif most_efficient.total_energy > data.total_energy:
            most_efficient = data
            eff_vector = sched_vector

        print(f"{k}\t : Schedule Power = {data.total_energy} J")

    print_schedule_summary(most_efficient, eff_vector)
    print(f"Most Efficient Schedule Found!")
    print(f"Hyperperiod = {calculate_hyperperiod(most_efficient.tasks)} s")
    print(f"Power = {compute_power_usage(eff_vector)}")


def run_edf(data: ScheduleData):
    sched_vector: list[ScheduleBlock] = []
    valid = True

    for i in range(1, data.exec_time + 1):
        valid = update_task_deadlines(i, data)
        earliest = find_earliest_incomplete_task(data)

        if earliest is not None:
            earliest.time_remaining = earliest.time_remaining - 1

            sched_vector.append(
                ScheduleBlock(earliest.name, earliest.clock_state, data.power_by_clock_state[earliest.clock_state]))
        else:
            sched_vector.append(ScheduleBlock("IDLE", 4, data.power_by_clock_state[4]))

    print_schedule_summary(data, sched_vector)
    print(f"Valid ? = {valid}")
    print(f"Hyperperiod = {calculate_hyperperiod(data.tasks)} s")
    print(f"Power = {compute_power_usage(sched_vector)}")
