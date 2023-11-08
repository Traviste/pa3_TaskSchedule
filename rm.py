import math
from utils import Task, ScheduleData, ScheduleBlock, CLOCK_STATE_TO_FREQ_MAP

def next(data: ScheduleData):
    #prioritize by lowest period
    next_lowest_period = None
    next_period = None
    for t in data.tasks:
        if next_lowest_period == None:
            next_lowest_period = t.period
        else:
            if (t.complete == False and t.period < next_lowest_period):
                next_period = t
    
    return next_period

def rm_schedule(data: ScheduleData):
    hyperperiod = data.exec_time
    sched_vector: list[ScheduleBlock] = []

    #create scheduling vector
    for current_time in range(0, hyperperiod):
        next_Task = next(data)
        if next_Task is not None:
            next_Task.complete = 1.0/next_Task.wcet_by_clock_state[0]

            if next_Task.complete >= 1.0:
                next_Task.percent_complete = 1
                next_Task.complete = True

            sched_vector.append(ScheduleBlock(next_Task.name, next_Task.power_by_clock_state[0], idle = False))
            print("Append block Task")
        else:
            sched_vector.append(ScheduleBlock("IDLE", next_Task.power_by_clock_state[4], idle = True))
            print("Append Block Idle")
        
        for t in data.tasks:
            if current_time >= t.next_deadline:
                t.next_deadline = t.period + current_time
                t.complete = False
                t.complete = 0.0

    #iterate through scheduling vector

#print(f'{current_time} {data.task[0].name} {data.CPU frequency} {how long it ran for} {energy consumed in joules}J)
