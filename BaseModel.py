from rangeProcessor import KenLm, Hypothesis, RangeProcessor
from featureProcessor import FeatureProcessor
import nltk
from sklearn.linear_model import LogisticRegression

def readCorrectSentences(path):
	sentences = []
	with open(path, "r", encoding="utf-8") as f:
		for line in f:
			sentences.append(nltk.word_tokenize(line.strip()))
	return sentences


def collectYLabels(sentences, correctSents):
	Y = []
	for i, sent in enumerate(sentences):
		result = []
		for candidate in sent:		
			isRight = True
			if len(candidate) == len(correctSents[i]):			
				for j in range(len(candidate)):
					if candidate[j] != correctSents[i][j]:
						isRight = False
						break
			else:
				isRight = False
			Y.append(int(isRight))
	for sent in correctSents:		
		Y.append(1)
	return Y


class BaseModel:

	def __init__(self, languageModel, classifier):
		self.lm  = languageModel
		self.rangeProcessor = RangeProcessor(self.lm)
		self.fp = FeatureProcessor(self.lm)
		self.classifier = classifier


	def makeSample(self, sourceCandidateFile, sourceCorrectFile, testCandidateFile, testCorrectFile):	
		rangedCandidates = self.rangeProcessor.rangeCandidatesForCorpus(sourceCandidateFile)
		correctSents = readCorrectSentences(sourceCorrectFile)
		
		#формируем обучающую выборку
		XTrain = self.fp.generateFeaturesForSents(rangedCandidates)
		XTrain += self.fp.generateFeaturesForCorrectSents(correctSents)
		YTrain = collectYLabels(rangedCandidates, correctSents)

		#формируем тестовую выборку
		testRangedCandidates = self.rangeProcessor.rangeCandidatesForCorpus(testCandidateFile)

		XTest = []
		for sent in testRangedCandidates:
			XTest.append(self.fp.generateFeaturesForCandidates(sent))
		YTest = readCorrectSentences(testCorrectFile)
		return XTrain, YTrain, XTest, YTest

	def fit(self, XTrain, YTrain):
		self.classifier.fit(XTrain, YTrain)

	def predict(self, testRangedCandidates):
		scores = []
		for i, sent in enumerate(testRangedCandidates):
			result = []
			for candidate in sent:
				result.append(self.classifier.predict_proba([candidate])[0][1])
			scores.append(result)
		return scores

	


		