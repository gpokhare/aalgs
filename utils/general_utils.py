import argparse
from structs import config
import sys
import csv
import  numpy as np
import random

# Helper function that writes an array to file
def write_to_file(filename, array):
    file = open(filename, 'w', newline='')
    writer = csv.writer(file)
    for w in range(len(array)):
        writer.writerow([array[w]])
    file.close()

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

    config.number_of_runs = int(args.num_runs)
    config.experiment_type = int(args.experiment_type)
    config.player_preference_type = args.player_pref
    config.arm_preference_type = args.arm_pref


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

    config.running_on = args.running_on
    # For Windows
    if config.running_on == '0':
        config.temploc = r'C:\Users\gabip\Desktop\logs\temp\\' # Folder location of where temporary files go
        config.random_loc = r"C:\Users\gabip\Desktop\logs\Random\\" # Folder location of where Random Logs go
        config.het_loc = r"C:\Users\gabip\Desktop\logs\Varied\\" # Folder location of where varied prefs go
        config.anim = r"C:\Users\gabip\Desktop\logs\anim\\"
        config.loc = r"C:\Users\gabip\Desktop\logs\\"
    # For Mac and Linux
    else:
        if config.running_on == '1':
            config.loc = r"/Users/gaurab/Documents/Git/logs/"
        else:
            config.loc = r"/scratch/gpokhare/temp/logs/"
        config.temploc = config.loc + "temp/"
        config.random_loc = config.loc + "Random/"
        config.het_loc = config.loc + "Varied/"
        config.anim = config.loc + "anim/"

    if config.experiment_type == 0:
        config.player_type = 'knowing'
        config.arm_type = 'knowing'
    elif config.experiment_type == 1:
        config.player_type = 'unknowing I'
        config.arm_type = 'knowing'
    else:
        config.player_type = 'unknowing II'
        config.arm_type = 'unknowing'

def print_to_log(string):
    org_stdout = sys.stdout
    with open(config.loc + "run_" + str(config.run_number) + "_" + str(config.seed) + ".txt",
              'a') as f:
        sys.stdout = f
        print(string)
    sys.stdout = org_stdout


def print_true_state(solver):
    org_stdout = sys.stdout
    with open(config.loc + "run_" + str(config.run_number) + "_" + str(config.seed) + ".txt",
              'a') as f:
        sys.stdout = f
        print("TRUE PREFERENCES OF THE MARKET")
        print(solver.Mrkt)
        sys.stdout = org_stdout

def print_current_belief_state(solver, t, stability):
    org_stdout = sys.stdout
    with open(config.loc + "run_" + str(config.run_number) + "_" + str(config.seed) + ".txt", 'a') as f:
        sys.stdout = f
        if (t >= 2) and (t % config.debug_steps == 0):
            print()
            print("======================================================================")
            print(f"TIME STEP: {t}")
            print("--------------------------------------------------------------------")
            print("Matching at current time step is ", end="")
            if stability == 1:
                print("STABLE")
            else:
                print(f"UNSTABLE. The blocking pair is : {solver.Mrkt.blocking_pair}")
                print()
                print("The current Matchings are: ")
                for p in solver.Mrkt.players:
                    if t not in p.successful_pulls.keys():
                        print(f"(p {p.index}, None).", end="")
                    else:
                        print(f"(p {p.index}, a {p.successful_pulls[t]}).", end="")
                    print("Player Belief : ", end=" >>>  ")
                    p.print_player_state(t)
                print("--------------------------------------------------------------------")
                print("Current Arm Beliefs are: ")
                for a in solver.Mrkt.arms:
                    a.print_arm_state(t)
            print("======================================================================")
            print()
        sys.stdout = org_stdout


def print_stability_to_console(solver, t, stability):
    if (t >= 2) and (t % 5000 == 0):
        if stability == 0:
            print("market unstable")
        else:
            print("STABLE")
        # print("The current Matchings are: ")
        # for p in list(solver.Mrkt.players_dict.values()):
        #     if t not in p.successful_pulls.keys():
        #         print(f"(p {p.index}, None)")
        #     else:
        #         print(f"(p {p.index}, a {p.successful_pulls[t]})")