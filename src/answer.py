
import os, sys
import numpy as np

KNOWLEDGE_BASE_PATH = "../knowledge_base/"


def load_knowledge(psg):
	knowledge = {}
	f = open(os.path.join(KNOWLEDGE_BASE_PATH, psg), "r")
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
	q = q.strip().lower()
	if q[0] == "what":
		return "what"
	elif q[0] == "how":
		return "how"
	elif q[0] == "who":
		return "who"
	elif q[0] in ["is", "was", "are", "were", "am", "does", "do", "did"]:
		return "yes_no"
	elif q[0] == "why":
		return "why"
	


	return "exception"


def get_sim(q1, q2):
	"""

		TODO: similarity matching, use word2vec/sentence2vec perhaps.

		For now, a simple jaccard is used.


		In final version, will use more advanced methods
	"""
	q1 = set(q1.strip().lower().split())
	q2 = set(q2.strip().lower().split())
	intersect = q1.intersection(b)


	return float(len(intersect)) / (len(q1) + len(q2) - len(intersect))



def exception_answer(psg):
	"""
		TODO: when exception occurs, call this function.

		Now, temporary return the title of the passage.

		Maybe should add an attribute of question type.
	"""
	f = open(os.path.join("../data", psg), "r")
	title = f.readlines[0].strip()
	return title

def main(argv):

	psg = argv[1]
	question_file = argv[2]

	knowledge = load_knowledge(psg)

	qf = open(question_file, "r")
	questions = qf.readlines()

	for question in questions:
		question = question.strip().lower()
		qtype = get_type(q)

		if qtype == "exception":
			print (exception_answer(psg) + "\n")
			continue

		if (question, qtype) in knowledge:
			# Temporarily just print the answer
			print (knowledge(question, qtype) + "\n")
			continue

		max_sim = -float("inf")
		argmax_ans = None
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
		if argmax_ans == None:
			argmax_ans = exception_answer(psg)

		print (argmax_ans + "\n")
	# end for

	qf.close()




if __name__ == '__main__':
	main(sys.argv)