import csv

import numpy as np
from structs import config
from structs.player import Player
import matplotlib.pyplot as plt


plt.rcParams['figure.dpi'] = 300
from scipy.stats import norm
from matplotlib import gridspec


class UnknowingPlayerII(Player):

    def __init__(self, Index, ArmsList=None, PlayerList=None, ArmsPreference=None):
        self.arms_preferences = None
        super().__init__(Index, ArmsList, PlayerList)
        # self.ucb = None
        self.win_counts = {}
        self.lose_counts = {}

        #========================
        self.last_ucb = None
        self.last_probab = None
        self.last_value = None
        # ========================

    def print_player_state(self, time):
        print(f"Player {self.index} ::: ", end="")

        #===============================================================================================================
        arr = np.zeros((len(self.arms_list.keys()), 2))
        for arm_index in self.arms_list.keys():
            arr[arm_index][0] = arm_index
            arr[arm_index][1] = self.last_value[arm_index]
        arr = arr[arr[:, 1].argsort()]
        for row in range(arr.shape[0] - 1, -1, -1):
            arm_index = int(arr[row][0])
            print(
                f"(A{arm_index}, Mean: {self.last_ucb[arm_index]:.2f}, Prob: {self.last_probab[arm_index]:.2f}, V: {self.last_value[arm_index]:.2f})  ||",
                end="")
        print("")
        #===============================================================================================================

        # player_list = self.get_matched_players(time)
        # # Calculate first vector
        # ucb_vector = np.ones(len(self.arms_list.keys()), int)
        # for arm_index in self.arms_list.keys():
        #     val = self.get_ucb(self.arms_list[arm_index], time)
        #     ucb_vector[arm_index] = val
        #
        # # Calculate second vector
        # probability_vector = np.zeros(len(self.arms_list.keys()))
        # arm_index = 0
        # for player_index in player_list:
        #     if player_index == -99:
        #         probability_vector[arm_index] = 1.0
        #     else:
        #         probability_vector[arm_index] = self.get_probability_of_winning(self.players_list[player_index],
        #                                                                         self.arms_list[arm_index], time)
        #     arm_index += 1
        #
        # values = np.multiply(ucb_vector, probability_vector)
        #
        # # for arm_index in self.arms_list.keys():
        # #     print(f"({arm_index}, UCB: {ucb_vector[arm_index]:.2f}, P: {probability_vector[arm_index]:.2f}, V: {values[arm_index]:.2f}) ", end="")
        # # print("")
        # # ADDITION
        # arr = np.zeros((len(self.arms_list.keys()), 2))
        # for arm_index in self.arms_list.keys():
        #     arr[arm_index][0] = arm_index
        #     arr[arm_index][1] = values[arm_index]
        # arr = arr[arr[:, 1].argsort()]
        # for row in range(arr.shape[0] - 1, -1, -1):
        #     arm_index = int(arr[row][0])
        #     print(
        #         f"(A{arm_index}, pulls : {self.tracked_values[arm_index][1]:.2f} , Mean: {self.tracked_values[arm_index][2]:.2f}, Prob: {probability_vector[arm_index]:.2f}, V: {values[arm_index]:.2f})  ||",
        #         end="")
        # print("")
        # ###################################################################################################################

    def make_graph_thompson(self, time, AX, colors):
        AXX = gridspec.GridSpec(5, 2)
        AXX.update(wspace=1.5, hspace=1.5)
        x_axis = np.arange(0, 10, 0.1)
        for a_index in range(10):
            if a_index <= 4:
                y = 0
                x = a_index
            else:
                x = a_index - 5
                y = 1
            ax = plt.subplot(AXX[x, y])
            mean = self.tracked_values[a_index][2]
            stdev = np.sqrt(self.tracked_values[a_index][3])
            ax.plot(x_axis, norm.pdf(x_axis, mean, stdev), linewidth=0.5, color=colors[a_index])
            ax.set_title(f"A{a_index} for P{self.index}, t{time}", fontdict={'fontsize': 5})
        plt.show()

    # TODO: Write this
    def dump_anim_files(self, values, probability):
        pass
        # means = np.zeros(len(self.arms_list))
        # variances = np.zeros(len(self.arms_list))
        # for arm_index in range(len(self.arms_list)):
        #     means[arm_index] = self.tracked_values[arm_index][2]
        #     variances[arm_index] = self.tracked_values[arm_index][3]
        #
        # mean_name = config.anim + f"thomp_valsm_{self.index}.csv"
        # var_name = config.anim + f"thomp_valsv_{self.index}.csv"
        # prob_name = config.anim + f"prob_vals_{self.index}.csv"
        # val_name = config.anim + f"vals_{self.index}.csv"
        #
        # with open(mean_name, 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(means)
        # with open(var_name, 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(variances)
        # with open(prob_name, 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(probability)
        # with open(val_name, 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(values)


    def initialize_probabilities_matrix(self):
        number_of_arms = len(self.arms_list.keys())
        number_of_players = len(self.players_list.keys())

        self.win_counts = np.zeros((number_of_players, number_of_arms), int)
        self.lose_counts = np.zeros((number_of_players, number_of_arms), int)

    def get_probability_of_winning(self, player, arm, time):
        win_counts = self.win_counts[player.index][arm.index]
        lose_counts = self.lose_counts[player.index][arm.index]
        total = win_counts + lose_counts
        #print(win_counts, lose_counts)
        if total == 0:
            return 1
        if config.use_thompson:
            value = np.random.beta(win_counts + 1, lose_counts + 1, 1)[0]
        else:
            value = (win_counts / total) + np.sqrt((3 * np.log(time)) / (2 * total))
        if value > 1.0:
            return 1.0
        else:
            return value

    # Lost conflict with opposing player over arm
    def lost_conflict(self, pulled_arm_index, opposing_player_index):
        # I lost conflict against another player for an arm
        self.lose_counts[opposing_player_index][
            pulled_arm_index] += 1  # Increment my lose counts for that arm against that player
        opposing_player = self.players_list[opposing_player_index]
        opposing_player.win_counts[self.index][
            pulled_arm_index] += 1  # Increament that players win count against me for that arm

    def get_best_arm(self, time):
        player_list = self.get_matched_players(time)

        # Calculate first vector
        ucb_vector = np.ones(len(self.arms_list.keys()), int)
        for arm_index in self.arms_list.keys():
            val = self.get_arm_value_based_on_current_belief(self.arms_list[arm_index], time)
            ucb_vector[arm_index] = val

        # Calculate second vector
        probability_vector = np.zeros(len(self.arms_list.keys()))
        arm_index = 0
        for arm_index in range(len(player_list)):
            if player_list[arm_index] == -99:
                probability_vector[arm_index] = 1.0
            else:
                player_index = player_list[arm_index]
                probability_vector[arm_index] = self.get_probability_of_winning(self.players_list[player_index],
                                                                                self.arms_list[arm_index], time)

        # Find Max and return
        values = np.multiply(ucb_vector, probability_vector)
        max_val = np.amax(values)
        indices = np.where(values == max_val)[0]
        return_val = np.random.choice(indices, 1)[0] # Randomly break ties
        self.dump_anim_files(values, probability_vector)

        #--------------------------------------
        self.last_probab = probability_vector
        self.last_value = values
        self.last_ucb = ucb_vector
        #--------------------------------------

        return self.arms_list[return_val]

    def get_matched_players(self, time):
        players = np.zeros(len(self.arms_list.keys()), int)
        for arm_index in self.arms_list.keys():
            arm = self.arms_list[arm_index]

            if (time - 1) not in arm.pulls.keys():
                players[arm_index] = -99
            else:
                player_that_pulled_index = arm.pulls[time - 1]
                players[arm_index] = player_that_pulled_index
        return players

    def initialize_belief_tracking(self, number_of_players, number_of_arms):
        if config.use_UCB:
            self.initialize_ucb()
        if config.use_thompson:
            self.initialize_thompson()
        self.initialize_probabilities_matrix()


"""
 (the left matrix, there needs to be two) each player maintains for each arm, two pieces of information: 
 - what is the mean avg reward that i have seen from this arm so far? 
 - what is the number of times i have successfully played this arm? 

 For each player, there is going to be two right matrix (for each arm) 
 1) first matrix is going to have, number of times i have gone up against another player in a head to head battle and succeeded 
 2) Number of times i have gone up against another player and lost 

 pi vs pj on ak. i know perfectly well how many times i have gone up against pj and how many i won and lost. 

 last time period, arm k was matched with player j, i is trying to figure out if it makes sense to propose to k? The only thing i care about there is my probability of winning against arm j. 





for every arm ak, i compute the UCB estimate of my expected value (computed from left matrix) conditional on being successful. 
now, what i need to ask myself is what is the probability that i will successful if i propose to that arm? 
    - if that arm was unmatched last time, then i go ahead and assume that i have probability 1 (could be wrong) 
    - if it was matched last time, i am going to compute two different vectors and then take the element wise product of those vectors and choose the max of that 
        - vector number 2 will be filled in as follows: 
            - for each arm k, if k was unmatched last time put in 1 
            - if it was matched with player j, i am going to look up what is the number of times I have confliced with j when proposing to k, how many win? how many lose? then computer the 
            bernoulli UCB estimate of that and fill that in into this vector. 
        so now, i am estimating a probability of success if i make a proposal to arm k. Now that i have the probabilities for all arms k, and I have my UCB expected values, i take the element wise product 
        and i choose the one that maximizes 

        suppose i won 10 times, and lost 20 times 
        bernoulli_ucb = (10/30, 30) 
"""