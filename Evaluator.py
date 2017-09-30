from collections import defaultdict

class BaseEvaluator:

	def rangeAnswers(self, sentences, scores):
		rangedAnswers = []
		for sentence, score in zip(sentences, scores):
			rangedAnswers.append(sorted(zip(sentence, score), reverse=True, key = lambda item: item[1]))
		return rangedAnswers

	def getStatistics(self, sentences, scores, correctSents):
		tops = defaultdict(int)
		rangedSentences = self.rangeAnswers(sentences, scores)
		#print("rangedSents ", rangedSentences[:2])
		for candidates, correctSent in zip(rangedSentences, correctSents):
			#print("candidates", candidates)
			for i, (candidate, score) in enumerate(candidates):
				print(candidate, correctSent)
				if self.compareSents(candidate[0], correctSent):
					tops[i] += 1
		return tops

	def compareSents(self, candidate, correctSentence):
		isRight = True
		if len(candidate) == len(correctSentence):		
			for j in range(len(candidate)):
				if candidate[j] != correctSentence[j]:
					isRight = False
					break
		else:
			isRight = False
		return int(isRight)