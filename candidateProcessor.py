import MorphoPy

class CandidateProcessor:

	def __init__(self, wordVarCount = 10):
		self.wordVarCount = wordVarCount
		self.lp = MorphoPy.Engine().CreateLanguageProcessor( "Russian" )

	def buildCandidatesForCorpus(self, pathToCorpus):
		allCandidates = []
		with open(pathToCorpus, "r", encoding="utf-8") as f:
			i = 0
			for line in f:
				sentence = line.strip()
				print(i)
				candidates = self.buildCandidatesForSentence( sentence )
				allCandidates.append( candidates )
				i += 1
		self.g.close()
		return allCandidates

	def buildCandidatesForSentence(self, sentence):
		words = nltk.word_tokenize(sentence)
		candidates = []
		for word in words:
			curCandidates = self.lp.SuggestExp3( word, self.wordVarCount )
			#если ничего не можем предложить, используем исходный вариант
			if len(curCandidates) == 0:
				curCandidates = [[word], 0]
			#если слово есть в словаре и не попало в выдачу SuggestExp3, добавляем его в список кандидатов
			elif curCandidates[0][1] != 0 and self.lp.CheckWord(word)[1]:
				curCandidates = [[word], 0]
			candidates.append( curCandidate )
		return candidates
				
	def writeCandidates(self, candidates, path):
		with open(path, "w", encoding="utf-8") as f:
			for candidate in candidates:
				f.write("#\n")
				for i, (wordCandidates, wordPenalties) in enumerate(candidate):
					for j, word in enumerate(wordCandidates):
						f.write(word + "\n")
					f.write("\n")

def main():
	candidateProcessor = CandidateProcessor()
	candidates = candidateProcessor.buildCandidatesForCorpus("source_sents.txt")
	candidateProcessor.writeCandidates(candidates, "candidates.txt")
	

if __name__ == "__main__":
    main()