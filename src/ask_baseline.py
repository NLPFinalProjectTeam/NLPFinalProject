#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import io
import random
import os.path
import nltk
import nltk.data

########################### General Info ############################

# input: text of a Wikipedia article, and an integer n
# output: n distinct questions about the article. 
# Questions should be fluent and reasonable
# usage: python ask_baseline.py article.txt nquestions [v]

# This is a brutal, savage and naive baseline implementation.
# Viva la heuristics! 
# It simply splits the article into sentences 
# and uses some hard-coded rules to generate 
# two types of questions: wh-questions and yes-no questions, 
# based on PoS tags.
# Finally, it outputs the number of questions requested, with no 
# evaluation. That is, previous functions may give a list that
# contains more questions than requested, but here we just output 
# the first n questions in that list.

# Some potential fields of improvement:
# 1. use more sophisticated rules
# 2. use CFG parsing based rules instead of PoS only
# 3. resolve references (he, she, they, etc)
# 4. do information extraction on the articles
#    (store information in a file/db for future use)
#    that enables complicated questions
# 5. find existing functions provided by NLTK
#    that can be helpful in question generation

#####################################################################




# Two helper functions that convert an article into 
# a list of list of sentences. Each list contains
# sentences of one paragraph
def get_paragraphs(article_file_name):
    paragraphs = []
    with io.open(article_file_name, 'r', encoding='utf-8')\
         as article:
        for line in article:
            paragraph = line.strip("\r\n")
            if paragraph != "":
                paragraphs.append(paragraph)
    return paragraphs
def split_paragraphs_to_sentences(paragraphs):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return [tokenizer.tokenize(paragraph) for paragraph in paragraphs]


# A hard-coded rule that generate yes-no questions 
def sentences_to_yesnoquestions_baseline(sentences):
    target_verb_list = ["am", "is", "are", "was", "were", "can", \
                        "cannot", "can't", "could", "couldn't", \
                        "dare", "may", "might", "must", "mustn't", \
                        "need", "needn't", "ought", "shall", \
                        "should", "shouldn't", "will", \
                        "would", "won't"]
    forward_stop_tag_list = [",", ":", ".", "WRB"]
    backward_stop_tag_list = [",", ":", "CC", "IN"]
    title = sentences[0][0].strip("\r\n").lower()
    keywords = title.split(' ')

    sentences = reduce(lambda x, y: x + y, sentences)
    questions = []
    for sentence in sentences:
        pos_tags = nltk.pos_tag(nltk.word_tokenize(sentence))
        verb_index = -1
        for i in range(len(pos_tags)):
            if pos_tags[i][1].startswith('V') and pos_tags[i][0].lower() in target_verb_list:
                verb_index = i
                break
        
        if verb_index <= 0 \
           or pos_tags[-1][0] != '.' \
           or not pos_tags[verb_index - 1][1].startswith("NN") \
           or verb_index == len(pos_tags) - 1 \
           or pos_tags[verb_index + 1][1] in forward_stop_tag_list:
            continue

        begin = verb_index - 1
        while begin >= 0 and pos_tags[begin][1] not in backward_stop_tag_list:
            begin -= 1
            
        end = verb_index + 1
        while end < len(pos_tags) and pos_tags[end][1] not in forward_stop_tag_list:
            end += 1

        subj = pos_tags[(begin + 1) : verb_index]
        subj = [tag[0] for tag in subj]
        obj = pos_tags[(verb_index + 1) : end]
        obj = [tag[0] for tag in obj]
        if filter(lambda noun: noun.lower() in keywords, subj):
            question = reduce(lambda x, y: x + ' ' + y if y not in ["'s", "'", ")", "%"] and x[-1] not in ["("] else x + y, [pos_tags[i][0]] + subj + obj)
            questions.append(question[0].upper() + question[1:] + "?")

    return questions


# A wrapper function. Given a list of list of sentences 
# and a list of rules, output a list of questions.
def get_questions_from_sentences(sentences, \
                                 sentence_to_questions_functions):
    return reduce(lambda x, y: x + y, [f(sentences) for f in sentence_to_questions_functions])
    


def usage():
    print("usage: python ask_baseline.py <article file name> \
          <number of questions to generate> [v]")

def main():
    # Process arguments
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        usage()
        return
    article_file_name = sys.argv[1]
    num_questions = sys.argv[2]
    verbose = False
    if len(sys.argv) == 4 and sys.argv[3].lower() == "v":
        verbose = True
    if (not num_questions.isdigit()) or int(num_questions) <= 0:
        print("Please enter a valid number of questions file name.")
        return
    if not os.path.isfile(article_file_name):
        print("Please enter a valid article file name.")
        return
    num_questions = int(num_questions)


    # Split the article into sentences, then 
    # use some hard-coded rules to generate questions from each 
    # sentence
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    sentences_in_paragraphs = split_paragraphs_to_sentences(get_paragraphs(article_file_name))
    questions = get_questions_from_sentences(sentences_in_paragraphs, [sentences_to_yesnoquestions_baseline])
    if verbose:
        print(questions)

    # Shuffle and print: don't use this
    questions = filter(lambda q: len(q.split(' ')) < 30 and len(q.split(' ')) > 5, questions)
    random.shuffle(questions)
    print("\n".join(questions[0:num_questions]))


if __name__ == "__main__":
    main()