from dataclasses import dataclass

# In MHz
CLOCK_STATE_TO_FREQ_MAP = [1188, 918, 648, 384, 0]


@dataclass
class Task:
    name: str
    period: int
    wcet_by_clock_state: list[int]


@dataclass
class ScheduleData:
    task_count: int
    exec_time: int
    power_by_clock_state: list[int]
    tasks: list[Task]


# parse file function
def parse_input_file(filename) -> ScheduleData:
    with open(filename, 'r', encoding='utf-8') as f:
        line = f.readline().strip().split(" ")
        task_count = int(line[0])
        exec_time = int(line[1])
        clock_state_power = [int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6])]
        tasks = []

        for i, line in enumerate(f):
            line = line.strip().split(" ")
            tasks.append(Task(line[0], int(line[1]), [int(line[2]), int(line[3]), int(line[4]), int(line[5])]))

    data = ScheduleData(task_count, exec_time, clock_state_power, tasks)
    return data