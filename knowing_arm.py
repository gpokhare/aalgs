from structs.arm import Arm
from structs import config
from utils import general_utils
class KnowingArm(Arm):

    def __init__(self, Index, ArmsList=None, PlayerList=None, PreferenceOrder=None):

        self.preference = PreferenceOrder
        super().__init__(Index, ArmsList, PlayerList)

    # Function that sets the preference order for self
    def set_preference_order(self, preference_order):
        self.preference = preference_order

    # Function that checks which player is more preferred for self
    def check_player_preference(self, player1_index, player2_index):
        for i in range(len(self.preference)):
            if self.preference[i] == player2_index:
                return player2_index
            if self.preference[i] == player1_index:
                return player1_index

    # Function that picks the best player among the incoming requests at time t
    def resolve_pull_requests(self, time):
        # Check if someone already attempted to pull this arm at time t
        if time not in self.pull_requests.keys():
            if config.debug:
                general_utils.print_to_log("No pull request for this arm at current time. ")
            return None
        else:
            # At least one person has attempted to pull this arm at current time
            best_player_index = self.pull_requests[time][0]
            for current_player in self.pull_requests[time]:
                best_player_index = self.check_player_preference(best_player_index, current_player)
            # Now that you have best player among the pull requests
            self.pulls[time] = best_player_index
            best_player = self.players_list[best_player_index]
            best_player.pull_arm(self, time)

            # If the players do not know the arm preferences, the need to update their preference tracking.
            # This portion of the code takes care of that
            if not config.player_type == 'knowing':
                pull_requests = self.pull_requests[time].copy()
                pull_requests.remove(best_player_index)
                if len(pull_requests) != 0:
                    for _ in pull_requests:
                        p = self.players_list[_]
                        p.lost_conflict(self.index, best_player_index)

                        if config.debug:
                            general_utils.print_to_log(" ")
                            general_utils.print_to_log(f"Player {p.index} lost conflict to Player {best_player.index}")
                            general_utils.print_to_log(" ")
            return best_player

