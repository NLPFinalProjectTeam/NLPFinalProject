
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


def get_sim(q1, q2):
	"""

		TODO: similarity matching, use word2vec perhaps.
	"""
	return 0

def main(argv):

	psg = argv[1]
	question_file = argv[2]

	knowledge = load_knowledge(psg)

	qf = open(question_file, "r")
	questions = qf.readlines()

	for question in questions:
		question = question.strip().lower()
		qtype = get_type(q)
		if (question, qtype) in knowledge:
			# Temporarily just print the answer
			print (knowledge(question, qtype) + "\n")
			continue

		max_sim = -float("inf")
		for tup, ans in knowledge:
			q, t = tup[0], tup[1]
			if qtype != t:
				continue

			similarity = get_sim(q, question)
			if similarity > max_sim:
				max_sim = similarity
				argmax_ans = ans

		# end for
		# Temporarily just print the answer
		print (ans + "\n")
	# end for




if __name__ == '__main__':
	main(sys.argv)