

class FeatureProcessor:

	def __init__(self, lm):
		self.lm = lm

	def generateFeatures(self, sentences):
		allFeatures = []
		for sent in sentences:
			allFeatures.append(self.generateFeaturesForSent(sent))
		return allFeatures

	def generateFeaturesForSent(self, sentence):
		return [self.lm.sentScore(" ".join(sentence)), 0, len(sentence)]