"""
@Date: 04/25/2022
@Author: Gaurab Pokharel (@gpokhare@gmu.edu)

Description:
A python file containing the configuration settings for runing experiments on the code.
"""
import random
import numpy as np

#===============================================================================================================
# Seeds
#----------------------------------------------------------------------------------------------------------------
inf = 999
seed = None
run_number = None
################################################################################################################



#===============================================================================================================
# LOG SETTINGS
#----------------------------------------------------------------------------------------------------------------
running_on = None #0 for windows, 1 for mac, 2 for linux
debug = False
debug_steps = 500 # Number of time steps in which to spit out world state
delete_temp_files = False

temploc = None
random_loc = None
het_loc = None
anim = None
loc = None




#===============================================================================================================
# EXPERIMENT SETTINGS
#----------------------------------------------------------------------------------------------------------------
"""
Experiment Type Options are:  
'0'     : players know arm preferences (knowing), arms know their own preferences  (knowing) Vanilla CA_UCB
'1'     : players do not know arm preferences (unknowing I), arms know their own preferences (knowing)
'2'     : players do not know arm preferences (unknowing II), arms do not know their own preferences (unknowing) 
"""
experiment_type = None


player_type = None
arm_type = None

player_preference_type = None
arm_preference_type = None

use_thompson = None
use_UCB = None

run_random = None # Run only random Preference
run_varied = None # Run only varied pref het

player_pessimal_regret = False # When false => Player optimal
arm_pessimal_regret = True # When false => Arm Optimal
analyse_arm_regrets = True  # When true => graphs will include arm regrets as well


# RUN PARAMETERS
horizon = None
number_of_runs = 10
Lambda = 0.9
market_sizes = [5, 10, 15, 20]
beta_vals = [0, 10, 100, 1000]

################################################################################################################
