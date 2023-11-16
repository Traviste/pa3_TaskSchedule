import math
from utils import Task, ScheduleData, ScheduleBlock, CLOCK_STATE_TO_FREQ_MAP

def update_deadlines(current_time: int, data: ScheduleData):
    for t in data.tasks:
        if current_time >= t.next_deadline:
            t.next_deadline = t.next_deadline + t.period
            t.time_remaining = t.wcet_by_clock_state[t.clock_state]

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

    #create scheduling vector
    for current_time in range(0, hyperperiod):
        next_Task = next(data)
        if next_Task is not None:

            next_Task.time_remaining = next_Task.time_remaining - 1
        
            sched_vector.append(ScheduleBlock(next_Task.name, 0, data.power_by_clock_state[next_Task.clock_state]))
        else:
            sched_vector.append(ScheduleBlock("IDLE", 4, data.power_by_clock_state[4]))
        
        update_deadlines(current_time, data)

    last_block = sched_vector[0]
    time_count = 1
    time_started = 1
    energy_consumed = 0
    idle_time = 0
    
    #iterate through scheduling vector
    for i in range(1, len(sched_vector)):
        if (sched_vector[i].task_name == last_block.task_name) and i != (len(sched_vector) - 1):
            time_count = time_count + 1
        else:
            power_used = (last_block.power_at_frequency * time_count) / 1000.0
            print(f"{time_started}\t{last_block.task_name}\t"
                  f"{CLOCK_STATE_TO_FREQ_MAP[last_block.frequency]}\t{time_count}\t{power_used} J")
            energy_consumed += power_used
            if(last_block.task_name ==  "IDLE"):
                idle_time += time_count

            time_count = 1
            time_started = i + 1

        last_block = sched_vector[i]
    
    percent_idle = (idle_time/time_started) * 100
    print(f"Execution Time: {time_started}, Percent Idle Time: {percent_idle}%, Total Energy Consumption: {energy_consumed}J")