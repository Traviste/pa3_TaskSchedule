import sys
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


def parse_input_file(filename):
    with open(filename, 'r') as f:
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


if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(len(sys.argv))
        print("Wrong number of args:\n"
              "main.py <input_file_name> <EDF or RM> [EE]")
        exit()

    # Get filename and scheduler to use
    fn = sys.argv[1]
    sched_type = sys.argv[2]

    # Check if using energy efficient scheduling
    ee = False
    if len(sys.argv) == 4:
        ee = True

    if sched_type == "RM" and ee is False:
        print("Using RM")
    elif sched_type == "RM" and ee is True:
        print("Using EE-RM")
    elif sched_type == "EDF" and ee is False:
        print("Using EDF")
    elif sched_type == "EDF" and ee is True:
        print("Using EE-EDF")

    parse_input_file(fn)
