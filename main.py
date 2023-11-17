import sys
from utils import parse_input_file
from edf import run_edf, find_optimal_edf_ee
from rm import run_rm, find_optimal_rm_ee

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Wrong number of args:\n"
              "main.py <input_file_name> <EDF or RM> [EE]")
        exit()

    # Get filename and scheduler to use
    fn = sys.argv[1]
    sched_type = sys.argv[2].lower()

    # Check if using energy efficient scheduling
    ee = False
    if len(sys.argv) == 4:
        ee = True

    sched_data = parse_input_file(fn)

    # Run scheduler
    if sched_type == "rm" and ee is False:
        print("Using RM")
        run_rm(sched_data)
    elif sched_type == "rm" and ee:
        print("Using EE-RM")
        find_optimal_rm_ee(sched_data)
    elif sched_type == "edf" and ee is False:
        print("Using EDF")
        run_edf(sched_data)
    elif sched_type == "edf" and ee:
        print("Using EE-EDF")
        find_optimal_edf_ee(sched_data)
    else:
        print("No matching scheduler found:\n"
              "main.py <input_file_name> <EDF or RM> [EE]")

