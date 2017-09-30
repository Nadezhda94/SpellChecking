import sys
from evaluate import extract_words, make_corrections_data, output_differences
from collections import defaultdict


class CompareProcessor:


	def __init__(self, sourceSents, suggestExpResults, gicrResults, correstSents):
		self.sourceSents = self.readSentences(sourceSents)
		self.suggestExpResults = self.readSentences(suggestExpResults)
		self.gicrResults = self.readSentences(gicrResults)
		self.correstSents = self.readSentences(correstSents)


	def readSentences(self, path):	
		sentences = []
		with open(path, "r", encoding="utf-8") as f:
			sentences = [extract_words(line.strip().strip('\ufeff'))
						for line in f.readlines() if line.strip().strip('\ufeff') != ""]
		return sentences

	def compare(self):
		sourceCorrections, suggestExpCorrections = \
		make_corrections_data(self.sourceSents, self.correstSents, self.suggestExpResults)

		sourceCorrections, gicrCorrections = \
		make_corrections_data(self.sourceSents, self.correstSents, self.gicrResults)
		suggestFalseNegatives = defaultdict(list)
		gicrFalseNegatives = defaultdict(list)
		print(suggestExpCorrections)

		for (num, i, j), gicrCorrection in gicrCorrections.items():
			sourceCorrection = sourceCorrections.get((num, i, j))

			if sourceCorrection != None and sourceCorrection == gicrCorrection:
				suggestExpCorrection = suggestExpCorrections.get((num, i, j))
				if gicrCorrection != suggestExpCorrection:
					if suggestExpCorrection == None:
						suggestExpCorrection = ()
					print(suggestExpCorrection, gicrCorrection)
					suggestFalseNegatives[num].append(((i, j), suggestExpCorrection, sourceCorrection))

		for (num, i, j), suggestExpCorrection in suggestExpCorrections.items():
			sourceCorrection = sourceCorrections.get((num, i, j))

			if sourceCorrection != None and sourceCorrection == suggestExpCorrection:
				gicrCorrection = gicrCorrections.get((num, i, j))
				if gicrCorrection != suggestExpCorrection:
					if gicrCorrection == None:
						gicrCorrection = ()
					gicrFalseNegatives[num].append(((i, j), gicrCorrection, sourceCorrection))
		with open("diff_suggest_mistakes.txt", "w", encoding="utf-8") as f,\
				open("diff_gicr_mistakes.txt", "w", encoding="utf-8") as g:
			for num, sent in enumerate(self.sourceSents):
				curSuggestFalseNegatives = suggestFalseNegatives[num]
				curGicrFalseNegatives = gicrFalseNegatives[num]
				if (len(curSuggestFalseNegatives) != 0):
					for (i, j), suggestExpCorrection, sourceCorrection in curSuggestFalseNegatives:
						if len(suggestExpCorrection) == 0:
							suggestExpCorrection = sent[i:j]
						f.write(" ".join(sent[i:j]) + "\t" + " ".join(suggestExpCorrection) +"\t" + \
							" ".join(sourceCorrection ) + "\n")
					f.write("\n")
				if (len(curGicrFalseNegatives) != 0):
					for (i, j), gicrCorrection, sourceCorrection in curGicrFalseNegatives:
						if len(gicrCorrection) == 0:
							gicrCorrection = sent[i:j]
						g.write(" ".join(sent[i:j]) + "\t" + " ".join(gicrCorrection)+"\t" + \
							" ".join(sourceCorrection ) + "\n")
					g.write("\n")




		"""
		for (num, i, j), suggestExpCorrection in suggestExpCorrections.items():
			sourceCorrection = sourceCorrections.get((num, i, j))
			if sourceCorrection is None:
				false_positives[num].append(((i, j), suggestExpCorrection))
			elif sourceCorrection != suggestExpCorrection:
				miscorrections[num].append(((i, j), suggestExpCorrection, sourceCorrection))
		for (num, i, j), sourceCorrection in sourceCorrections.items():
			suggestExpCorrection = suggestExpCorrections.get((num, i, j))
			if suggestExpCorrection is None:
				false_negatives[num].append(((i, j), suggestExpCorrection))
		"""

		#output_differences("diff.txt", self.sourceSents, self.correstSents, self.suggestExpResults,
		#	sourceCorrections, suggestExpCorrections)




def main():
	args = sys.argv[1:]
	cp = CompareProcessor(args[0], args[1], args[2], args[3])

	cp.compare()


if __name__ == "__main__":
	main()