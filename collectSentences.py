import os

def collectConllSentsFromFolder(pathToCorpusFolder, pathToWrite):
	g = open(pathToWrite, "w", encoding="utf-8")

	files = os.listdir(pathToCorpusFolder)
	for file in files:
		if file[-6:] == "conllu":
			collectConllSents(pathToCorpusFolder + file, g)
	#collectConllSents("/Users/hope/Downloads/Russian-annotated-conll17/Russian/ru-common_crawl-001.conllu", 
	#	g)
	#collectConllSents("/Users/hope/Downloads/Russian-annotated-conll17/Russian/ru-common_crawl-002.conllu", 
	#	g)
	#collectConllSents("/Users/hope/Downloads/Russian-annotated-conll17/Russian/ru-common_crawl-003.conllu", 
	#	g)
	#collectConllSents("/Users/hope/Downloads/Russian-annotated-conll17/Russian/ru-wikipedia-001.conllu", 
	#	g)
	#collectConllSents("/Users/hope/Downloads/Russian-annotated-conll17/Russian/ru-wikipedia-002.conllu", 
	#	g)
	#collectConllSents("/Users/hope/Downloads/Russian-annotated-conll17/Russian/ru-wikipedia-003.conllu", 
	#	g)
	#collectConllSents("/Users/hope/Downloads/Russian-annotated-conll17/Russian/ru-wikipedia-004.conllu", 
	#	g)
	#g.close()
	#g = open("/Users/hope/Downloads/Corpus_Russian/2.txt", "w", encoding="utf-8")
	gicrDir = "/Users/hope/Downloads/GOLD_1.2_release"
	files = os.listdir(gicrDir)
	for file in files: 
		collectGICRSents(gicrDir + "/" + file, g)
	g.close()

def collectConllSents(pathToFile, g):
	
	with open(pathToFile, "r", encoding="utf-8") as f:
		for line in f:
			
			if line[0:6] == "# text":
				text = line.split("=")[1].strip()
				g.write(text + "\n")

def collectGICRSents(pathToFile, g):
	with open(pathToFile, "r", encoding="utf-8") as f:
		curSent = ""
		for line in f:
			line = line.strip()
			if len(line)==0:
				if len(curSent) > 0:
					g.write(curSent[:-1] + "\n")
					curSent = ""
			elif line[0] != "T":
				curSent += line.split("\t")[2].strip() + " "

def collectStatSentencesFromDir(corpusPath, outputPath):
	outputFile = open(outputPath, "w", encoding="utf-8")
	files = os.listdir(corpusPath)
	for folder in files:
		if folder[0] != ".":
			for file in os.listdir(corpusPath + "/" + folder):
				if file[0] != ".":
					with open(corpusPath + "/" + folder + "/" + file, "r", encoding="utf-16") as f:
						for line in f:
							outputFile.write(line)
	collectSpellRuEvalSents("corrected_sents.txt", outputFile)
	outputFile.close()

def collectSpellRuEvalSents(pathToSource, outputFile):
	with open(pathToSource, "r", encoding="utf-8") as f:
		for line in f:
			outputFile.write(line.strip("\n"))






#collectConllSentsFromFolder("/Users/hope/Downloads/Russian-annotated-conll17/Russian/",
#	"/Users/hope/Downloads/Corpus_Russian/1.txt")
collectStatSentencesFromDir("/Users/hope/Downloads/StatisticsCorpora", "/Users/hope/Downloads/Corpus_Russian/statFull.txt")