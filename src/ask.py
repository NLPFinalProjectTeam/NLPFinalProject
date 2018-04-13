#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import io
import random
import os.path
import nltk
import nltk.data
from nltk import ne_chunk, tree2conlltags
from nltk.stem.wordnet import WordNetLemmatizer
from functools import *
import codecs
from nltk.parse.stanford import StanfordDependencyParser

word_lem = WordNetLemmatizer()
# path_to_jar = '../lib/parser/stanford-parser.jar'
# path_to_models = '../lib/parser/stanford-parser-3.9.1-models.jar'
# depend = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models)


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
    with codecs.open(article_file_name, 'r', encoding='utf-8') \
            as article:
        for line in article:
            paragraph = line.strip("\r\n")
            if paragraph != "":
                paragraphs.append(paragraph)
    return paragraphs


def split_paragraphs_to_sentences(paragraphs):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return [tokenizer.tokenize(paragraph) for paragraph in paragraphs]


def generate_wh_questionByStandfordNLP(sentences, depend):
    title = sentences[0][0].strip("\r\n").lower()
    # print('title:',title)
    keywords = title.split(' ')
    sentences = reduce(lambda x, y: x + y, sentences)
    questions = []
    for s in sentences[1:]:
        pos_tags = nltk.pos_tag(nltk.word_tokenize(s))
        try:
            ners = tree2conlltags(ne_chunk(pos_tags))
        except:
            continue
        words = [word[0] for word in ners]
        result = depend.raw_parse(s).__next__()
        triples = list(result.triples())
        sub = None
        for later, mid, front in triples:
            if mid == 'nsubj':
                # generate who
                try:
                    idx = words.index(front[0])
                except:
                    continue
                sub = front[0]
                ques = 'Who ' + ' '.join(words[idx + 1:-1]) + ' ?'
                type = 'WHO'
                answer = ' '.join(words[:idx + 1])
                answer = answer[0].upper() + answer[1:]
                print('who q', ques)
                questions.append(type + '\t' + ques + '\t' + answer)
            if mid == 'dobj':
                if sub == None:
                    continue
                try:
                    obj_idx = words.index(front[0])
                    verb_idx = words.index(later[0])
                except:
                    continue
                verb_tag = ners[verb_idx][1]
                what = False
                where = False
                if 'GPE' in ners[obj_idx][2] or 'LOC' in ners[obj_idx][2]:
                    where = True
                else:
                    what = True
                if what:
                    type = 'WHAT'
                    begin_word = 'What'
                else:
                    type = 'WHERE'
                    begin_word = 'Where'

                if verb_tag == 'VBD':
                    aux_verb = 'did'
                    true_verb = word_lem.lemmatize(later[0])
                elif verb_tag == 'VBZ':
                    aux_verb = 'does'
                    true_verb = word_lem.lemmatize(later[0])
                elif verb_tag in ('VB', 'VBP'):
                    aux_verb = 'do'
                    true_verb = word_lem.lemmatize(later[0])
                else:
                    find = False
                    for l1, m1, f1 in triples:
                        if m1 == 'aux':
                            find = True
                            aux_verb = f1[0]
                            true_verb = l1[0]
                            break
                    if not find:
                        continue
                ques = begin_word + ' ' + aux_verb + ' ' + sub + " " + true_verb + ' ?'
                answer = ' '.join(words[verb_idx + 1:])
                answer = answer[0].upper() + answer[1:]
                questions.append(type + '\t' + ques + '\t' + answer)
    return list(set(questions))

    pass


def generate_wh_questions(sentences):
    target_verb_list = ["am", "is", "are", "was", "were", "can", \
                        "cannot", "can't", "could", "couldn't", \
                        "dare", "may", "might", "must", "mustn't", \
                        "need", "needn't", "ought", "shall", \
                        "should", "shouldn't", "will", \
                        "would", "won't"]
    forward_stop_tag_list = [",", ":", ".", "WRB"]
    backward_stop_tag_list = [",", ":", "CC", "IN"]
    # print('sentence:',sentences)
    title = sentences[0][0].strip("\r\n").lower()
    # print('title:',title)
    keywords = title.split(' ')

    sentences = reduce(lambda x, y: x + y, sentences)
    questions = []
    for sentence in sentences[1:]:
        pos_tags = nltk.pos_tag(nltk.word_tokenize(sentence))
        try:
            ners = tree2conlltags(ne_chunk(pos_tags))
        except:
            continue
        verb_index = -1
        #
        who = None
        where = None
        objs = None
        endflag = False
        when = None  # tough, leave it
        why = None  # tough, leave it
        how = None  # tough, leave it
        for i in range(len(ners)):
            if ners[i][1].startswith('V'):
                verb_index = i
                break

        if verb_index <= 0 \
                or ners[-1][0] != '.' \
                or not ners[verb_index - 1][1].startswith("NN") \
                or verb_index == len(ners) - 1 \
                or ners[verb_index + 1][1] in forward_stop_tag_list:
            continue

        begin = verb_index - 1
        whof = False
        while begin >= 0 and ners[begin][1] not in backward_stop_tag_list:
            if (ners[begin][1].startswith('N') or ners[begin][1] == 'PRP') and not whof:
                who = begin
                whof = True
            begin -= 1
        if who == None:
            continue
        end = verb_index + 1
        objf = False
        while end <= len(ners) and ners[end][1] not in forward_stop_tag_list:
            if end == len(ners):
                endflag = True
                break
            if (ners[begin][1].startswith('N') or ners[begin][1] == 'PRP') and not objf:
                objf = True
                objs = end
            end += 1

        subj = pos_tags[(begin + 1): verb_index]
        subj = [tag[0] for tag in subj]
        obj = pos_tags[(verb_index + 1): end]
        obj = [tag[0] for tag in obj]
        answer = pos_tags[(begin + 1):end]
        answer = [tag[0] for tag in answer]
        # generate around subject
        if ners[who][1] == 'PRP' or 'PER' in ners[who][2]:
            questions.append("WHO\tWho " + ners[verb_index][0] + ' ' + ' '.join(obj) + '?\t' + ' '.join(answer))
        elif ners[who][1].startswith('N'):
            questions.append("WHAT\tWhat " + ners[verb_index][0] + ' ' + ' '.join(obj) + '?\t' + ' '.join(answer))
        # generate around object
        if objs != None:
            if ners[verb_index][0] in target_verb_list:
                if 'GPE' in ners[objs][2]:
                    lasts = ners[objs + 1:end]
                    lasts = [l[0] for l in lasts]
                    questions.append('WHERE\tWhere ' + ners[verb_index][0] + ' ' + ners[who][0] + ' ' + ' '.join(
                        lasts) + '?\t' + ' '.join(answer))
                else:
                    questions.append('WHAT\tWhat ' + ners[verb_index][0] + ' ' + ners[who][0] + ' ' + ' '.join(
                        objs) + '?\t' + ' '.join(answer))
            # else:
            #     beginpart=None
            #     endpart=None
            #     if ners[verb_index][1] in ('VBP','VB'):
            #         beginpart='Where do '+ners[who][0]+" "+

        # if filter(lambda noun: noun.lower() in keywords, subj):
        #     question = reduce(
        #         lambda x, y: x + ' ' + y if y not in ["'s", "'", ")", "%"] and x[-1] not in ["("] else x + y,
        #         [pos_tags[verb_index][0]] + subj + obj)
        #     questions.append(question[0].upper() + question[1:] + "?")
    return questions


def sentences_to_yesnoquestions_baseline2(sentences):
    non_target_verb_list = ["am", "is", "are", "was", "were", "can", \
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
        if pos_tags[-1][0] != '.':
            if pos_tags[-1][0] == '?':
                questions.append('YN\t' + sentence+ '\t' + 'Yes')
            continue

        noun_encountered = False
        verb_encountered = False
        have_encountered = False
        be_encountered = False
        keyword_encountered = False

        verb_index = -1
        have_index = -1
        for i in range(len(pos_tags)):
            if not verb_encountered and pos_tags[i][0].lower() in keywords:
                keyword_encountered = True
                noun_encountered = True

            if pos_tags[i][0].lower() in ["have", "has", "had"]:
                have_encountered = True
                have_index = i
                verb_index = i

            if not verb_encountered and pos_tags[i][0].lower() in ["am", "is", "are", "was", "were"]:
                be_encountered = True

            if not be_encountered and pos_tags[i][1] == "VBG":
                continue

            if not verb_encountered \
                    and not have_encountered \
                    and not be_encountered \
                    and pos_tags[i][1].startswith("N"):
                noun_encountered = True

            if noun_encountered and pos_tags[i][1].startswith('V') and pos_tags[i][
                0].lower() not in non_target_verb_list:
                verb_encountered = True
                verb_index = i
                break

        if verb_index <= 0 or be_encountered or not keyword_encountered:
            continue

        # TODO: identify important sub-sentence
        # TODO: captial letter of first word
        if have_encountered and verb_encountered:
            begin = have_index - 1
            while begin >= 0 and pos_tags[begin][1] not in backward_stop_tag_list:
                begin -= 1

            end = have_index + 1
            while end < len(pos_tags) and pos_tags[end][1] not in forward_stop_tag_list:
                end += 1

            subj = pos_tags[(begin + 1): have_index]
            subj = [tag[0] for tag in subj]
            obj = pos_tags[(have_index + 1): end]
            obj = [tag[0] for tag in obj]
            if subj:
                subj[0] = subj[0][0].lower() + subj[0][1:] if not pos_tags[begin + 1][1].startswith('N') else subj[0]
            question = reduce(
                lambda x, y: x + ' ' + y if y not in ["'s", "'", ")", "%"] and x[-1] not in ["("] else x + y,
                [pos_tags[have_index][0]] + subj + obj)
        else:
            begin = verb_index - 1
            while begin >= 0 and pos_tags[begin][1] not in backward_stop_tag_list:
                begin -= 1

            end = verb_index + 1
            while end < len(pos_tags) and pos_tags[end][1] not in forward_stop_tag_list:
                end += 1

            pos_tags[verb_index] = (
                WordNetLemmatizer().lemmatize(pos_tags[verb_index][0], 'v'), pos_tags[verb_index][1])
            subsentence = pos_tags[(begin + 1): end]
            rest_of_sentence = [tag[0] for tag in subsentence]
            if rest_of_sentence:
                rest_of_sentence[0] = rest_of_sentence[0][0].lower() + rest_of_sentence[0][1:] if not \
                    pos_tags[begin + 1][1].startswith('N') else rest_of_sentence[0]
            firstword = ""
            if pos_tags[verb_index][1] == "VBD" or pos_tags[verb_index][1] == "VBN":
                firstword = "Did"
            elif pos_tags[verb_index][1] == "VB" or pos_tags[verb_index][1] == "VBP":
                firstword = "Do"
            else:
                firstword = "Does"
            question = reduce(
                lambda x, y: x + ' ' + y if y not in ["'s", "'", ")", "%"] and x[-1] not in ["("] else x + y,
                [firstword] + rest_of_sentence)
        questions.append('YN\t' + question[0].upper() + question[1:] + "?" + '\t' + 'Yes')
    return questions


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

        subj = pos_tags[(begin + 1): verb_index]
        subj = [tag[0] for tag in subj]
        obj = pos_tags[(verb_index + 1): end]
        obj = [tag[0] for tag in obj]
        if subj:
            subj[0] = subj[0][0].lower() + subj[0][1:] if not pos_tags[begin + 1][1].startswith('N') else subj[0]
        if filter(lambda noun: noun.lower() in keywords, subj):
            question = reduce(
                lambda x, y: x + ' ' + y if y not in ["'s", "'", ")", "%"] and x[-1] not in ["("] else x + y,
                [pos_tags[verb_index][0]] + subj + obj)
            questions.append('YN\t' + question[0].upper() + question[1:] + "?" + '\t' + 'Yes')
    return questions


# A wrapper function. Given a list of list of sentences
# and a list of rules, output a list of questions.
def get_questions_from_sentences(sentences, \
                                 sentence_to_questions_functions):
    return list(reduce(lambda x, y: x + y, [f(sentences) for f in sentence_to_questions_functions]))


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
    nltk.download('wordnet')
    sentences_in_paragraphs = split_paragraphs_to_sentences(get_paragraphs(article_file_name))
    questions = get_questions_from_sentences(sentences_in_paragraphs, [sentences_to_yesnoquestions_baseline,
                                                                       sentences_to_yesnoquestions_baseline2,
                                                                       generate_wh_questions])
    #questions = get_questions_from_sentences(sentences_in_paragraphs,[generate_wh_questionByStandfordNLP])
    if verbose:
        print(questions)

    # Shuffle and print: don't use this
    questions = list(filter(lambda q: len(q.split(' ')) < 30 and len(q.split(' ')) > 5, questions))
    random.shuffle(questions)
    newpath = '../knowledge_base/generate_' + article_file_name
    allq = '\n'.join(questions)
    output_question = []
    for question_pair in questions:
        q = question_pair.strip().split('\t')
        if len(q)>1:
            q=q[1]
        else:
            continue
        output_question.append(q)
    with codecs.open(newpath, 'w','utf-8') as f:
        f.write(allq)
    print("\n".join(output_question[0:num_questions]))


if __name__ == "__main__":
    main()
