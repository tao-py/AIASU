class CandidateRanker:

    def rank(self, candidates):

        return sorted(list(set(candidates)), key=len)