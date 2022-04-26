"""
@Date: 04/26/2022
@Author: Gaurab Pokharel (@gpokhare@gmu.edu)

Description:
A python file containing all the parent classes (and the functions) of objects that are used in solving the domain.
These Classes act as parents to their (different and subsequent) children.
Implemented to reduce redundant code.


Note: tracked_values dict is dependent on the type of reward structure the agent is keeping track of.
- If using UCB:
    tracked_values[arm.index] = (total reward, number_of_pulls)
- If using thompson_sampling:
    tracked_values[arm.index] = (total_reward, total_pulls, mean, variance)

"""
from math import sqrt, log
import numpy as np
import config

class Player:
    def __init__(self, Index, ArmsList=None, PlayerList=None):
        self.index = Index  # Index to identify player
        self.tracked_values = {}  # Dict to keep track of values, depending on reward structre used
        self.attempted_pulls = {}  # Dict to keep track of attempted pulls at time t
        self.successful_pulls = {}  # Dict to keep track of successful pulls at time t
        self.arms_list = {}
        self.players_list = {}

    def initialize_player_and_arms_list(self, PlayerList, ArmsList):
        if ArmsList is not None:
            for a in ArmsList:
                self.arms_list[a.index] = a

        if PlayerList is not None:
            for p in PlayerList:
                self.players_list[p.index] = p

    # Function to set Thompson Tracking of Rewards
    def set_thompson(self, arm, rewards, pulls, mean, variance):
        self.tracked_values[arm.index] = [rewards, pulls, mean, variance]

    # Get a sample of reward based on beleif that we have about reward distribution
    def get_thompson(self, arm):
        if self.tracked_values[arm.index][1] == 0:
            return config.inf
        mean = self.tracked_values[arm.index][2]
        variance = self.tracked_values[arm.index][3]
        reward = -99
        while reward < 0:
            reward = np.random.normal(mean, sqrt(variance))
        return reward

    # Update Thompson Tracking of Preferences
    def update_thompson(self, arm, reward):
        # UPDATE POSTERIOR MEAN AND PRECISION FOR ARM
        self.tracked_values[arm.index][0] += reward # Update total reward
        self.tracked_values[arm.index][1] += 1 # Update total pulls
        old_mean = self.tracked_values[arm.index][2] # Keep a copy of old mean
        old_variance = self.tracked_values[arm.index][3] # Keep a copy of old variance
        total_reward = self.tracked_values[arm.index][0]
        n = self.tracked_values[arm.index][1]
        new_mean = (1 / ((1 / old_variance) + (n / old_variance))) * (
                    (old_mean / old_variance) + (total_reward / old_variance)) # Calculate new mean
        new_variance = ((1 / old_variance) + (n / old_variance)) ** (-1) # Calculate new variance
        self.tracked_values[arm.index][2] = new_mean

        # This is here to prevent NaN errors, variance 0 leads to issues. Keeping a very small number instead
        if new_variance <= 0.000001:
            self.tracked_values[arm.index][3] = 0.000001
        else:
            self.tracked_values[arm.index][3] = new_variance

    # Function that sets the ucb of the given arm for the player to input value
    def set_ucb(self, arm, value, number_of_pulls):
        self.tracked_values[arm.index] = [value, number_of_pulls]

    # Function that gets the ucb of the given arm at current time
    def get_ucb(self, arm, t):
        if self.tracked_values[arm.index][1] == 0:
            return config.inf
        t_r = self.tracked_values[arm.index][0]
        t_p = self.tracked_values[arm.index][1]
        return (t_r / t_p) + sqrt((3 * log(t)) / (2 * t_p))

    # Function that updates the ucb of the given arm.
    def update_ucb(self, arm, reward):
        if self.tracked_values[arm.index][0] == config.inf:
            self.tracked_values[arm.index][0] = reward
        else:
            self.tracked_values[arm.index][0] += reward
        self.tracked_values[arm.index][1] += 1
        return

    # Function that attemps an arm
    def attempt_arm(self, arm, time):
        self.attempted_pulls[time] = arm.index
        # Request to be pulled by arm
        arm.request_pull(self, time)
        return

    # Function that pulls as arm
    def pull_arm(self, arm, time):
        self.successful_pulls[time] = arm.index
        return

    # Function that returns either the UCB value of the arm, or the thompson sample of the arm
    # based on current belief
    def get_arm_value_based_on_current_belief(self, arm, time):
        if config.use_thompson:
            return self.get_thompson(arm)
        if config.use_UCB:
            return self.get_ucb(arm, time)

    # Function that updates the belief, either UCB or Thompson for a given arm at time t
    def update_belief(self, arm, reward):
        if config.use_UCB:
            return self.update_ucb(arm, reward)
        if config.use_thompson:
            return self.update_thompson(arm, reward)


    # Function that returns the best arm to pull at input time
    # TODO: Implemented in child class based on implementation
    def get_best_arm(self, time):
        pass

    # TODO: Implemented in child class, based on implementation
    def check_arm_preference(self, arm_index, player1_index):
        pass


