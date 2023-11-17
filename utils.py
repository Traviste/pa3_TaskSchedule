from dataclasses import dataclass, field
from math import gcd
from functools import reduce

# In MHz
CLOCK_STATE_TO_FREQ_MAP = ["1188", "918", "648", "384", "IDLE"]
IDLE_STATE = 4


@dataclass
class ScheduleBlock:
    task_name: str
    frequency: int
    power_at_frequency: int


@dataclass
class Task:
    # Read from simulation input
    name: str
    period: int
    wcet_by_clock_state: list[int]

    # Schedule Specific
    time_remaining: int = 0
    next_deadline: int = 0
    clock_state: int = 0


@dataclass
class ScheduleData:
    task_count: int
    exec_time: int
    power_by_clock_state: list[int]
    tasks: list[Task]

    total_energy: float = 0.0
    idle_rate: float = 0.0
    exec_time_used: int = 0
    sched_vector: list[ScheduleBlock] = field(default_factory=list)

    # Update each task's deadline tracking, and return if the schedule has missed any deadlines (is valid)
    def update_task_deadlines(self, current_time: int):
        valid = True

        for t in self.tasks:
            if current_time == t.next_deadline:
                if t.time_remaining > 0:
                    valid = False
                t.next_deadline = t.next_deadline + t.period
                t.time_remaining = t.wcet_by_clock_state[t.clock_state]

        return valid

    # Find the task with the earliest deadline
    def next_incomplete_task_by_earliest_deadline(self):
        earliest: None or Task = None

        for task in self.tasks:
            # If the task is incomplete
            if task.time_remaining > 0:
                if earliest is None:
                    earliest = task
                elif task.next_deadline < earliest.next_deadline:
                    earliest = task

        return earliest

    def next_incomplete_task_by_shortest_period(self):
        # Prioritize by lowest period
        next_task: None or Task = None

        for t in self.tasks:
            if t.time_remaining > 0:
                if next_task is None:
                    next_task = t
                elif t.period < next_task.period:
                    next_task = t

        return next_task

    # Calc hyperperiod of task set
    def calculate_hyperperiod(self):
        periods = [task.period for task in self.tasks]
        return reduce((lambda a, b: a * b // gcd(a, b)), periods, 1)


# parse file function
def parse_input_file(filename) -> ScheduleData:
    with open(filename, 'r', encoding='utf-8') as f:
        line = f.readline().strip().split(" ")
        task_count = int(line[0])
        exec_time = int(line[1])
        clock_state_power = [int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])]
        tasks: list[Task] = []

        for i, line in enumerate(f):
            line = line.strip().split(" ")
            tasks.append(
                Task(line[0],
                     int(line[1]),
                     [int(line[2]), int(line[3]), int(line[4]), int(line[5])],
                     next_deadline=int(line[1]), time_remaining=int(line[2])
                     )
            )

    data = ScheduleData(task_count, exec_time, clock_state_power, tasks)
    return data


# Print schedule summary
def print_schedule_summary(data: ScheduleData, sched_vector: list[ScheduleBlock], n=1000):
    last_block = sched_vector[0]
    energy = last_block.power_at_frequency

    # Keep track of how long a task runs for and what time it starts at
    time_count = 1
    time_started = 1

    # Compute the endpoint for how long we should summarize schedule for
    endpoint = min(len(sched_vector), n)

    # Go through each schedule block and print summary when block changes.
    for i in range(1, endpoint):
        energy += sched_vector[i].power_at_frequency

        if (sched_vector[i].task_name == last_block.task_name) and i != (endpoint - 1):
            time_count = time_count + 1
        else:
            # If we are at this block, we have reached a block transition, so print and reset
            power_used = (last_block.power_at_frequency * time_count) / 1000.0

            print(f"{time_started}\t{last_block.task_name}\t"
                  f"{CLOCK_STATE_TO_FREQ_MAP[last_block.frequency]}\t"
                  f"{time_count}\t{power_used} J")

            time_count = 1
            time_started = i + 1

        # If we are IDLE, increment exec_time_used ( this is used to keep track of idle time at this point)
        if sched_vector[i].frequency == IDLE_STATE:
            data.exec_time_used += 1

        last_block = sched_vector[i]

    # Compute idle rate and used exec time
    data.idle_rate = (data.exec_time_used / endpoint)
    data.exec_time_used = endpoint - data.exec_time_used

    # Print statistics
    print(f"Statistics for First {endpoint} s:")
    print(
        f"Idle Rate = {data.idle_rate * 100.0} %\tTotal Energy = {energy / 1000.0} J\t"
        f"Exec Time Used = {data.exec_time_used} s")
