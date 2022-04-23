
class GaleShapely:
    def __init__(self, number_of_proposers, number_of_proposees, proposer_preferences, proposee_preferences):
        self.unmatchedProposers = list(range(number_of_proposers))
        self.proposerMatching = {}
        for i in range(number_of_proposers):
            self.proposerMatching[i] = None

        self.proposeeMatching = {}
        for i in range(number_of_proposees):
            self.proposeeMatching[i] = None

        self.nextProposerChoice = [0] * number_of_proposers
        self.proposerPreferences = proposer_preferences
        self.proposeePreferences = proposee_preferences

    def __str__(self):

        print()
        print("The men's preferences are")
        for i in range(len(self.proposerPreferences)):
            print(f"proposer {i}", end=": ")
            for idx in range(len(self.proposerPreferences[i]) - 1):
                print(f"Proposee {self.proposerPreferences[i][idx]} > ", end="")
            print(f"Proposee {self.proposerPreferences[i][idx + 1]}")
            print()
        print()
        print("The women preferences are")
        for j in range(len(self.proposeePreferences)):
            print(f"Proposee {j}", end=": ")
            for idx in range(len(self.proposeePreferences[j]) - 1):
                print(f"proposer {self.proposeePreferences[j][idx]} > ", end="")
            print(f"proposer {self.proposeePreferences[j][idx + 1]}")
            print()
        print()
        # Now print out the enagements
        for i in self.proposerMatching.keys():
            print(f"Proposer {i} should Marry proposee {self.proposerMatching[i]}")
        return " "


    def run(self):
        # While unmatched proposer exists
        while self.unmatchedProposers:
            # Pick an arbitrary proposer
            proposerIndex = self.unmatchedProposers[0]
            proposerPreference = self.proposerPreferences[proposerIndex]

            # Find a proposee to propose to
            proposeeIndex = proposerPreference[self.nextProposerChoice[proposerIndex]]

            # Find current proposee matching
            proposeePreference = self.proposeePreferences[proposeeIndex]
            currentProposeeMatch = self.proposeeMatching[proposeeIndex]

            # Run Deferred Acceptance
            if currentProposeeMatch is None:
                # If there is no matching, any matching is desirable
                self.proposeeMatching[proposeeIndex] = proposerIndex
                self.proposerMatching[proposerIndex] = proposeeIndex

                # Update next choice for proposer
                self.nextProposerChoice[proposerIndex] = self.nextProposerChoice[proposerIndex] + 1

                # Remove proposer from unmatched list
                self.unmatchedProposers.pop(0)
            else:
                # There exists a current matching
                # Check the preferences of the current matching to the new proposer
                currentIndex = proposeePreference.index(currentProposeeMatch)
                newIndex = proposeePreference.index(proposerIndex)

                # Accept the proposal if new has higher preference
                if currentIndex > newIndex:
                    # New match found for proposee, update lists accordingly
                    self.proposeeMatching[proposeeIndex] = proposerIndex
                    self.proposerMatching[proposerIndex] = proposeeIndex
                    self.nextProposerChoice[proposerIndex] = self.nextProposerChoice[proposerIndex] + 1
                    self.unmatchedProposers.pop(0)
                    self.unmatchedProposers.insert(0, currentProposeeMatch)
                else:
                    self.nextProposerChoice[proposerIndex] = self.nextProposerChoice[proposerIndex] + 1

        return self.proposerMatching


