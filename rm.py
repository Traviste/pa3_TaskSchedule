from utils import ScheduleData, Task, ScheduleBlock, CLOCK_STATE_TO_FREQ_MAP, IDLE_STATE
from itertools import product
from math import gcd
from functools import reduce
import copy
from edf import print_schedule_summary, compute_power_usage, calculate_hyperperiod, find_earliest_incomplete_task

def update_deadlines(current_time: int, data: ScheduleData):
    valid = True
    for t in data.tasks:
        if current_time == t.next_deadline:
            if t.time_remaining > 0:
                valid = False
            t.next_deadline = t.next_deadline + t.period
            t.time_remaining = t.wcet_by_clock_state[t.clock_state]

    return valid

def next(data: ScheduleData):
    #prioritize by lowest period
    next_task: None or Task = None
    next_lowest_period = None

    for t in data.tasks:
        if(t.time_remaining > 0):
            if (next_task is None):
                next_task = t
            else:
                if (t.period < next_task.period):
                    next_task = t
        #for t in data.tasks:
            #if (t.period == next_lowest_period and t.time_remaining > 0):
            #    next_task = t
    
    return next_task
def find_optimal_rm_ee(base_data: ScheduleData):

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
            valid = update_deadlines(t, data)

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


def run_rm(data: ScheduleData):
    hyperperiod = data.exec_time
    sched_vector: list[ScheduleBlock] = []
    valid = True

    #create scheduling vector
    for current_time in range(1, hyperperiod+1):
        valid = update_deadlines(current_time, data)
        next_Task = next(data)

        if next_Task is not None:

            next_Task.time_remaining = next_Task.time_remaining - 1
        
            sched_vector.append(ScheduleBlock(next_Task.name, 0, data.power_by_clock_state[next_Task.clock_state]))
        else:
            sched_vector.append(ScheduleBlock("IDLE", 4, data.power_by_clock_state[4]))

    print_schedule_summary(data, sched_vector)
    print(f"Valid ? = {valid}")
    print(f"Hyperperiod = {calculate_hyperperiod(data.tasks)} s")
    print(f"Power = {compute_power_usage(sched_vector)}")