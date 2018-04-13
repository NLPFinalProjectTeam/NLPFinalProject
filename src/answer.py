#!/usr/bin/env python3
import os, sys
import numpy as np
import codecs

KNOWLEDGE_BASE_PATH = "../knowledge_base/"


def load_knowledge(psg):
    knowledge = {}
    try:
        f = codecs.open(os.path.join(KNOWLEDGE_BASE_PATH, "generate_"+psg), encoding="utf-8")
    except FileNotFoundError:
        return knowledge

    # lines = f.readlines()

    for line in f:
        qtype, question, answer = line.strip().split("\t")
        question = question.strip().lower().rstrip('?:!.,;')
        if (question, qtype) not in knowledge:
            knowledge[(question, qtype)] = answer

    f.close()
    return knowledge


def get_type(q):
    """
        TODO: use heuristics to get question type.

    """
    q = q.strip().lower().split()

    # print q[0]

    if q[0] == "what":
        return "WHAT"
    elif q[0] == "how":
        return "HOW"
    elif q[0] == "who":
        return "WHO"
    elif q[0] in ["is", "was", "are", "were", "am", "does",
                  "do", "did", "didn't", "isn't", "aren't",
                  "weren't", "don't", "wasn't"]:
        return "YN"
    elif q[0] == "why":
        return "WHY"

    return "exception"


def get_sim(q1, q2):
    """

        TODO: similarity matching, use word2vec/sentence2vec perhaps.

        For now, a simple jaccard is used.


        In final version, will use more advanced methods
    """
    q1 = set(q1.strip().lower().split())
    q2 = set(q2.strip().lower().split())
    intersect = q1.intersection(q2)

    return float(len(intersect)) / (len(q1) + len(q2) - len(intersect))


def exception_answer(psg):
    """
        TODO: when exception occurs, call this function.

        Now, temporary return the title of the passage.

        Maybe should add an attribute of question type.
    """
    f = codecs.open(psg, encoding="utf-8")
    title = f.readlines()[0].strip()
    return title


def main(argv):
    psg = argv[1]
    question_file = argv[2]

    knowledge = load_knowledge(psg)

    # print knowledge

    qf = codecs.open(question_file, encoding="utf-8")
    # questions = qf.readlines()

    for question in qf:
        question = question.strip().lower().rstrip('?:!.,;')
        qtype = get_type(question)

        # print qtype

        if qtype == "exception":
            print(exception_answer(psg))
            continue

        if (question, qtype) in knowledge:
            # Temporarily just print the answer
            # print question, qtype
            print(knowledge[(question, qtype)])
            continue

        max_sim = -float("inf")
        argmax_ans = None
        for tup, ans in knowledge.items():
            q, t = tup[0], tup[1]
            if qtype != t:
                continue

            similarity = get_sim(q, question)
            # print similarity
            if similarity > max_sim:
                max_sim = similarity
                argmax_ans = ans

        # end for
        # Temporarily just print the answer
        if argmax_ans == None:
            argmax_ans = exception_answer(psg)

        print(argmax_ans)
    # end for

    qf.close()


if __name__ == '__main__':
    main(sys.argv)
