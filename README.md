# pa3_TaskSchedule
- PA3_TaskSchedule will take in an input file and parse the lines according to the number of tasks, execution time, active CPU power, and worst case execution times at different frequencies
- Based on the terminal call, the program will execute the indicated task schedule and print out the resulting output
- Any schedule call with the correlating EE will find the most optimal energy efficient schedule by finding possible combinations of task frequencies, checking for tasks meeting its deadlines, and checking for lowest power consumption.

## Run
To run the functions type the terminal command:
```
main.py <input_file_name> <EDF or RM> [EE]
```
For Example (running RM EE): "main.py input1.txt RM EE"