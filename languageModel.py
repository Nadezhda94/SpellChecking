# -*- coding: utf-8 -*- s
import nltk
import copy
import re
import heapq
import kenlm
from sklearn.linear_model import LogisticRegression
import numpy as np
from sklearn.model_selection import cross_val_score

class KenLm:

	def __init__(self, pathToModel, n):
		self.lm = kenlm.Model(pathToModel)
		self.n = n

	def evaluate(self, ngram):
		#prob, length, oov для каждого слова
		return list(self.lm.full_scores(ngram))

	def sentScore(self, sentence):
		return self.lm.score(sentence)


class Hypothesis:

	def __init__(self, prob, err, candNumbers, prevHypthNumber):
		self.prob = prob
		self.candNumbers = candNumbers
		self.err = err
		self.prevHypthNumber = prevHypthNumber

	def __lt__(self, other):
		return (self.prob + self.err) < (other.prob + other.err)


class CandidateManager:
	g = open("res.txt", "w", encoding="utf-8")
	def __init__(self, languageModel, wordVarCount = 10, sentVarCount = 20):
		self.wordVarCount = wordVarCount
		self.sentVarCount = sentVarCount
		#self.lp = MorphoPy.Engine().CreateLanguageProcessor( "Russian" )
		self.lm = languageModel

	def buildCandidatesForCorpus(self, pathToCorpus):
		allCandidates = []
		with open(pathToCorpus, "r", encoding="utf-8") as f:
			i = 0
			for line in f:
				sentence = line.strip()
				print(i)
				candidates = self.buildCandidates( sentence )
				allCandidates.append(candidates)
				i += 1
		self.g.close()
		return allCandidates
				
	def writeCandidates(self, candidates, path):
		with open(path, "w", encoding="utf-8") as f:
			for candidate in candidates:
				f.write("#\n")
				for i, (wordCandidates, wordPenalties) in enumerate(candidate):
					for j, word in enumerate(wordCandidates):
						f.write(word + "\n")
					f.write("\n")

	def readCandidates(self, path):
		allCandidates = []
		with open(path, "r", encoding="utf-8") as f:
			curcSent = []
			curCandidate = []
			for line in f:
				line = line.strip()
				if line == "#":
					if len(curcSent) > 0:
						allCandidates.append(curcSent)
						curcSent = []
				elif len(line) == 0:
					curcSent.append(curCandidate)
					curCandidate = []
				else:
					curCandidate.append(line.split("\t"))
		return allCandidates


	def rangeCandidates(self, candidates):
		"""
		[
		 (
		  [кандидат1 для слова1, кандидат2 для слова1],
		  [штраф за кандидат1, штраф за кандидат2]
		 ), 
		 (
		  [кандидат1 для слова2,],
		  [штраф за кандидат1, штраф за кандидат2]
		  )
		]
		"""	

		allWordsFeatures = []	
		#список гипотез для каждого слова ограничен
		hypothesis = [[] for i in range(len(candidates) + 1)]
		hypothesis[0].append(Hypothesis(0, 0, [], -1))
		for i, wordCandidates in enumerate(candidates):
			candidateFeatures = []
			for l, hypths in enumerate(hypothesis[i]):
				if len(hypths.candNumbers) == self.lm.n - 1:
					candIndex = 1
				else:
					candIndex = 0
				
				for j, [word, penalty] in enumerate(wordCandidates):					
					prob = hypths.prob + self.lm.evaluate(
						" ".join([candidates[i - len(hypths.candNumbers) + k][num][0]
						for k, num in enumerate(hypths.candNumbers)]) +" " +word)[-2][0]
					err = hypths.err - int(penalty)
					#print(" ".join([candidates[i - self.lm.n + 2 + k][num] 
					#	for k, num in enumerate(hypths.candNumbers[1:])])+word + str(prob))
					if len(hypothesis[i+1]) < self.sentVarCount:
						
						heapq.heappush(hypothesis[i+1],
						 Hypothesis(prob, err, hypths.candNumbers[candIndex:]+[j],l))
					elif len(hypothesis[i+1]) == self.sentVarCount:
						if	hypothesis[i+1][0].prob + hypothesis[i+1][0].err < prob + err:
							heapq.heapreplace(hypothesis[i+1], 
								Hypothesis(prob, err, hypths.candNumbers[candIndex:]+[j], l))
					
					
		self.g.write(str(allWordsFeatures))
		allSentences = []
		for hyp in hypothesis[-1]:
			curHyp = hyp
			curNumber = 1
			sentence = []
			sentProb = curHyp.prob
			sentErr = curHyp.err
			while (curNumber != len(hypothesis)):
				sentence.append(candidates[-curNumber][curHyp.candNumbers[-1]][0])
				curNumber += 1
				curHyp = hypothesis[-curNumber][curHyp.prevHypthNumber]
			sentence = sentence[::-1]
			allSentences.append([copy.deepcopy(sentence), sentProb, sentErr ])
		return allSentences

	def buildCandidates(self, sentence):
		words = nltk.word_tokenize(sentence)
		candidates = []
		for word in words:
			if self.isWord(word):
				curCandidates = self.lp.SuggestExp3(word, self.wordVarCount)
				if len(curCandidates) == 0:
					curCandidates = [[word], 0]
				elif curCandidates[0][1] != 0 and self.lp.CheckWord(word)[1]:
					curCandidates = [[word], 0]
				candidates.append(curCandidate)
			else:
				candidates.append(([word], [0]))
		return candidates

	def createFeaturesForWord(self, word):
		wordFeatures = []
		if self.isWord(word):
			wordFeatures.append(self.lp.AnalyseWord(word)[0].GetPartOfSpeech())
		else:
			wordFeatures.append(-1)
		return wordFeatures

	def isWord(self, word):
		pattern = "[А-Яа-я]+-?[А-Яа-я]*"
		m = re.match(pattern,word)
		if m != None: 
			if len(word) == m.end():
				return True
		return False

	def getSentScore(self, sentence):
		return self.lm.sentScore(sentence)

def readCorrectSentences(path):
	sentences = []
	with open(path, "r", encoding="utf-8") as f:
		for line in f:
			sentences.append(nltk.word_tokenize(line.strip()))
	return sentences


def generateTrainSample(sentences, candidateManager):
	correctSents = readCorrectSentences("corrected_sents.txt")
	X = []
	Y = []
	for i, sent in enumerate(sentences):
		result = []
		for candidate in sent:
			X.append(candidate[1:]+[len(candidate[0])])			
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
		X.append([candidateManager.getSentScore(" ".join(sent)), 0, len(sent)])
		Y.append(1)
	return X, Y

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
	candidateManager = CandidateManager(KenLm("text.arpa", 3))
	#candidates = candidateManager.buildCandidatesForCorpus("source_sents.txt")
	#candidateManager.writeCandidates(candidates, "candidates.txt")
	
	allCandidates = candidateManager.readCandidates("candidates.txt")
	sentences = []
	for candidate in allCandidates:
		sentences.append(candidateManager.rangeCandidates(candidate))

	X, Y = generateTrainSample(sentences, candidateManager)
	lr = LogisticRegression()
	lr.fit(X, Y)
	sentences = generateTestSample(candidateManager)
	Y_True = readCorrectSentences("corr_sample_testset.txt")
	corrSentsNumber = 0
	resFile = open("test_result.txt", "w", encoding = "utf-8")
	for i, sent in enumerate(sentences):
		result = []
		probToResult = {}
		for candidate in sent:
			result.append(lr.predict_proba([candidate[1:]+[len(candidate[0])]])[0][1])
			probToResult[result[-1]] = len(result) - 1
		result = sorted(result, reverse=True)
		#for res in result:
		resFile.write(" ".join(sent[probToResult[result[0]]][0])+"\n")
		corrSentsNumber += compareSents(sent[probToResult[result[0]]][0], Y_True[i])
	print("number of corrected sentences: ", corrSentsNumber)
	print("accuracy: ", float(corrSentsNumber)/len(sentences))
	

if __name__ == "__main__":
    main()