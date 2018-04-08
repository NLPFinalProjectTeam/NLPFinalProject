
import os, sys

KNOWLEDGE_BASE_PATH = "../knowledge_base/"


def load_knowledge(psg):
	knowledge = {}
	f = open(KNOWLEDGE_BASE_PATH + psg, "r")
	lines = f.readlines()

	for line in lines:
		question, answer, qtype = line.strip().split("\t")
		if (question, qtype) not in knowledge:
			knowledge[(question, qtype)] = answer

	f.close()
	return knowledge


def get_type(q):

	"""
		TODO: use heuristics to get question type.

	"""
	pass


def main(argv):

	psg = argv[1]
	question_file = argv[2]

	knowledge = load_knowledge(psg)

	qf = open(question_file, "r")
	questions = qf.readlines()

	for q in questions:
		q = q.strip().lower()
		qtype = get_type(q)
		if (q, qtype) in knowledge:
			# Temporarily just print the answer
			print (knowledge(q, qtype) + "\n")
			continue

		# similarity matching, use word2vec TODO
		for tup, ans in 




if __name__ == '__main__':
	main(sys.argv)