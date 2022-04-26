import numpy as np
from structs import config
import sys, random
from structs.player import Player

class UnknowingPlayerI(Player):

    def __init__(self, Index, ArmsList=None, PlayerList=None, ArmsPreference=None):
        self.plausible_set = {}  # List to keep track of the plausible set for player
        self.arms_preferences = None
        super().__init__(Index, ArmsList, PlayerList)

    def initialize_belief_tracking(self, number_of_players, number_of_arms):
        if config.use_UCB:
            self.initialize_ucb()
        if config.use_thompson:
            self.initialize_thompson()
        # Numpy array of all 0s
        # 1 indicates that this arm is before me in that particular arm's preference ordering
        self.arms_preferences = np.zeros((number_of_arms, number_of_players), int)

    def check_arm_preference(self, arm_index, player1_index):
        # If self tracked preferences indicates that player1 is preferred more, return player 1
        # Comparison with self, always true (redundant check)
        if player1_index == self.index:
            return self.index
        if self.arms_preferences[arm_index][player1_index]:
            return player1_index
        else:
            return self.index

    # Function that returns the arm with the highest UCB value
    def get_best_arm(self, time):
        self.update_plausible_set(time)
        if len(self.plausible_set[time]) == 0:
            print("ERROR: EMPTY PLAUSIBLE SET.")
            return None
        best_list = []
        best_val = -9999
        for i in range(len(self.plausible_set[time])):
            curr_arm = self.plausible_set[time][i]
            curr_val = self.get_arm_value_based_on_current_belief(self.arms_list[curr_arm], time)
            if curr_val > best_val:
                best_list = []
                best_list.append(curr_arm)
                best_val = curr_val
            elif curr_val == best_val:
                best_list.append(curr_arm)
        best_arm = self.arms_list[best_list[random.randint(0, len(best_list) - 1)]]
        return best_arm

    # Lost conflict with opposing arm over arm
    def lost_conflict(self, pulled_arm_index, opposing_player_index):
        self.arms_preferences[pulled_arm_index][opposing_player_index] = 1

    # Function to update the plausible set of arm using self tracked preferences
    def update_plausible_set(self, t):
        """"if the arm wasn't pulled at all then it is in the plausible set. for the arms that were pulled, if they preferred self then it goes in the set."""
        new_plausible_set = []
        for a in self.arms_list.keys():
            arm = self.arms_list[a]
            # Check if this arm was pulled at previous time step
            if t - 1 in arm.pulls.keys():
                # Who pulled this arm at previous time
                prev_player = self.players_list[arm.pulls[t - 1]]
                # Check if the arm prefers self over prev_player, if it does then put arm in plausible set

                if self.check_arm_preference(arm.index, prev_player.index) == self.index:
                    new_plausible_set.append(arm.index)
            else:
                # If it wasn't then by default this arm is plausible
                new_plausible_set.append(arm.index)
        self.plausible_set[t] = new_plausible_set

        # DEBUG
        if config.debug:
            org_stdout = sys.stdout
            with open(config.loc + "run_" + str(config.run_number) + "_" + str(config.seed) + ".txt", 'a') as f:
                sys.stdout = f
                print(f"Successfully updated plausible set player {self.index} at time {t}. New Set: [", end='')
                for item in new_plausible_set:
                    print(f"{item.index} , ", end='')
                print("]")
            sys.stdout = org_stdout
        # =========================================================================================