# -*- coding: utf-8 -*- s
import nltk
import copy
import re
import kenlm
import heapq
import numpy as np

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

	def __init__(self, prob, err, candNumbers, prevHypthNumber, isOOV):
		self.prob = prob
		self.candNumbers = candNumbers
		self.err = err
		self.prevHypthNumber = prevHypthNumber
		self.isOOV = isOOV

	def __lt__(self, other):
		return (0.8*self.prob + 0.2*self.err) < (0.8*other.prob + 0.2*other.err)


class RangeProcessor:
	"""
    
    :sentCandidateCount - максимальное число кандидатов
    """

	def __init__(self, languageModel, sentCandidatesCount = 20):
		self.sentCandidatesCount = sentCandidatesCount
		self.lm = languageModel

	def rangeCandidatesForCorpus(self, path):
		allCandidates = self.readCandidates(path)
		rangedCandidates = []
		for candidate in allCandidates:
			rangedCandidates.append(self.rangeCandidates(candidate))
		return rangedCandidates

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

		#список гипотез для каждого слова ограничен параметром 
		hypothesis = [[] for i in range(len(candidates) + 1)]
		hypothesis[0].append(Hypothesis(0, 0, [], -1, 0))
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

					if len(hypothesis[i+1]) < self.sentCandidatesCount:			
						heapq.heappush(hypothesis[i+1],
						 Hypothesis(prob, err, hypths.candNumbers[candIndex:]+[j],l, hypths.err!=0))
					elif len(hypothesis[i+1]) == self.sentCandidatesCount:
						if	hypothesis[i+1][0].prob + hypothesis[i+1][0].err < prob + err:
							heapq.heapreplace(hypothesis[i+1], 
								Hypothesis(prob, err, hypths.candNumbers[candIndex:]+[j], l))
					
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
			allSentences.append([copy.deepcopy(sentence), sentProb, sentErr,  ])
		return allSentences
