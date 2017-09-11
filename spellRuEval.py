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


def generateTestSample(candidateManager):
	sentences = readCorrectSentences("test_sample_testset.txt")
	allCandidates = candidateManager.readCandidates("candidates_test.txt")
	sentences = []
	for candidate in allCandidates:
		sentences.append(candidateManager.rangeCandidates(candidate))
	return sentences
	
def compareSents(candidate, realSent):
	isRight = True
	if len(candidate) == len(realSent):		
		for j in range(len(candidate)):
			if candidate[j] != realSent[j]:
				isRight = False
				break
	else:
		isRight = False
	return int(isRight)

def main():
	lm = KenLm("text.arpa", 3)
	rangeProcessor = RangeProcessor(lm)
	
	allCandidates = rangeProcessor.readCandidates("candidates.txt")
	rangedCandidates = []
	for candidate in allCandidates:
		rangedCandidates.append(rangeProcessor.rangeCandidates(candidate))

	correctSents = readCorrectSentences("corrected_sents.txt")

	fp = FeatureProcessor(lm)

	XTrain = []
	for i, sent in enumerate(rangedCandidates):
		for candidate in sent:
			XTrain.append(candidate[1:]+[len(candidate[0])])	
	
	XTrain += fp.generateFeatures(correctSents)

	YTrain = collectYLabels(rangedCandidates, correctSents)

	#print(XTrain)
	lr = LogisticRegression()
	lr.fit(XTrain, YTrain)

	testCandidates = rangeProcessor.readCandidates("candidates_test.txt")
	testRangedCandidates = []
	for candidate in testCandidates:
		testRangedCandidates.append(rangeProcessor.rangeCandidates(candidate))

	correctSents = readCorrectSentences("test_sample_testset.txt")
	
	XTest = []
	for i, sent in enumerate(testRangedCandidates):
		for candidate in sent:
			XTest.append(candidate[1:]+[len(candidate[0])])	

	YTest = readCorrectSentences("corr_sample_testset.txt")

	#вывод, метрики
	corrSentsNumber = 0
	resFile = open("test_result.txt", "w", encoding = "utf-8")
	for i, sent in enumerate(testRangedCandidates):
		result = []
		probToResult = {}
		for candidate in sent:
			result.append(lr.predict_proba([candidate[1:]+[len(candidate[0])]])[0][1])
			probToResult[result[-1]] = len(result) - 1
		result = sorted(result, reverse=True)
		#for res in result:
		resFile.write(" ".join(sent[probToResult[result[0]]][0])+"\n")
		corrSentsNumber += compareSents(sent[probToResult[result[0]]][0], YTest[i])
	print("number of corrected sentences: ", corrSentsNumber)
	print("accuracy: ", float(corrSentsNumber)/len(correctSents))


if __name__ == "__main__":
    main()