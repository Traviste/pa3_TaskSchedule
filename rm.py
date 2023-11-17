from utils import ScheduleData, ScheduleBlock, IDLE_STATE, print_schedule_summary
from itertools import product
import copy


# Run RM scheduler
def run_rm(data: ScheduleData):
    sched_valid = True

    # Simulate the schedule
    for t in range(1, data.exec_time + 1):
        # Update deadlines based on current time and check for deadline misses
        sched_valid = sched_valid and data.update_task_deadlines(t)
        # Get the next task by shortest Period
        next_task = data.next_incomplete_task_by_shortest_period()

        # If we have a new earliest task, run the task (-=1), and add it to the schedule, otherwise add an IDLE
        if next_task is not None:
            next_task.time_remaining -= 1
            data.sched_vector.append(
                ScheduleBlock(next_task.name, next_task.clock_state, data.power_by_clock_state[next_task.clock_state]))
        else:
            data.sched_vector.append(ScheduleBlock("IDLE", 4, data.power_by_clock_state[4]))

    # Print summary and show if it is valid
    print_schedule_summary(data, data.sched_vector)
    print(f"Valid RM Schedule up to {data.exec_time} s ? = {sched_valid}")
    if not sched_valid:
        print("NOTE: SCHEDULE IS INVALID, DEADLINE MISSED")


# Run RM EE optimizer
def find_optimal_rm_ee(base_data: ScheduleData):
    # Generate all possible combinations of clock states for the given tasks
    state_combinations = product(range(4), repeat=len(base_data.tasks))

    most_efficient: None or ScheduleData = None
    h = base_data.calculate_hyperperiod()

    # For every possible state
    for k, state in enumerate(state_combinations):
        # At this point we are trying to run 1 possible schedule
        data: ScheduleData = copy.deepcopy(base_data)
        sched_valid = True

        # Apply each combination of states to the tasks
        for i, task in enumerate(data.tasks):
            task.clock_state = state[i]
            task.time_remaining = task.wcet_by_clock_state[task.clock_state]

        # Simulate the schedule
        for t in range(1, h + 1):
            # Update deadlines based on current time and check for deadline misses
            sched_valid = sched_valid and data.update_task_deadlines(t)

            # If we have a deadline miss, schedule is invalid so break
            if not sched_valid:
                break

            # Find the next task by shortest period
            earliest = data.next_incomplete_task_by_shortest_period()

            # If we have a new earliest task, run the task and add it to the schedule
            if earliest is not None:
                earliest.time_remaining -= 1
                data.total_energy += data.power_by_clock_state[earliest.clock_state]

                data.sched_vector.append(
                    ScheduleBlock(earliest.name, earliest.clock_state, data.power_by_clock_state[earliest.clock_state])
                )
            else:
                data.total_energy += data.power_by_clock_state[IDLE_STATE]
                data.sched_vector.append(ScheduleBlock("IDLE", IDLE_STATE, data.power_by_clock_state[IDLE_STATE]))

        if not sched_valid:
            print(f"{k}\t : Invalid Schedule")
            continue

        # data.total_energy = compute_power_usage(sched_vector, n_iterations_inclusive=1000)
        data.total_energy = data.total_energy / 1000.0

        # Find schedule with the least energy usage
        if most_efficient is None:
            most_efficient = data
        elif most_efficient.total_energy > data.total_energy:
            most_efficient = data

        print(f"{k}\t : Schedule Energy (across hyperperiod {h}) = {data.total_energy} J")

    if most_efficient is not None:
        print_schedule_summary(most_efficient, most_efficient.sched_vector)
        print(f"\nValid RM EE Schedule Found!")
        print(f"Most Efficient Schedule Total Energy = {most_efficient.total_energy} J")
    else:
        print("NO VALID RM EE SCHEDULES FOUND")
