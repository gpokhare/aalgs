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

# For Windows
if running_on == 0:
    temploc = r'C:\Users\gabip\Desktop\logs\temp\\' # Folder location of where temporary files go
    random_loc = r"C:\Users\gabip\Desktop\logs\Random\\" # Folder location of where Random Logs go
    het_loc = r"C:\Users\gabip\Desktop\logs\Varied\\" # Folder location of where varied prefs go
    anim = r"C:\Users\gabip\Desktop\logs\anim\\"
    loc = r"C:\Users\gabip\Desktop\logs\\"
# For Mac and Linux
else:
    if running_on == 1:
        loc = r"/Users/gaurab/Documents/Git/logs/"
    else:
        loc = r"/scratch/gpokhare/logs/"
    temploc = loc + "temp/"
    random_loc = loc + "Random/"
    het_loc = loc + "Varied/"
    anim = loc + "anim/"

################################################################################################################



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


if experiment_type == 0:
    player_type = 'knowing'
    arm_type = 'knowing'
elif experiment_type == 1:
    player_type = 'unknowing I'
    arm_type = 'knowing'
else:
    player_type = 'unknowing II'
    arm_type = 'unknowing'

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