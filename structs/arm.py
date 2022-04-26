
class Arm:

    def __init__(self, Index, ArmsList=None, PlayerList=None):
        self.index = Index  # Index of the arm
        self.pulls = {}  # Dict to keep track of successful arms pulls of the player
        self.pull_requests = {}
        self.arms_list = {}
        self.players_list = {}

        if ArmsList is not None:
            for a in ArmsList:
                self.arms_list[a.index] = a

        if PlayerList is not None:
            for p in PlayerList:
                self.players_list[p.index] = p

    def initialize_player_and_arms_list(self, PlayerList, ArmsList):
        self.players_list = PlayerList
        self.arms_list = ArmsList

    def request_pull(self, player, time):
        if time not in self.pull_requests.keys():
            self.pull_requests[time] = [player.index]
        else:
            self.pull_requests[time].append(player.index)

    # A function to check preference of arm between p1 and p2
    # Implemented on child class depending on type
    def check_player_preference(self, player1_index, player2_index):
        pass
        #TODO: Implement in child class

    # Function that picks the best player among the incoming requests at time t
    def resolve_pull_requests(self, time):
        pass
        #TODO: Implement in child class