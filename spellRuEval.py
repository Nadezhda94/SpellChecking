from rangeProcessor import KenLm, Hypothesis, RangeProcessor
from featureProcessor import FeatureProcessor
import nltk
from sklearn.linear_model import LogisticRegression
import sys
from BaseModel import BaseModel
from Evaluator import BaseEvaluator





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

def main():
	args = sys.argv[1:]
	if len(args) != 5:
		sys.exit("Использование: evaluate.py languageModel sourceCandidateFile sourceCorrectFile testCandidateFile testCorrectFile\n"
        		"languageModel: языковая модель\n"
        		"sourceCandidateFile: файл c исправлениями-кандидатами для обучающей выборки\n"
        		"sourceCorrectFile: файл с эталонными исправлениями для обучающей выборки\n"
        		"testCandidateFile: файл с исправлениями-кандидатами для тестовой выборки\n"
        		"testCorrectFile: файл с эталонными исправлениями для тестовой выборки\n")
	languageModel, sourceCandidateFile, sourceCorrectFile, testCandidateFile, testCorrectFile = args
	lm  = KenLm(languageModel, 3)
	rangeProcessor = RangeProcessor(lm)
	fp = FeatureProcessor(lm)

	sourceXTrain = []
	sourceXTest = []

	with open("source_sents.txt", "r", encoding="utf-8") as f:
		for line in f:
			sourceXTrain.append(nltk.word_tokenize(line.strip("\n")))

	with open("test_sample_testset.txt", "r", encoding="utf-8") as f:
		for line in f:
			sourceXTest.append(nltk.word_tokenize(line.strip("\n")))


	model = BaseModel(lm, LogisticRegression())
	#XTrain, YTrain, XTest, YTest = model.makeSample(sourceCandidateFile, sourceCorrectFile, testCandidateFile, testCorrectFile)
	rangedCandidates = rangeProcessor.rangeCandidatesForCorpus(sourceCandidateFile)
	correctSents = readCorrectSentences(sourceCorrectFile)
	
	#формируем обучающую выборку
	XTrain = fp.generateFeaturesForSents(rangedCandidates, sourceXTrain)
	XTrain += fp.generateFeaturesForCorrectSents(correctSents)
	YTrain = collectYLabels(rangedCandidates, correctSents)

	print(XTrain[:10])

	# формируем тестовую выборку
	testRangedCandidates = rangeProcessor.rangeCandidatesForCorpus(testCandidateFile)

	XTest = []
	for sent, sourceSent in zip(testRangedCandidates, sourceXTest):
		XTest.append(fp.generateFeaturesForCandidates(sent, sourceSent))
	YTest = readCorrectSentences(testCorrectFile)
	model.fit(XTrain, YTrain)
	scores = model.predict(XTest)

	simpleScores = [[sum(candidate[1:]) for candidate in sent] for sent in XTest]

	evaluator = BaseEvaluator()
	tops = evaluator.getStatistics(testRangedCandidates, scores, YTest)

	corrSentsNumberTop1 = tops[0]
	corrSentsNumberTopN = sum([tops[i] for i in tops])
	print("number of top1 corrected sentences: ", corrSentsNumberTop1)
	print("number of topN corrected sentences: ", corrSentsNumberTopN)
	print("accuracy top1: ", float(corrSentsNumberTop1)/len(XTest))
	print("accuracy topN: ", float(corrSentsNumberTopN)/len(XTest))


if __name__ == "__main__":
    main()