"""
@Date: 04/22/2022
@Author: Gaurab Pokharel (gpokhare@gmu.edu)

Description:
Main file for running experiments
"""
from structs import config

##TODO
# ""continue"" instead of resetting seed if you already find a run-data in location

import argparse
# Function that gets arguments from the command line for running the experiments
def get_arguments():
    parser = argparse.ArgumentParser()

    # Non Boolean Vars
    parser.add_argument("--horizon", help="Number of time steps to run experiment for", metavar="t", required=True)
    parser.add_argument("--running_on", help="0 for windows, 1 for mac, 2 for linux", metavar="X", required=True)
    parser.add_argument("--num_runs", help="Number of runs to execute", metavar="N")
    parser.add_argument("--lambda", help="Value of Lambda for the experiment", metavar="L")
    parser.add_argument("--experiment_type", help="Experiment type to run, can be {0, 1, 2}", metavar="E", required=True)
    parser.add_argument("--player_pref", help="Can be Random/Varied", metavar="P", required=True)
    parser.add_argument("--arm_pref", help="Can be Random/Varied", metavar="A", required=True)
    parser.add_argument("--seed", help="Random Seed for this run", metavar="S", required=True)

    # Boolean Vars
    parser.add_argument("--use_thompson", help="Turn on to use Thompson Sampling for rewards ", action="store_true")
    parser.add_argument("--use_UCB", help="Turn on to use UCB for rewards ", action="store_true")
    parser.add_argument("--run_random", help="Turn on to run random market of varying sizes", action="store_true")
    parser.add_argument("--run_varied", help="Turn on to run markets with varying pref. homogeniety", action="store_true")
    parser.add_argument("-l", "--log_results", help="Turn on to log experiment", action="store_true")
    parser.add_argument("-dt", "--delete_temp", help="Turn on to delete temporary files", action="store_true")
    parser.add_argument("--==================", help="")
    args = parser.parse_args()

    config.horizon = int(args.horizon)
    print(config.horizon)

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
