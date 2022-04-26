from structs.arm import Arm
from structs import config
from utils import general_utils
from math import sqrt, log
import numpy as np
import sys
import random

"""
Note: tracked_values dict is dependent on the type of reward structure the agent is keeping track of.
- If using UCB:
    tracked_values[player.index] = (total reward, number_of_pulls)
- If using thompson_sampling:
    tracked_values[player.index] = (total_reward, total_pulls, mean, variance)
"""

class UnknowingArm(Arm):

    def __init__(self, Index, ArmsList=None, PlayerList=None):
        self.tracked_values = {}
        self.arms_list = {}
        self.players_list = {}
        super().__init__(Index, ArmsList, PlayerList)


    def print_arm_state(self, t):
        arr = np.zeros((len(self.players_list.keys()), 2))
        for p_i in self.players_list.keys():
            arr[p_i][0] = p_i
            arr[p_i][1] = self.get_player_value_based_on_current_belief(self.players_list[p_i], t)
        arr = arr[arr[:, 1].argsort()]
        print(f"Arm {self.index} tracked rewards ::: ", end="")
        for row in range(arr.shape[0]-1, -1, -1):
            p_i = int(arr[row][0])
            if config.use_UCB:
                print(f"( P{p_i}, Mean: {self.tracked_values[p_i][0] / self.tracked_values[p_i][1]:.2f} ) ||", end="")
            else:
                print(f"( P{p_i}, Mean: {self.tracked_values[p_i][2]:.2f} ) ||", end="")
        print("")

    # Function that sets the ucb of the given player
    def set_ucb(self, player, value, number_of_pulls):
        self.tracked_values[player.index] = [value, number_of_pulls]
        return

    # Function that sets the thompson tracking for a given player
    def set_thompson(self, player, reward, pulls, mean, variance):
        self.tracked_values[player.index] = [reward, pulls, mean, variance]
        return

    # Function that initializes the UCB tracking of the players
    def initialize_ucb(self):
        for player_index in self.players_list.keys():
            plyr = self.players_list[player_index]
            self.set_ucb(plyr, config.inf, 0)
        return

    # Function that initializes the thompson tracking of the players
    def initialize_thompson(self):
        for player_index in self.players_list.keys():
            plyr = self.players_list[player_index]
            self.set_thompson(plyr, 0.0, 0.0, len(self.players_list.keys()), len(self.players_list.keys()))
        return

    # Function that initializes the belief tracking, either thompson or UCB
    def initialize_belief_tracking(self):
        if config.use_UCB:
            return self.initialize_ucb()
        if config.use_thompson:
            return self.initialize_thompson()

    # Function that gets the ucb of the given player at current time
    def get_ucb(self, player, t):
        if self.tracked_values[player.index][1] == 0:
            return config.inf
        t_r = self.tracked_values[player.index][0]
        t_p = self.tracked_values[player.index][1]
        return (t_r / t_p) + sqrt((3 * log(t)) / (2 * t_p))

    # Update the UCB for a player
    def update_ucb(self, player, reward):
        if self.tracked_values[player.index][0] == config.inf:
            self.tracked_values[player.index][0] = reward
        else:
            self.tracked_values[player.index][0] += reward
        self.tracked_values[player.index][1] += 1
        return

    # Get the thompson sample of the given player at current time
    def get_thompson(self, player):
        if self.tracked_values[player.index][1] == 0.0:
            return config.inf
        mean = self.tracked_values[player.index][2]
        variance = self.tracked_values[player.index][3]
        reward = -99
        while reward < 0:
            reward = np.random.normal(mean, sqrt(variance))
        return reward

    # Update the thompson belief for the player at current time
    def update_thompson(self, player, reward):
        self.tracked_values[player.index][0] += reward
        self.tracked_values[player.index][1] += 1
        old_mean = self.tracked_values[player.index][2]
        old_variance = self.tracked_values[player.index][3]

        total_reward = self.tracked_values[player.index][0]
        n = self.tracked_values[player.index][1]

        new_mean = (1 / ((1 / old_variance) + (n / old_variance))) * (
                    (old_mean / old_variance) + (total_reward / old_variance))
        new_variance = ((1 / old_variance) + (n / old_variance)) ** (-1)
        self.tracked_values[player.index][2] = new_mean
        if new_variance <= 0.000001:
            self.tracked_values[player.index][3] = 0.000001
        else:
            self.tracked_values[player.index][3] = new_variance
        return

    # Function that updates the belief, either UCB or Thompson for a given arm at time t
    def update_belief(self, player, reward):
        if config.use_UCB:
            return self.update_ucb(player, reward)
        if config.use_thompson:
            return self.update_thompson(player, reward)


    # Function that returns either the UCB value of the arm, or the thompson sample of the arm
    # based on current belief
    def get_player_value_based_on_current_belief(self, player, time):
        if config.use_thompson:
            return self.get_thompson(player)
        if config.use_UCB:
            return self.get_ucb(player, time)

    # Function that returns the arm with the highest value
    def get_best_player(self, time):
        pull_requestss = self.pull_requests[time]
        if len(pull_requestss) == 0:
            print("ERROR: EMPTY PULL REQUESTS SET.")
            return None
        best_list = []
        best_val = -9999
        for i in range(len(pull_requestss)):
            curr_player = pull_requestss[i]
            curr_val = self.get_player_value_based_on_current_belief(self.players_list[curr_player], time)
            if curr_val > best_val:
                best_list = list()
                best_list.append(curr_player)
                best_val = curr_val
            elif curr_val == best_val:
                best_list.append(curr_player)
        best_player = self.players_list[best_list[random.randint(0, len(best_list) - 1)]]
        return best_player

    def check_better_player(self, p1_idnex, p2_index, time):
        p1_val = self.get_player_value_based_on_current_belief(self.players_list[p1_idnex], time)
        p2_val = self.get_player_value_based_on_current_belief(self.players_list[p2_index], time)
        if p1_val > p2_val:
            return p1_idnex
        else:
            return p2_index

    # Function that picks the best player among the incoming requests at time t
    def resolve_pull_requests(self, time):
        # Check if someone already attempted to pull this arm at time t
        if time not in self.pull_requests.keys():
            if config.debug:
                general_utils.print_to_log("No pull request for this arm at current time.")
            return None
        else:
            # At least one person has attempted to pull this arm at current time
            best_player_index = self.pull_requests[time][0]
            for current_player in self.pull_requests[time]:
                best_player_index = self.check_better_player(best_player_index, current_player, time)
            # Now that you have best player among the pull requests

            best_player = self.players_list[best_player_index]
            self.pulls[time] = best_player_index
            best_player.pull_arm(self, time)

            if not config.player_type == 'unkowing II':
                general_utils.print_to_log("ERROR: Player/ARM type mismatch.")
            else:
                pull_requests = self.pull_requests[time].copy()
                pull_requests.remove(best_player_index)
                if len(pull_requests) != 0:
                    for plyr in pull_requests:
                        p = self.players_list[plyr]
                        p.lost_conflict(self.index, best_player_index)
            return best_player