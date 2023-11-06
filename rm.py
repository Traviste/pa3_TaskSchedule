import math
from utils import Task, ScheduleData, parse_input_file

def rm_schedule(data: ScheduleData):
    for i in range(1, data.task_count):
        hyperperiod = data.tasks[0].period
        hyperperiod = math.lcm(hyperperiod, data.tasks[0].period)

    current_time = 0
    for i in range(0, hyperperiod):
        
    
    #print(f'{time started} {task name} {CPU frequency} {how long it ran for} {energy consumed in joules}J)


def rm_scheduleEE(data: ScheduleData):
    for i in range(1, data.task_count):
        hyperperiod = data.tasks[0].period
        hyperperiod = math.lcm(hyperperiod, data.tasks[0].period)

    current_time = 0