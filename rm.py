from utils import ScheduleData, Task, ScheduleBlock, CLOCK_STATE_TO_FREQ_MAP, IDLE_STATE
from itertools import product
from math import gcd
from functools import reduce
import copy
from edf import print_schedule_summary, compute_power_usage, calculate_hyperperiod

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
    next_lowest_period = None
    next_task = None
    for t in data.tasks:
        if next_lowest_period == None:
            next_lowest_period = t.period
        else:
            if (t.time_remaining > 0 and t.period < next_lowest_period):
                next_lowest_period = t.period    

    for t in data.tasks:
        if(t.period == next_lowest_period and t.time_remaining > 0):
            next_task = t
            return next_task

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