#!/usr/bin/env python3
import os, sys
import numpy as np
import codecs
import string

from indexing.build_index import segment_into_sentences, build_index
from indexing.retrieve_sentences import retrieve

from nltk.stem.porter import *
from pycorenlp import StanfordCoreNLP

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
    elif q[0] == "when":
        return "WHEN"
    elif q[0] == "where":
        return "WHERE"

    return "exception"



def main(argv):
    psg = argv[1]
    question_file = argv[2]

    knowledge = load_knowledge(psg)

    qf = codecs.open(question_file, encoding="utf-8")
    # questions = qf.readlines()

    translator = str.maketrans('', '', string.punctuation)
    stanford = StanfordCoreNLP('http://localhost:9000')

    for question in qf:
        question = question.strip().lower().translate(translator)
        qtype = get_type(question)

        if (question, qtype) in knowledge:
            # Temporarily just print the answer
            # print question, qtype
            print(knowledge[(question, qtype)])
            continue

        # Retrieve
        num_of_returns = 5
        retrieve_result = retrieve(psg, question, num_of_returns)


        # error handling
    	if retrieve_result = None or len(retrieve_result) == 0:
    		print ("THIS IS AN EASTER EGG.")
    		continue

        answer = from_retrieve(retrieve_result, question, qtype, stanford)
        print (answer)
    # end for

    stanford.close()
    qf.close()


def from_retrieve(retrieve_result, question, qtype, stanford):
    """
        [(score, sentence),...]
    """


    sent = retrieve_result[0][1] # temporary choice

    if qtype == "YN":
        answer = get_answer_yn(sent, question, stanford)
    elif qtype == "HOW":
        answer = get_answer_how(sent, question, stanford)
    elif qtype == "WHY":
        answer = get_answer_why(sent, question, stanford)
    elif qtype == "WHEN":
        answer = get_answer_when(sent, question, stanford)
    elif qtype == "WHO":
        answer = get_answer_who(sent, question, stanford)
    elif qtype == "WHAT":
        answer = get_answer_what(sent, question, stanford)
    elif qtype == "WHERE":
        answer = get_answer_where(sent, question, stanford)


    if answer != None:
        return answer

    # last choice, return the most relevant sentence
    return sent


def get_answer_yn(sent, question, stanford):


    """
        TODO: given a sentence and a question, judge yes/no

    """
    stemmer = PorterStemmer()

    tokens_sent = stanford.annotate(sent,
                                    properties={
                                        'annotators': 'pos'
                                        'outputFormat': 'json'
                                        'timeout': 1000,
                                    })['sentences'][0]['tokens']

    tokens_ques = stanford.annotate(question,
                                    properties={
                                        'annotators': 'pos'
                                        'outputFormat': 'json'
                                        'timeout': 1000,
                                    })['sentences'][0]['tokens']



    sent = set([stemmer.stem(t['originalText']) for t in tokens_sent if is_keyword(t['pos'])])
    question = set([stemmer.stem(t['originalText']) for t in tokens_ques if is_keyword(t['pos'])])
    intersect = sent.intersection(question)

    if len(intersect) < len(sent) and len(intersect) < len(question):
        return "No"
    else:
        return "Yes"

def get_answer_how(sent, question, stanford):
    """
        TODO: furthur split into "how many", "how much", etc.
    """

    second = question.strip().lower().split()[1]
    tokens = stanford.annotate(sent,
    							properties={
    								'annotators': 'ner',
    								'outputFormat': 'json',
    								'timeout': 2000,
    							})["sentences"][0]["tokens"]

    if second == "much":
    	money = group_by(tokens, ["MONEY"], question)
    	if len(money) > 0:
    		return money[0]
    elif second == "many":
    	numbers = group_by(tokens, ["NUMBER"], question)
    	if len(numbers) > 0:
    		return numbers[0]

    return sent

def get_answer_why(sent, question, stanford):
    return sent

def get_answer_when(sent, question, stanford):
    
    """
        TODO: solve WHEN questions



        USE STANFORD NER.
    """

    tokens = stanford.annotate(sent,
    							properties={
    								'annotators': 'ner',
    								'outputFormat': 'json',
    								'timeout': 2000,
    							})["sentences"][0]["tokens"]

    date_time = group_by(tokens, ["DATE", "TIME"])
    if len(date_time) == 1:
    	return date_time[0]

    return sent 

    # return naive_method(sent, question)


def get_answer_what(sent, question, stanford):


    """
        TODO: solve WHAT questions


        USE STANFORD NER.
    """

    tokens = stanford.annotate(sent,
    							properties={
    								'annotators': 'ner',
    								'outputFormat': 'json',
    								'timeout': 2000,
    							})["sentences"][0]["tokens"]


    titles = group_by(sent, ["TITLE"], question)
    if len(titles) > 0:
    	return titles[0]


    organizations = group_by(sent, ["ORGANIZATION"], question)
    if len(organizations) > 0:
    	return organizations[0]


    return sent
    # return naive_method(sent, question)


def get_answer_who(sent, question, stanford):

    """
        TODO: solve WHO questions

        USE STANFORD NER.

    """

    tokens = stanford.annotate(sent,
                                properties={
                                    'annotators': 'ner',
                                    'outputFormat': 'json',
                                    'timeout': 2000,
                                })["sentences"][0]["tokens"]

    # persons = []
    # person = []
    # for token in annotation["sentences"][0]["tokens"]:
        
    #     if token["ner"] == "PERSON":
    #         person.append(token["originalText"])

    #     else:
    #         if len(person) > 0:
    #             p = " ".join(person).strip()
    #             if p not in question.lower():
    #                 persons.append(p)
    #         person = []

    # if len(persons) > 0:
    #     return persons[0]

    persons = group_by(tokens, ["PERSON"], question)
    if len(persons) > 0:
    	return persons[0]
    
    return sent
    #return naive_method(sent, question)

def get_answer_where(sent, question, stanford):

    """
        TODO: solve WHERE questions

        USE STANFORD NER.

    """
    tokens = stanford.annotate(sent,
                                properties={
                                    'annotators': 'ner',
                                    'outputFormat': 'json',
                                    'timeout': 2000,
                                })["sentences"][0]["tokens"]

    locations = group_by(tokens, ["LOCATION, CITY, COUNTRY"], question)
    if len(locations) > 0:
    	return locations[0]


    organizations = group_by(sent, ["ORGANIZATION"], question)
    if len(organizations) > 0:
    	return organizations[0]


    return sent



def naive_method(sent, question, stanford):

    """
        A naive way of generation answer, by using set-minus of sentence and question

        Not used anymore.
    """

    translator = str.maketrans('', '', string.punctuation)
    stemmer = PorterStemmer()
    sent = sent.strip().lower().translate(translator).split()
    sent_stemmed = [stemmer.stem(w) for w in sent]
    question = question.strip().lower().translate(translator).split()
    question_stemmed = [stemmer.stem(w) for w in question]

    recover = {}
    for i in range(len(sent)):
        recover[sent_stemmed[i]] = sent[i]

    for w in question_stemmed:
        if w in sent_stemmed:
            sent_stemmed.remove(w)

    return " ".join([recover[w] for w in sent_stemmed]).strip()




def is_keyword(pos_tag):
    pos_tag = pos_tag.upper()
    if pos_tag.startswith("V") or pos_tag.startswith("N") or pos_tag.startswith("J"):
        return True

    return False


def group_by(tokens, ner_tags, question=""):
	"""
		Group by an NER-tag
	"""

	results = []
    temp = []
    for token in tokens:
        
        if token["ner"].upper() in ner_tags:
            temp.append(token["originalText"])

        else:
            if len(temp) > 0:
                p = " ".join(temp).strip()
                if p.lower() not in question.lower():
                    persons.append(p)
            temp = []


if __name__ == '__main__':
    main(sys.argv)
