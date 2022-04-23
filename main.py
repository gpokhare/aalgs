"""
@Date: 04/22/2022
@Author: Gaurab Pokharel (gpokhare@gmu.edu)

Description:
Main file for running experiments
"""


##TODO
# ""continue"" instead of resetting seed if you already find a run-data in location

import argparse
# Function that gets arguments from the command line for running the experiments
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizon", help="Number of time steps to run experiment for", metavar="t")
    parser.add_argument("--running_on", help="0 for windows, 1 for mac, 2 for linux", metavar="X")
    parser.add_argument("--num_runs", help="Number of runs to execute", metavar="N")
    parser.add_argument("--lambda", help="Value of Lambda for the experiment", metavar="L")
    parser.add_argument("--use_thompson", help="Turn on to use Thompson Sampling for rewards ", action="store_true")
    parser.add_argument("--run_random", help="Turn on to run random market of varying sizes", action="store_true")
    parser.add_argument("--run_varied", help="Turn on to run markets with varying pref. homogeniety", action="store_true")
    parser.add_argument("-l", "--log_results", help="Turn on to log experiment", action="store_true")
    args = parser.parse_args()

    return args



def main():
    args = get_arguments()

    if args.running_on == '0':
        print("Windows")
    elif args.running_on == '1':
        print("Mac")
    elif args.running_on == '2':
        print("Linux")

    if args.run_random:
        print("running random")

    if args.log_results:
        print("Logging results")

if __name__ == "__main__":
    main()
