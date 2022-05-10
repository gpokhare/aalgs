"""
@Date: 04/22/2022
@Author: Gaurab Pokharel (gpokhare@gmu.edu)

Description:
Main file for running experiments
"""
from utils import general_utils
import os
import glob
from structs import config
from solvers.ca_ucb import ca_ucb
from utils.analysis import Analyse
import numpy as np
import random

##TODO
# ""continue"" instead of resetting seed if you already find a run-data in location


def main():
    # First get the experiment settings
    general_utils.get_arguments()
    arr = np.arange(0, 10000, 1)

    # Delete all existing temporary text log files from before
    prev_dir = os.getcwd()
    os.chdir(config.loc)
    allfiles = glob.glob("*.txt")
    for file in allfiles:
        os.remove(file)
    os.chdir(prev_dir)

    ########################################################################################################
    # RANDOM PREFERENCES ON BOTH SIDES
    ########################################################################################################

    if config.run_random:  # Check if we want to run experiments with random preferences on both sides
        for i in range(config.number_of_runs):
            for N in config.market_sizes:
                # config.newseed += 1
                config.run_number = i

                seed = np.random.choice(arr, 1)[0]
                np.random.seed(seed)
                random.seed(seed)
                config.seed = seed

                # DEBUG
                print()
                print()
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

                print(f"MARKET SIZE {N} RUN NUMBER {i}")
                # ========================================

                regret_p_filename = config.temploc +  'regret_p_market_size_' + str(N) + '_run_' + str(i) + '.csv'
                regret_a_filename = config.temploc + 'regret_a_market_size_' + str(N) + '_run_' + str(i) + '.csv'
                stability_filename = config.temploc + 'stability_market_size_' + str(N) + '_run_' + str(i) + '.csv'


                if not os.path.exists(regret_p_filename):


                    instance = ca_ucb(number_of_agents=N, number_of_arms=N, beta=-1)
                    r_p_o, r_p_p, r_a_o, r_a_p, s = instance.run()

                    # Write this instance to file for later analysis purpose
                    if config.player_pessimal_regret:
                        general_utils.write_to_file(regret_p_filename, r_p_p)
                    else:
                        general_utils.write_to_file(regret_p_filename, r_p_o)
                    if config.arm_pessimal_regret:
                        general_utils.write_to_file(regret_a_filename, r_a_p)
                    else:
                        general_utils.write_to_file(regret_a_filename, r_a_o)
                    general_utils.write_to_file(stability_filename, s)


    #########################################################################################################
    # VARIED PREFERENCE HETEROGENITY
    #########################################################################################################

    if config.run_varied:  # Check if we want to run experiments with varied preference heterogenity
        N = 10
        for i in range(config.number_of_runs):
            for b in config.beta_vals:
                # config.newseed += 1
                config.run_number = i

                seed = np.random.choice(arr, 1)[0]
                np.random.seed(seed)
                random.seed(seed)
                config.seed = seed

                # DEBUG
                print()
                print(f"BETA {b} RUN NUMBER {i}")
                # ========================================
                # Write this instance to file for later analysis purpose
                regret_p_filename = config.temploc + 'regret_p_beta_' + str(b) + '_run_' + str(i) + '.csv'
                regret_a_filename = config.temploc + 'regret_a_beta_' + str(b) + '_run_' + str(i) + '.csv'
                stability_filename = config.temploc + 'stability_beta_' + str(b) + '_run_' + str(i) + '.csv'

                if not os.path.exists(regret_p_filename):
                    instance = ca_ucb(number_of_agents=N, number_of_arms=N, beta=b)
                    r_p_o, r_p_p, r_a_o, r_a_p, s = instance.run()

                    if config.player_pessimal_regret:
                        general_utils.write_to_file(regret_p_filename, r_p_p)
                    else:
                        general_utils.write_to_file(regret_p_filename, r_p_o)
                    if config.arm_pessimal_regret:
                        general_utils.write_to_file(regret_a_filename, r_a_p)
                    else:
                        general_utils.write_to_file(regret_a_filename, r_a_o)
                    general_utils.write_to_file(stability_filename, s)

    #
    ana = Analyse(config.temploc)
    ana.analyse()

if __name__ == "__main__":
    main()

