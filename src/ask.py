#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import io
import random
import os.path
import nltk
import nltk.data
import logging
from nltk import ne_chunk, tree2conlltags
from nltk.stem.wordnet import WordNetLemmatizer
from functools import *
import codecs
from nltk.parse.stanford import StanfordDependencyParser
from stanfordcorenlp import StanfordCoreNLP
from nltk.tree import Tree, ParentedTree
import string
import re
from pattern.en import conjugate, lemma, lexeme, PRESENT, SG, PL, PAST
import math

# TODO:
# Rank the questions
# no questions rules

word_lem = WordNetLemmatizer()
nlp = StanfordCoreNLP(r'/Users/lazy/Documents/cmu/11611/stanfordNLP/stanford-corenlp-full-2018-02-27')


# nlp=StanfordCoreNLP(r'/Users/lazy/Documents/cmu/11611/stanfordNLP/stanford-corenlp-full-2018-02-27',quiet=False, logging_level=logging.DEBUG)


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


# Replace a word by what it should be
def symbol_to_word(symbol):
    if symbol == "--":
        return "-"
    elif symbol == "-LRB-" or symbol == "-LRB-Unicode":
        return "("
    elif symbol == "-LCB-" or symbol == "-LCB-Unicode":
        return "{"
    elif symbol == "-LSB-" or symbol == "-LSB-Unicode":
        return "["
    elif symbol == "-RRB-" or symbol == "-RRB-Unicode":
        return ")"
    elif symbol == "-RCB-" or symbol == "-RCB-Unicode":
        return "}"
    elif symbol == "-RSB-" or symbol == "-RSB-Unicode":
        return "]"
    elif symbol == "``" or symbol == "''":
        return '"'
    elif symbol == "`":
        return "'"
    else:
        return symbol


# Convert a list of words into a string

def list_to_segment(word_list):
    if len(word_list) == 0:
        return ''
    elif len(word_list) == 1:
        return word_list[0]

    ret = ""
    unclosed_single_quote = 0
    unclosed_double_quote = 0
    for ind, word in enumerate(word_list):
        word = symbol_to_word(word)

        if ind == 0:
            ret += word
        elif word == '"':
            if unclosed_double_quote == 0:
                ret += ' "'
                unclosed_double_quote = 1
            else:
                ret += '"'
                unclosed_double_quote = 0
        elif word == "'" and len(ret) > 0 and ret[-1] == 's':
            ret += "'"
        elif word == "'":
            if unclosed_single_quote == 0:
                ret += " '"
                unclosed_single_quote = 1
            else:
                ret += "'"
                unclosed_single_quote = 0
        elif word.startswith("'"):
            ret += word
        elif len(ret) > 0 and ret[-1] == '"' and unclosed_double_quote == 1:
            ret += word
        elif len(ret) > 0 and ret[-1] == "'" and unclosed_single_quote == 1:
            ret += word
        elif word in [")", "%", ",", ";", ":", "@", "_", "}", "]", "."] or (
                len(ret) > 0 and ret[-1] in ["(", "_", "@", "[", "{", "$", "#"]):
            ret += word
        elif word == "+":
            if len(ret) > 0 and ret[-1] in ["A", "B", "C", "D"]:
                ret += "+"
            else:
                ret += " +"
        else:
            ret += ' ' + word

    return ret


# Some hard coded rules to generate no questions
def yes_question_to_no(question):
    questions = []
    float_re = re.compile("[0-9]+(\.[0-9]+){1}")
    one_digit_re = re.compile("[0-9]{1}")
    two_digit_re = re.compile("[0-9]{2}")
    three_digit_re = re.compile("[0-9]{3}")
    four_digit_re = re.compile("[0-9]{4}")
    five_or_more_digit_re = re.compile("[0-9]{5,}")

    five_match = five_or_more_digit_re.search(question)
    four_match = four_digit_re.search(question)
    three_match = three_digit_re.search(question)
    two_match = two_digit_re.search(question)
    one_match = one_digit_re.search(question)

    if float_re.search(question):
        questions.append(float_re.sub("3.1451", question))
    if four_match:
        questions.append(four_digit_re.sub(str(int(four_match.group()) - 30), question, 1))
    elif five_match:
        questions.append(five_or_more_digit_re.sub(str(int(five_match.group()) - 10), question, 1))
    elif three_match:
        questions.append(three_digit_re.sub(str(int(three_match.group()) - 30), question, 1))
    elif two_match:
        questions.append(two_digit_re.sub("8" + two_match.group(), question, 1))
    elif one_match:
        questions.append(one_digit_re.sub("8" + one_match.group(), question, 1))

    return questions


# Return a list of what, who, where, when, how question
def generate_wh_from_root(sentence):
    try:
        # print('original sentence:',sentence)
        old_sent = sentence
        if old_sent[0] == '"':
            old_sent = old_sent[1:]
        if old_sent[-1] == '"':
            old_sent = old_sent[:-1]
        tree = nlp.parse(sentence)
        parse_tree = ParentedTree.fromstring(tree)[0]
        for t in parse_tree.subtrees(lambda x: x.label() == 'S'):
            find_np = False
            find_vp = False
            for subt in t:
                if subt.label() == 'NP' and not find_vp:
                    find_np = True
                if subt.label() == 'VP' and find_np:
                    find_vp = True
            if find_np and find_vp:
                parse_tree = t
                break
        # print('parse tree',parse_tree)
        if parse_tree.label() != "S":
            # print('illegle sentence!')
            return []
        sentence = parse_tree.leaves()
        # print('new sentence', sentence)
        sentence_ner = [p[1] for p in nlp.ner(' '.join(sentence))]
        # print('sentence ner:',sentence_ner)
        dependency_tree = nlp.dependency_parse(' '.join(sentence))
        # print('dependency tree',dependency_tree)

    except:
        # print('cannot pass, invalid sentence, next!')
        return []
    start_idx = 0
    be_verbs = ["am", "is", "are", "was", "were", "be", "been"]
    do_verbs = ["do", "does", "did", "done", "doing"]
    have_verbs = ["have", "has", "had", "having", "haven't", "hadn't", "hasn't"]
    modal_verbs = ["can", "cannot", "can't", "could", "couldn't", \
                   "dare", "may", "might", "must", "mustn't", \
                   "need", "needn't", "ought", "shall", \
                   "should", "shouldn't", "will", \
                   "would", "won't", "ought"]
    questions = []
    np = None
    vp = None
    for t in parse_tree.subtrees(lambda st: st.parent() == parse_tree):
        if t.label() == "NP" and not vp:
            np = t
        if t.label() == "VP" and np:
            vp = t
    if not np or not vp:
        # print('not find np or vp')
        return []
    # print('find np',np)
    # print('find vp',vp)

    # deal with subject
    # Construct subject list
    # Check if it contains a normal noun
    np_pos = np.pos()
    np_idx = []
    contains_nn = False
    np_ner = []
    for p in np_pos:
        if p[1].startswith("NN"):
            contains_nn = True
            break
    if not contains_nn:
        # print('invalid subject!')
        return []
    subj_list = [p[0] for p in np_pos]
    for nbv in subj_list:
        try:
            sub_i = sentence.index(nbv, start_idx)
            start_idx = sub_i
            np_idx.append(sub_i + 1)
            np_ner.append(sentence_ner[sub_i])
        except:
            # print('no subjective!')
            return []

    if len(subj_list) > 0 and len(np_ner) > 0 and np_ner[-1] not in ("LOCATION", "PERSON", "ORGANIZATION"):
        subj_list[0] = subj_list[0][0].lower() + subj_list[0][1:]

    # print('np ner:',np_ner)
    # print('subjective list',subj_list)
    # print('np pos',np_pos)
    # print('np idx',np_idx)

    verb_list = []
    verb_idx = []
    verb_pos = []
    vp_sentence = vp.pos()
    # print('original vp pos',vp.pos())
    for vb in vp.subtrees():
        if vb.label().startswith('N'):
            break
        if type(vb[0]) == str:
            if vb.label().startswith('V') or vb.label().startswith('TO') or vb.label().startswith('MD'):
                verb_list.append(vb[0])
                verb_pos.append(vb.label())

    # more than 3 verb like "could have been done" is too complex and currently we just ignore
    if len(verb_list) > 3 or len(verb_list) <= 0:
        # print('too many verbs!',verb_list)
        return []
    # find index for dependency parse process
    for vb in verb_list:
        try:
            vbidx = sentence.index(vb, start_idx)
            start_idx = vbidx
        except:
            # print('not find')
            return []
        verb_idx.append(vbidx + 1)
    # print('vp list',verb_list,'verb index:',verb_idx,'verb POS:',verb_pos)

    # find object
    objp = None
    has_obj = False
    obj_idx = []
    obj_pos = []
    obj_ner = []
    obj_list = []
    valid_obj = True
    """
    To be verified about the height!!
    """
    for t in vp.subtrees(lambda st: st.label() == 'NP'):
        is_find = True
        # print('subtree',t.pos())
        # print('subtree',t,t.label())
        for subt in t:
            if subt.label() == 'NP':
                is_find = False
                break
            # sub_pos = subt.pos()
            # is_find=False
            # for n1,p1 in sub_pos:
            #     if p1.startswith('N'):
            #         is_find=True
            #         break
            # if not is_find:
            #     continue
        if is_find:
            has_obj = True
            objp = t
            # print('find obj',objp)
            break

    if has_obj:
        opjPOS = objp.pos()
        contains_nn = False
        for p in opjPOS:
            if p[1].startswith("N"):
                contains_nn = True
                break
        if not contains_nn:
            valid_obj = False
        for o, pos in opjPOS:
            try:
                obji = sentence.index(o, start_idx)
                start_idx = obji
            except:
                has_obj = False
                objp = None
                break
            obj_idx.append(obji + 1)
            obj_pos.append(pos)
            obj_ner.append(sentence_ner[obji])
        obj_list = [p[0] for p in opjPOS]
    if not valid_obj:
        # print('obj not valid!')
        has_obj = False
    # print('has obj?',has_obj)
    # if has_obj:
    #     print('obj tree',objp)
    #     print('obj list',obj_list)
    #     print('obj ner',obj_ner,'obj pos:',obj_pos,'obj index:',obj_idx)

    is_passive = False
    core_verbidx = verb_idx[-1]

    for (depend, front, later) in dependency_tree:
        if front == core_verbidx and 'pass' in depend:
            is_passive = True
            break

    # generate question
    qtype = None
    if is_passive:
        # q1: ask obj
        is_singular = True
        if has_obj and obj_pos[-1] in ('NNS', 'NNPS'):
            is_singular = False

        if has_obj and (obj_ner[-1] == 'PERSON' or obj_pos[-1] == 'PRP'):
            qtype = 'Who'
        else:
            qtype = 'What'
        new_verblist = []
        aux_verb = None
        true_verb = None
        type_3verb = None
        if len(verb_list) == 3:
            if verb_list[0] in have_verbs:
                if verb_pos[0] in ('VB', 'VBZ', 'VBP'):
                    if is_singular:
                        new_verblist.append('has')
                        aux_verb = 'has'
                    else:
                        new_verblist.append('have')
                        aux_verb = 'have'
                else:
                    new_verblist.append('had')
                    aux_verb = 'had'
                new_verblist.append(verb_list[-1])
                true_verb = verb_list[-1]
                type_3verb = 'done'
            elif verb_list[0] in modal_verbs:
                new_verblist.append(verb_list[0])
                new_verblist.append(word_lem.lemmatize(verb_list[-1], 'v'))
                aux_verb = verb_list[0]
                true_verb = new_verblist[-1]
                type_3verb = 'do'
            else:
                # print('invalid!')
                return []
        elif len(verb_list) == 2:
            true_verb = word_lem.lemmatize(verb_list[-1], 'v')
            type_3verb = 'do'
            if verb_pos[0] in ('VB', 'VBZ', 'VBP'):
                if is_singular:
                    new_verblist.append(conjugate(verb=verb_list[-1], tense=PRESENT, number=SG))
                    aux_verb = 'does'
                else:
                    new_verblist.append(conjugate(verb=verb_list[-1], tense=PRESENT, number=PL))
                    aux_verb = 'do'
            else:
                new_verblist.append(conjugate(verb=verb_list[-1], tense=PAST))
                aux_verb = 'did'
        else:
            # rint('wrong verb list length!')
            return []
        question = qtype + ' ' + ' '.join(new_verblist) + ' ' + list_to_segment(subj_list) + '?'
        answer = list_to_segment(obj_list) + '.'
        answer = answer[0].upper() + answer[1:]
        questions.append(qtype + '\t' + question + '\t' + answer)
        # print('generate passive question 1:',question)
        if has_obj and aux_verb:
            if np_ner[-1] == 'PERSON' or np_pos[-1] == 'PRP':
                qtype = 'Whom'
            else:
                qtype = 'What'
            question = qtype + ' ' + aux_verb + ' ' + list_to_segment(obj_list) + ' ' + true_verb + '?'
            answer = list_to_segment(subj_list) + '.'
            answer = answer[0].upper() + answer[1:]
            questions.append(qtype + '\t' + question + '\t' + answer)
            # print('generate passive question 2:', question)
            question = 'What ' + aux_verb + ' ' + list_to_segment(obj_list) + ' ' + type_3verb + '?'
            answer = list_to_segment(obj_list) + ' ' + ' '.join(new_verblist) + ' ' + list_to_segment(subj_list) + '.'
            answer = answer[0].upper() + answer[1:]
            questions.append('What ' + '\t' + question + '\t' + answer)
        # print('generate passive question 3:', question)
    else:
        # q1: ask obj
        new_verblist = []
        aux_verb = None
        true_verb = None
        type_3verb = None
        # 1. ask sub
        if np_ner[-1] == 'PERSON' or np_pos[-1] == 'PRP':
            qtype = 'Who'
        else:
            qtype = 'What'
        new_verblist = list(verb_list)
        if verb_pos[0] in ('VB', 'VBP', 'VBZ'):
            new_verblist[0] = conjugate(verb=new_verblist[0], tense=PRESENT, number=SG)
        if has_obj:
            question = qtype + ' ' + ' '.join(new_verblist) + ' ' + list_to_segment(obj_list) + '?'
            answer = list_to_segment(subj_list) + '.'
            answer = answer[0].upper() + answer[1:]
            questions.append(qtype + '\t' + question + '\t' + answer)
            # eg: Who makes this happen?
            # print('generate active question 1(who/what):', question)

        if len(verb_list) > 1 and (
                verb_list[0] in modal_verbs or verb_list[0] in have_verbs or verb_list[0] in be_verbs):
            aux_verb = verb_list[0]
            true_verb = ' ' + ' '.join(verb_list[1:])
        else:
            if verb_list[0] in be_verbs:
                true_verb = ''
                aux_verb = verb_list[-1]
            else:
                true_verb = ' ' + word_lem.lemmatize(verb_list[0], 'v')
                if len(verb_list) > 1:
                    true_verb += ' ' + ' '.join(verb_list[1:])
                if verb_pos[0] in ('VB', 'VBP'):
                    aux_verb = 'do'
                elif verb_pos[0] == 'VBZ':
                    aux_verb = 'does'
                else:
                    aux_verb = 'did'
        # q2: ask obj
        if has_obj:
            if obj_ner[-1] in ('CITY', 'COUNTRY', 'ORGANIZATION', 'LOCATION', 'GPE', 'GSP', 'FACILITY'):
                qtype = 'Where'
                question = qtype + ' ' + aux_verb + ' ' + list_to_segment(subj_list) + true_verb + '?'
                answer = list_to_segment(obj_list) + '.'
                answer = answer[0].upper() + answer[1:]
                questions.append(qtype + '\t' + question + '\t' + answer)
                # eg: Where did he go?
                # print('generate active question 2(where):', question)
            else:
                prop = ''
                for (rel, front, end) in dependency_tree:
                    if front == obj_idx[-1] and rel == 'case':
                        prop = ' ' + sentence[end - 1]
                        break
                if obj_ner[-1] == 'PERSON' or obj_pos[-1] == 'PRP':
                    qtype = 'Whom'
                else:
                    qtype = 'What'
                question = qtype + ' ' + aux_verb + ' ' + list_to_segment(subj_list) + true_verb + prop + '?'
                # print('true verb:','-'+true_verb,'prop:','-'+prop)
                answer = list_to_segment(obj_list) + '.'
                answer = answer[0].upper() + answer[1:]
                questions.append(qtype + '\t' + question + '\t' + answer)
                # eg: Whom has he played for?
                # print('generate active question 3 (whom/what):', question)

        if 'DATE' in sentence_ner or 'TIME' in sentence_ner:
            qtype = 'When'
            question = qtype + ' ' + aux_verb + ' ' + list_to_segment(subj_list) + true_verb + ' ' + list_to_segment(
                obj_list) + '?'
            answer = []
            for idx, ner in enumerate(sentence_ner):
                if ner in ('DATE', 'TIME'):
                    answer.append(sentence[idx])
            answer = ' '.join(answer) + '.'
            answer = answer[0].upper() + answer[1:]
            questions.append(qtype + '\t' + question + '\t' + answer)
            # eg: When did he go to university
        # print('generate active question 4(when):', question)
        """
        how many/much, countable/uncountable
        """
        if 'because' in sentence or 'since' in sentence or 'reason' in sentence or re.search(r'for.*ing', ' '.join(
                sentence)) or 'due to' in ' '.join(sentence):
            qtype = 'Why'
            question = qtype + ' ' + aux_verb + ' ' + list_to_segment(
                subj_list) + true_verb + ' ' + list_to_segment(obj_list) + '?'
            answer = old_sent
            questions.append(qtype + '\t' + question + '\t' + answer)
            # eg: Why did he go to university
            # print('generate active question 5(Why):', question)

        if 'via' in sentence or 'through' in sentence or re.search(r'by.*of', ' '.join(sentence)) or re.search(
                r'in.*way', ' '.join(sentence)) or re.search(r'with.*of', ' '.join(sentence)):
            qtype = 'How'
            question = qtype + ' ' + aux_verb + ' ' + list_to_segment(
                subj_list) + true_verb + ' ' + list_to_segment(obj_list) + '?'
            answer = old_sent
            questions.append(qtype + '\t' + question + '\t' + answer)
            # eg: Why did he go to university
            # print('generate active question 6(How):', question)
    return questions


# Returns a list of questions, given
def get_yesnoquestions_from_root(parse_tree):
    if parse_tree.label() != "S":
        return []

    be_verbs = ["am", "is", "are", "was", "were"]

    questions = []
    np = None
    vp = None

    # Get NP, VP and subsentences
    for t in parse_tree.subtrees(lambda st: st.parent() == parse_tree):
        if t.label() == "NP" and not vp:
            np = t
        if t.label() == "VP" and np:
            vp = t

    if not np or not vp:
        return []

    # Get verb from VP
    verb_tag = None
    vp_count = 0
    for t in vp.subtrees(lambda st: st.parent() == vp and st.label().startswith("V")):
        if vp_count == 0 and t.height() == 2:
            verb_tag = t
        vp_count += 1
    if not verb_tag or not verb_tag.leaves():
        return []
    verb = verb_tag.leaves()[0]
    verb_tag = verb_tag.pos()[0]

    # Construct subject list
    # Check if it contains a normal noun
    np_pos = np.pos()
    contains_nn = False
    for p in np_pos:
        if p[1].startswith("NN"):
            contains_nn = True
            break
    if not contains_nn:
        return []

    # determine if we need to lowercase the first letter
    np_ner = nlp.ner(' '.join([p[0] for p in np_pos]))
    subj_list = [p[0] for p in np_pos]
    if len(subj_list) > 0 and len(np_ner) > 0 and subj_list[0] == np_ner[0][0] and (
            np_ner[0][1] != "LOCATION" and np_ner[0][1] != "PERSON" and np_ner[0][1] != "ORGANIZATION"):
        subj_list[0] = subj_list[0][0].lower() + subj_list[0][1:]
    subj_segment = list_to_segment(subj_list)

    # Construct questions
    if vp_count == 1:
        if verb.lower() in be_verbs:
            # e.g.: Is Dempsy a nice person?
            # Construct object list
            obj_list = []
            for p in vp.pos():
                if p[0] != verb:
                    obj_list.append(p[0])
            questions.append(
                verb[0].upper() + verb[1:] + ' ' + subj_segment + ' ' + list_to_segment(obj_list).split(";")[0] + "?")
        else:
            # e.g.: Does John work in Starsucks?
            # Construct object list
            obj_list = [word_lem.lemmatize(p[0], 'v') if p[1] == "VBZ" or p[1] == "VBD" else p[0] for p in
                        [tag for tag in vp.pos()]]
            if verb_tag[1] == "VBD" or verb_tag[1] == "VBN":
                first_word = "Did"
            elif verb_tag[1] == "VBZ":
                first_word = "Does"
            else:
                first_word = "Do"

            questions.append(first_word + ' ' + subj_segment + ' ' + list_to_segment(obj_list).split(";")[0] + "?")
    else:
        # e.g.: Could he finish the job?
        # Construct object list
        obj_list = []
        for p in vp.pos():
            if p[0] != verb:
                obj_list.append(p[0])
        questions.append(
            verb[0].upper() + verb[1:] + ' ' + subj_segment + ' ' + list_to_segment(obj_list).split(";")[0] + "?")

    return questions


def sentences_to_yesnoquestions(sentences):
    title = sentences[0][0].strip("\r\n").lower()
    keywords = title.split(' ')

    sentences = reduce(lambda x, y: x + y, sentences)
    questions = []
    for sentence in sentences:
        if len(sentence) > 0 and sentence[-1] == '?':
            questions.append(sentence)
            continue
        if len(sentence) > 0 and sentence[-1] not in string.punctuation:
            continue

        tmp_questions = []
        seed_for_no_questions = ''
        try:  # bad practice, but I don't want the program to fail
            cons_tree = ParentedTree.fromstring(nlp.parse(sentence))
            tmp_questions = get_yesnoquestions_from_root(cons_tree[0])
        except:
            pass
        else:
            if tmp_questions:
                seed_for_no_questions = tmp_questions[0]
                for i in range(len(tmp_questions)):
                    tmp_questions[i] = "YN\t" + tmp_questions[i] + '\t' + "Yes."
                questions += tmp_questions
        if tmp_questions:
            try:
                no_questions = yes_question_to_no(seed_for_no_questions)
                for i in range(len(no_questions)):
                    no_questions[i] = "YN\t" + no_questions[i] + '\t' + "No."
            except:
                pass
            else:
                questions += no_questions

    return questions


def sentence_to_whquestions(sentences):
    sentences = reduce(lambda x, y: x + y, sentences)
    questions = []
    for sentence in sentences:
        if len(sentence) > 0 and sentence[-1] == '?':
            questions.append(sentence.strip().split()[0] + '\t' + sentence + '\t' + "'Sorry, I don't know.")
            continue
        if len(sentence) > 0 and sentence[-1] not in string.punctuation:
            continue
        try:  # bad practice, but I don't want the program to fail
            tmp_questions = generate_wh_from_root(sentence)
        except:
            pass
        else:
            questions += tmp_questions
    return questions


# A wrapper function. Given a list of list of sentences
# and a list of rules, output a list of questions.
def get_questions_from_sentences(sentences, \
                                 sentence_to_questions_functions):
    return list(reduce(lambda x, y: x + y, [f(sentences) for f in sentence_to_questions_functions]))


def usage():
    print("usage: python ask_baseline.py <article file name> \
          <number of questions to generate> [v]")


def my_sort(questions, nums, results, forbid_word, unnecessary):
    count = 0
    for q in questions:
        q_word = q.split()
        # filter word
        for w in forbid_word:
            if w in q_word:
                unnecessary.append(q)
                continue
        if len(q_word) >= 5 and len(q_word) <= 30 and count < nums:
            results.append(q)
            count += 1
        else:
            unnecessary.append(q)

    if count < nums:
        results += unnecessary[:nums - count]
        unnecessary = unnecessary[nums - count:]

    return results, unnecessary


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
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger/averaged_perceptron_tagger.pickle')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')

    try:
        nltk.data.find('chunkers/maxent_ne_chunker/english_ace_multiclass.pickle')
    except LookupError:
        nltk.download('maxent_ne_chunker')

    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')

    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')

    sentences_in_paragraphs = split_paragraphs_to_sentences(get_paragraphs(article_file_name))
    # print('sentence',sentences_in_paragraphs)
    questions = get_questions_from_sentences(sentences_in_paragraphs,
                                             [sentence_to_whquestions, sentences_to_yesnoquestions])

    nlp.close()

    if verbose:
        print(questions)

    # Shuffle and print
    # random.shuffle(questions)
    newpath = '../knowledge_base/generate_' + article_file_name
    allq = '\n'.join(questions)
    output_question = []
    what_q = []  # 30%
    what_num = math.ceil(num_questions * 0.3)
    who_q = []  # 15%
    who_num = math.ceil(num_questions * 0.15)
    why_q = []  # 6%
    why_num = math.ceil(num_questions * 0.06)
    yn_q = []  # 25%
    yn_num = math.ceil(num_questions * 0.25)
    whom_q = []  # 6%
    whom_num = math.ceil(num_questions * 0.06)
    how_q = []  # 6%
    how_num = math.ceil(num_questions * 0.06)
    when_q = []  # 6%
    when_num = math.ceil(num_questions * 0.06)
    where_q = []  # 6%
    where_num = math.ceil(num_questions * 0.06)

    forbid_word = ['I', 'it', 'their', 'her', 'his', 'him', 'she', 'he', 'they', 'our', 'us', 'we', 'them']
    unnecessary = []
    for question_pair in questions:
        q = question_pair.strip().split('\t')
        if len(q) > 1:
            # sort different question first
            if q[0] == 'What':
                what_q.append(q[1])
            elif q[0] == 'YN':
                yn_q.append(q[1])
            elif q[0] == 'Who':
                who_q.append(q[1])
            elif q[0] == 'Whom':
                whom_q.append(q[1])
            elif q[0] == 'How':
                how_q.append(q[1])
            elif q[0] == 'Where':
                where_q.append(q[1])
            elif q[0] == 'When':
                when_q.append(q[1])
            elif q[0] == 'Why':
                why_q.append(q[1])
        else:
            continue

    output_question, unnecessary = my_sort(why_q, why_num, output_question, forbid_word, unnecessary)
    output_question, unnecessary = my_sort(what_q, what_num, output_question, forbid_word, unnecessary)
    output_question, unnecessary = my_sort(yn_q, yn_num, output_question, forbid_word, unnecessary)
    output_question, unnecessary = my_sort(whom_q, whom_num, output_question, forbid_word, unnecessary)
    output_question, unnecessary = my_sort(who_q, who_num, output_question, forbid_word, unnecessary)
    output_question, unnecessary = my_sort(how_q, how_num, output_question, forbid_word, unnecessary)
    output_question, unnecessary = my_sort(where_q, where_num, output_question, forbid_word, unnecessary)
    output_question, unnecessary = my_sort(when_q, when_num, output_question, forbid_word, unnecessary)
    if len(output_question) < num_questions:
        random.shuffle(unnecessary)
        output_question += unnecessary[:num_questions - len(output_question)]
    # print('output',output_question)
    random.shuffle(output_question)
    with codecs.open(newpath, 'w', 'utf-8') as f:
        f.write(allq)
    print("\n".join(output_question[0:num_questions]))


if __name__ == "__main__":
    if not os.path.exists('../knowledge_base'):
        os.mkdir('../knowledge_base')
    main()
