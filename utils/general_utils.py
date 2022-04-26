import argparse
from structs import config
import sys
# Function that gets arguments from the command line for running the experiments
def get_arguments():
    parser = argparse.ArgumentParser()
    # Non Boolean Vars
    parser.add_argument("--horizon", help="Number of time steps to run experiment for", metavar="t", required=True)
    parser.add_argument("--running_on", help="0 for windows, 1 for mac, 2 for linux", metavar="X", required=True)
    parser.add_argument("--num_runs", help="Number of runs to execute", metavar="N", required=True)
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
    config.running_on = int(args.running_on)
    config.number_of_runs = int(args.num_runs)
    config.experiment_type = int(args.experiment_type)
    config.player_preference_type = args.player_pref
    config.arm_preference_type = args.arm_pref
    config.seed = int(args.seed)

    if args.use_thompson:
        config.use_thompson = True
        config.use_UCB = False

    if args.use_UCB:
        config.use_UCB = True
        config.use_thompson = False

    if args.run_random:
        config.run_random = True
    else:
        config.run_random = False
    if args.run_varied:
        config.run_varied = True
    else:
        config.run_varied = False
    if args.log_results:
        config.debug = True
    else:
        config.debug = False
    if args.delete_temp:
        config.delete_temp_files = True
    else:
        config.delete_temp_files = False
    return


def print_to_log(string):
    org_stdout = sys.stdout
    with open(config.loc + "run_" + str(config.run_number) + "_" + str(config.seed) + ".txt",
              'a') as f:
        sys.stdout = f
        print(string)
    sys.stdout = org_stdout

