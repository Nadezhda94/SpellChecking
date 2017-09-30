

class FeatureProcessor:

	def __init__(self, lm):
		self.lm = lm

	def generateFeaturesForSents(self, candidates, sourceSents):
		candidatesFeatures = []
		for i, (sent, sourceSent) in enumerate(zip(candidates, sourceSents)):
			candidatesFeatures += self.generateFeaturesForCandidates(sent, sourceSent)
		return candidatesFeatures

	def generateFeaturesForCandidates(self, candidates, sourceSent):
		candidatesFeatures = []
		for candidate in candidates:
			candidatesFeatures.append(candidate[1:]+[len(candidate[0]), 
									self.getCorrectedWordCount(candidate, sourceSent)])
		return candidatesFeatures 

	def getCorrectedWordCount(self, candidate, sourceSent):
		return sum([int(candidateWord != sourceWord) 
				for candidateWord, sourceWord in zip(candidate[0], sourceSent)])

	def generateFeaturesForCorrectSents(self, sentences):
		allFeatures = []
		for sent in sentences:
			allFeatures.append(self.generateFeaturesForCorrectSentence(sent))
		return allFeatures

	def generateFeaturesForCorrectSentence(self, sentence):
		return [self.lm.sentScore(" ".join(sentence)), 0, len(sentence), 0]