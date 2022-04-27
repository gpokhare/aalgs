import random
from scipy.stats import bernoulli
from structs.domain import Market
from structs import config
from utils import general_utils
import sys


class ca_ucb:
    def __init__(self, number_of_agents, number_of_arms, beta):
        self.N = number_of_agents
        self.A = number_of_arms
        self.BETA = beta
        self.Mrkt = Market(number_of_players=number_of_agents, number_of_arms=number_of_arms, Beta=self.BETA)


    def run(self):
        player_optimal_regrets = []
        arm_optimal_regrets = []
        player_pessimal_regrets = []
        arm_pessimal_regrets = []
        stability = []

        #DEBUG
        if config.debug:
            general_utils.print_true_state(self)
        # ======================================================================

        for t in range(config.horizon):

            if t % config.debug_steps:
                if config.debug:
                    org_stdout = sys.stdout
                    with open(config.loc + "thompson_log_run_" + str(config.run_number) + "_" + str(config.seed) + ".txt", 'a') as f:
                        sys.stdout = f
                        print("=======================================================================================================================================", flush=True)
                        print(f"TIMESTEP: {t}", flush=True)
                        self.Mrkt.print_player_tracked_thompson()
                        sys.stdout = org_stdout

            if config.debug:
                if t % config.debug_steps == 0:
                    general_utils.print_to_log(f"Time Step: {t}")

            #TODO: change this in market to print out player tracked values, regardless of UCB or thompson, for environment 1 and 2.
            # if t % 5000 == 0:
            #     if config.debug:
            #         org_stdout = sys.stdout
            #         with open(config.loc + "thompson_log_run_" + str(config.run_number) + "_" + str(config.seed) + ".txt",
            #                   'a') as f:
            #             sys.stdout = f
            #             print(
            #                 "=======================================================================================================================================")
            #             print(f"TIMESTEP: {t}")
            #             self.Mrkt.print_player_tracked_thompson()
            #             sys.stdout = org_stdout



            if t % 5000 == 0:
                print(f"Time Step: {t}")


            for i in range(self.N):
                players = list(self.Mrkt.players_dict.values())
                player = players[i]
                arm_to_attempt = None
                if t == 0:
                    player.initialize_belief_tracking(self.A, self.N)
                    arms = list(self.Mrkt.arms_dict.values())
                    arm_to_attempt = arms[random.randint(0, self.A - 1)]
                else:
                    # Draw Dit ~ Ber(Lambda) independetly
                    Dit = bernoulli.rvs(config.Lambda, size=1)[0]
                    if Dit == 0:
                        # DEBUG
                        if config.debug:
                            general_utils.print_to_log(f"Dit 0, update plausible set for player {i}")
                        # ======================================================================
                        # Get the best arm for player
                        arm_to_attempt = player.get_best_arm(t)
                    else:
                        arm_to_attempt = self.Mrkt.arms_dict[player.attempted_pulls[t - 1]]
                # DEBUG
                if config.debug:
                    general_utils.print_to_log(f"Player {player.index} attempting arm {arm_to_attempt.index} at time {t}")
                # ======================================================================
                player.attempt_arm(arm_to_attempt, t)

            # When you have the arms to attempt for all players at current time step, resolve conflicts, pull arm, update UCB
            for a in self.Mrkt.arms_dict.values():

                #DEBUG
                if config.debug:
                    general_utils.print_to_log(f"TIME STEP: {t}, RESOLVING PULL REQ FOR ARM {a.index}")
                # ======================================================================

                winning_player = a.resolve_pull_requests(t)
                if winning_player is not None:
                    winning_player.update_belief(a, self.Mrkt.sample_reward_for_player(winning_player, a))

                    # Depending on algorithm type, arms also need to update UCB for player (Most of the stuff is handled in resolve pull request, this is here only because reward can be sampled from here)
                    if config.player_type == 'unknowing II':
                        reward = self.Mrkt.sample_reward_for_arm(a, winning_player)
                        a.update_belief(winning_player, reward)


            # For analysis purposes
            p_o_r, p_p_r = self.Mrkt.calculate_max_player_regret(t)
            a_o_r, a_p_r = self.Mrkt.calculate_max_arm_regret(t)
            s = self.Mrkt.check_stability(t)

            player_optimal_regrets.append(p_o_r)
            arm_optimal_regrets.append(a_o_r)
            player_pessimal_regrets.append(p_p_r)
            arm_pessimal_regrets.append(a_p_r)
            stability.append(s)
            general_utils.print_stability_to_console(self, t, stability[-1])

            # DEBUG
            if config.debug:
                general_utils.print_current_belief_state(self, t, stability[-1])
            # ======================================================================

        return player_optimal_regrets, player_pessimal_regrets, arm_optimal_regrets, arm_pessimal_regrets, stability
