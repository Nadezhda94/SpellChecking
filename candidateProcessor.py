import MorphoPy
import nltk

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
		return allCandidates

	def buildCandidatesForSentence(self, sentence):
		words = nltk.word_tokenize(sentence)
		candidates = []
		for word in words:
			curCandidates = self.lp.SuggestExp3( word, self.wordVarCount )
			
			#если ничего не можем предложить, используем исходный вариант
			if len(curCandidates[0]) == 0:
				curCandidates = [[word], 0]
			#если слово есть в словаре и не попало в выдачу SuggestExp3, добавляем его в список кандидатов
			elif curCandidates[1][0] != 0 and self.lp.CheckWord(word)["result"]:
				curCandidates = [[word], 0]
			candidates.append( curCandidates )
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
	args = sys.argv[1:]
	if len(args) != 2:
        sys.exit("Использование: candidateProcessor.py source_file candidate_file\n"
                 "source_file: исходный файл c предложениями\n"
                 "candidate_file: выходной файл с кандидатами\n"
                 )
    source_file, candidate_file = args
	candidateProcessor = CandidateProcessor()
	candidates = candidateProcessor.buildCandidatesForCorpus("source_sents.txt")
	candidateProcessor.writeCandidates(candidates, "candidates.txt")
	