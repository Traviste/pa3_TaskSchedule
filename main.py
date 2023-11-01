import sys
from utils import Task, ScheduleData, parse_input_file

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
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

    sched_data = parse_input_file(fn)
    print(sched_data)

    if sched_type == "RM" and ee is False:
        print("Using RM")
    elif sched_type == "RM" and ee is True:
        print("Using EE-RM")
    elif sched_type == "EDF" and ee is False:
        print("Using EDF")
    elif sched_type == "EDF" and ee is True:
        print("Using EE-EDF")

