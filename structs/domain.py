import numpy as np
from solvers.gale_shapley import GaleShapely
from collections import defaultdict

# Import arm types
from knowing_arm import KnowingArm
from unknowing_arm import UnknowingArm

# Import player types
from player_type_0 import KnowingPlayer
from player_type_1 import UnknowingPlayerI
from player_type_2 import UnknowingPlayerII

from structs import config


class Market:
    def __init__(self, number_of_players, number_of_arms, Beta):
        # Set up hyperparams
        self.N = number_of_players
        self.A = number_of_arms
        self.beta = Beta

        # Make the arms and players
        self.arms_dict = {}
        self.players_dict = {}
        self.player_preferences = {}
        self.arm_preferences = {}
        self.initialize_players_and_arms()


        # Set up rewards and means for regret analysis
        self.player_rewards, self.arm_rewards = self.initailize_mean_rewards()
        self.player_optimal_rewards, self.player_pessimal_rewards = self.get_GS_rewards(proposer_type='player')
        self.arm_optimal_rewards, self.arm_pessimal_rewards = self.get_GS_rewards(proposer_type='arm')

        self.blocking_pair = (-1, -1)

    # This function prints out the true preferences of the players and the arms.
    def __str__(self):
        print()
        print("The player's preferences are")
        for i in range(self.N):
            print(f"player {self.players_dict[i].index}", end=": ")
            for idx in range(len(self.player_preferences[self.players_dict[i].index]) - 1):
                print(f"Arm {self.player_preferences[self.players_dict[i].index][idx]} > ", end="")
            print(f"Arm {self.player_preferences[self.players_dict[i].index][idx + 1]}")
        print()

        print("The arm's preferences are")
        for j in range(self.A):
            print(f"Arm {self.arms_dict[j].index}", end=": ")
            for idx in range(len(self.arm_preferences[self.arms_dict[j].index]) - 1):
                print(f"Player {self.arm_preferences[self.arms_dict[j].index][idx]} > ", end="")
            print(f"Player {self.arm_preferences[self.arms_dict[j].index][idx + 1]}")
        print()

        print("Stable Match with players proposing is:")
        p_preferences = self.player_preferences
        a_preferences = self.arm_preferences

        # Players as proposers
        GS_ia = GaleShapely(self.N, self.A, p_preferences, a_preferences)
        GS_i = GS_ia.run()

        for p in self.players_dict.values():
            p_index = p.index
            a_index = GS_i[p_index]
            print(f"(p {p_index}, a {a_index})")
        return ""


    def print_player_tracked_thompson(self):
        for p in self.players_dict.values():
            print(f"Player {p.index} tracked and true rewards are: ", flush=True)
            for a in self.arms_dict.values():
                true_mean = self.player_rewards[p.index][a.index]
                tracked_mean = p.tracked_values[a.index][2]
                tracked_variance = p.tracked_values[a.index][3]
                print(f"Arm {a.index}: True Mean = {true_mean}, Pull Count ={p.tracked_values[a.index][1]:5.2f} , (mean, var) = ({tracked_mean:.2f}, {tracked_variance:.2f}), Diff = {(true_mean - tracked_mean):.2f}", flush=True)
            print(flush=True)
        print("=======================================================================================================================================", flush=True)

    # Initialize the players and arms
    def initialize_players_and_arms(self):

        if config.experiment_type == 0:
            # Player knowing, arm knowing
            # players know arm preferences, arms know their own preferences
            for index in range(self.N):
                p = KnowingPlayer(Index=index)
                # self.players.append(p)
                self.players_dict[index] = p

            for index in range(self.A):
                a = KnowingArm(Index=index)
                # self.arms.append(a)
                self.arms_dict[index] = a

            self.player_preferences = self.initialize_players_preference(config.player_preference_type)
            self.arm_preferences = self.initialize_arms_preference(config.arm_preference_type)

            # Make the necessary information available to the players
            for p in self.players_dict.values():
                p.initialize_player_and_arms_list(self.players_dict, self.arms_dict)
                p.arms_preferences = self.arm_preferences

            # Make the necessary information available to the arms
            for a in self.arms_dict.values():
                a.initialize_player_and_arms_list(self.players_dict, self.arms_dict)
                a.preference = self.arm_preferences[a.index]

        elif config.experiment_type == 1:
            # player unknowing I, arm knowing
            for index in range(self.N):
                p = UnknowingPlayerI(Index=index)
                self.players_dict[index] = p

            for index in range(self.A):
                a = KnowingArm(Index=index)
                self.arms_dict[index] = a

            self.player_preferences = self.initialize_players_preference(config.player_preference_type)
            self.arm_preferences = self.initialize_arms_preference(config.arm_preference_type)

            # Make the necessary information available to the arms
            for a in self.arms_dict.values():
                a.initialize_player_and_arms_list(self.players_dict, self.arms_dict)
                a.preference = self.arm_preferences[a.index]

            # Make the necessary information available to the arms
            for p in self.players_dict.values():
                p.initialize_player_and_arms_list(self.players_dict, self.arms_dict)
                p.initialize_belief_tracking(self.N, self.A) # Players do not have access to arms preferences

        else:
            #player unknowing II, arm unknowing
            for index in range(self.N):
                p = UnknowingPlayerII(Index=index)
                self.players_dict[index] = p

            for index in range(self.A):
                a = UnknowingArm(Index=index)
                self.arms_dict[index] = a

            self.player_preferences = self.initialize_players_preference(config.player_preference_type)
            self.arm_preferences = self.initialize_arms_preference(config.arm_preference_type)

            # Make the necessary information available to the arms
            for a in self.arms_dict.values():
                a.initialize_player_and_arms_list(self.players_dict, self.arms_dict)
                a.initialize_belief_tracking()  # Initialize ucb or thompson

            # Make the necessary information available to the arms
            for p in self.players_dict.values():
                p.initialize_player_and_arms_list(self.players_dict, self.arms_dict)
                p.initialize_belief_tracking(self.N, self.A)


    # A function that initializes the preference order for all players
    def initialize_players_preference(self, preference_type):
        p_pref = {}
        # If the player preferences are supposed to be random
        if preference_type == 'random':
            for p in self.players_dict.values():
                pref_order = []
                random_order = np.arange(len(self.arms_dict.values()))
                np.random.shuffle(random_order)
                arms_ = list(self.arms_dict.values())
                for a in range(len(self.arms_dict.values())):
                    ii = random_order[a]
                    pref_order.append(arms_[ii].index)
                p_pref[p.index] = pref_order

        # If player preferences aren't random, then they are varied according to Beta
        else:
            rewards = defaultdict(dict)
            # Caclulate the new rewards for the players
            for i in self.arms_dict.keys():
                x_i = np.random.uniform(0, 1)
                for k in self.players_dict.keys():
                    E_ik = np.random.logistic(0, 1)
                    U_ik = (self.beta * x_i) + E_ik
                    rewards[i][k] = U_ik
            # For each player
            for p in self.players_dict.values():
                # For each arm, calulate how many other arm's rewards as less than this arm's reward
                # This arm's index in new preference order is that number
                preference_order = [None] * (len(self.arms_dict.values()))
                for current_arm in self.arms_dict.values():
                    current_reward = rewards[current_arm.index][p.index]
                    index = 0
                    for a in self.arms_dict.values():
                        if a.index != current_arm.index:
                            rwrd = rewards[a.index][p.index]
                            if rwrd >= current_reward:
                                index += 1
                    preference_order[index] = current_arm.index
                p_pref[p.index] = preference_order
        return p_pref

    # Function that initializes the random preference of arms over players
    def initialize_arms_preference(self, preference_type):
        a_pref = {}
        # If the player preferences are supposed to be random
        if preference_type == 'random':
            for a in self.arms_dict.values():
                pref_order = []
                random_order = np.arange(self.N)
                np.random.shuffle(random_order)
                players = list(self.players_dict.values())
                for p in range(self.N):
                    pref_order.append(players[random_order[p]].index)
                a_pref[a.index] = pref_order

        # If player preferences aren't random, then they are varied according to Beta
        else:
            rewards = defaultdict(dict)
            for i in self.players_dict.keys():
                x_i = np.random.uniform(0, 1)
                for k in self.arms_dict.keys():
                    E_ik = np.random.logistic(0, 1)
                    U_ik = (self.beta * x_i) + E_ik
                    rewards[i][k] = U_ik
            for a in self.arms_dict.values():
                preference_order = [None] * (len(self.players_dict.values()))
                for current_player in self.players_dict.values():
                    current_reward = rewards[current_player.index][a.index]
                    index = 0
                    for p in self.players_dict.values():
                        if p.index != current_player.index:
                            rwrd = rewards[p.index][a.index]
                            if rwrd >= current_reward:
                                index += 1
                    preference_order[index] = current_player.index
                a_pref[a.index] = preference_order
        return a_pref

    # Function that returns agent optimal and pessimal rewards based on true preferences
    def get_GS_rewards(self, proposer_type):
        p_preferences = self.player_preferences
        a_preferences = self.arm_preferences

        # Players as proposers
        GS_ia = GaleShapely(self.N, self.A, p_preferences, a_preferences)
        GS_i = GS_ia.run()

        # Arms as proposers
        GS_iia = GaleShapely(self.A, self.N, a_preferences, p_preferences)
        GS_ii = GS_iia.run()

        # Return player optimal and player pessimal rewards
        if proposer_type == 'player':
            # First calcualte player optimal rewards
            player_optimal_rewards = {}
            for p_index in GS_i.keys():
                player = self.players_dict[p_index]
                arm = self.arms_dict[GS_i[p_index]]
                player_optimal_rewards[player.index] = self.player_rewards[player.index][arm.index]

            # Calculate player pessimal rewards
            player_pessimal_rewards = {}
            # Now we have a dict of (arm, player) pairs, for each player go through their preference list
            for a_index in GS_ii.keys():
                arm = self.arms_dict[a_index]
                plyr = self.players_dict[GS_ii[a_index]]
                player_pessimal_rewards[plyr.index] = self.player_rewards[plyr.index][arm.index]

            return player_optimal_rewards, player_pessimal_rewards

        if proposer_type == 'arm':
            # Calculate arm pessimal rewards
            arm_pessimal_rewards = {}
            for p_index in GS_i.keys():
                player = self.players_dict[p_index]
                arm = self.arms_dict[GS_i[p_index]]
                arm_pessimal_rewards[arm.index] = self.arm_rewards[arm.index][player.index]

            # Calculate arm optimal rewards
            arm_optimal_rewards = {}
            # Now we have a dict of (arm, player) pairs, for each player go through their preference list
            for a_index in GS_ii.keys():
                arm = self.arms_dict[a_index]
                plyr = self.players_dict[GS_ii[a_index]]
                arm_optimal_rewards[arm.index] = self.arm_rewards[arm.index][plyr.index]
            return arm_optimal_rewards, arm_pessimal_rewards

    # Keep track of (true) mean reawards for players and arms
    def initailize_mean_rewards(self):
        mean_rewards_player = {}
        mean_rewards_arm = {}

        # For all players
        for p in self.players_dict.values():
            # Create a dict of mean reward of arms
            reward_dict = {}
            max_reward = self.A
            # Loop over all arms in preference order
            for a in self.player_preferences[p.index]:
                reward_dict[a] = max_reward
                max_reward -= 1
            mean_rewards_player[p.index] = reward_dict

        # For all arms
        for a in self.arms_dict.values():
            # Create a dict of mean rewards of players
            reward_dict = {}
            max_reward = self.N
            # Loop over all players in preference order
            for p in self.arm_preferences[a.index]:
                reward_dict[p] = max_reward
                max_reward -= 1
            mean_rewards_arm[a.index] = reward_dict

        return mean_rewards_player, mean_rewards_arm

    # A function that samples a reward for a player successfully pulling an arm
    def sample_reward_for_player(self, player, arm):
        reward = -99
        while reward < 0:
            mean = self.player_rewards[player.index][arm.index]
            reward = np.random.normal(mean, 1, 1)[0]
        return reward

    # A function that samples a reward for an arm successfully selecting a player (used only in unknowing arm)
    def sample_reward_for_arm(self, arm, player):
        reward = -99
        while reward <0:
            mean = self.arm_rewards[arm.index][player.index]
            reward = np.random.normal(mean, 1, 1)[0]
        return reward

    # A function to check preference of player between a1 and a2
    def check_player_preference(self, player_index, arm1_index, arm2_index):
        pref_order = self.player_preferences[player_index]
        for i in range(len(pref_order)):
            # If a1 comes first in the preferece list return a1
            if pref_order[i] == arm1_index:
                return arm1_index
            # If a2 comes first in the preference list return a2
            if pref_order[i] == arm2_index:
                return arm2_index

    # A function to check preference of arm between p1 and p2
    def check_arm_preference(self, arm_index, player1_index, player2_index):
        pref_order = self.arm_preferences[arm_index]
        for i in range(len(pref_order)):
            if pref_order[i] == player1_index:
                return player1_index
            if pref_order[i] == player2_index:
                return player2_index

    # Function that calculates the max regret among players at time t
    def calculate_max_player_regret(self, t):
        max_regret_opt = -99
        max_regret_pess = -99
        diff_opt = 0
        diff_pess = 0
        for p in self.players_dict.values():
            # What arm did player pull, if at all
            if t not in p.successful_pulls.keys():
                rewards = 0.0
            else:
                successful_arm = p.successful_pulls[t]
                rewards = self.player_rewards[p.index][successful_arm]
            compare_reward_pess = self.player_pessimal_rewards[p.index]
            compare_reward_opt = self.player_optimal_rewards[p.index]

            diff_opt = compare_reward_opt - rewards
            diff_pess = compare_reward_pess - rewards
            if diff_opt > max_regret_opt:
                max_regret_opt = diff_opt
            if diff_pess > max_regret_pess:
                max_regret_pess = diff_pess
        return max_regret_opt, max_regret_pess

    # Function that calculates the max regret among arms at time t
    def calculate_max_arm_regret(self, t):
        max_regret_opt = -99
        max_regret_pess = -99
        diff_opt = 0
        diff_pess = 0
        for a in self.arms_dict.values():
            if t not in a.pulls.keys():
                rewards = 0.0
            else:
                successful_player = a.pulls[t]
                rewards = self.arm_rewards[a.index][successful_player]

            compare_reward_pess = self.arm_pessimal_rewards[a.index]
            compare_reward_opt = self.arm_optimal_rewards[a.index]

            diff_opt = compare_reward_opt - rewards
            diff_pess = compare_reward_pess - rewards
            if diff_opt > max_regret_opt:
                max_regret_opt = diff_opt
            if diff_pess > max_regret_pess:
                max_regret_pess = diff_pess
        return max_regret_opt, max_regret_pess

    # Function that Checks stability of the matches of players at time t
    def check_stability(self, time):
        # Go through matching of each player at time t
        for p in self.players_dict.keys():

            curr_player = self.players_dict[p]
            # If player did not get to pull any arm at this time, match unstable
            if time not in curr_player.successful_pulls.keys():
                self.blocking_pair = (p, None)
                return 0

            # If player did get to pull an arm
            successful_arm_index = curr_player.successful_pulls[time]
            successful_arm = self.arms_dict[successful_arm_index]
            preferred_players = []
            # Go through preference list of successful_arm and add all preferred players to list
            for alternate_p_index in self.arm_preferences[successful_arm_index]:
                if self.check_arm_preference(successful_arm_index, alternate_p_index, p) == alternate_p_index:
                    # Because the way check_preference is structured, need to check if they are same index
                    if alternate_p_index != p:
                        preferred_players.append(alternate_p_index)

            # Now go through preferred players and check if they prefer successful_arm to their current matching
            for a_p_index in preferred_players:

                # If it couldn't pull any arm at current time, then it'd prefer anything over nothing
                preferred_player = self.players_dict[a_p_index]
                if time not in preferred_player.successful_pulls.keys():
                    self.blocking_pair = (a_p_index, None)
                    return 0
                ap_arm_index = preferred_player.successful_pulls[time]

                # If the alternate player also prefers sucessful_arm over their current section, then match unstable
                if self.check_player_preference(a_p_index, ap_arm_index, successful_arm_index) == successful_arm_index:
                    # Because the way check_preference is structured, need to check if they are same index
                    if ap_arm_index != successful_arm_index:
                        self.blocking_pair = (a_p_index, successful_arm_index)
                        return 0
        return 1


