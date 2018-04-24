# NLPFinalProject

This project is based on Python3, implemented basic question generation and question answering. For question answering we currently support Yes/No, what and who question implemented by NLTK's NER and POS, we'll use stanford NLP to generate more accurate and various question types with reference resolution in our next stage (this project already includes a standford NLP basic method). For question answering currently we simply match the questions with answers that are already generated regarding that article by the number of overlapping words. If no match is found, then the article's title is returned as the default answer. We'll implement information retrieval method (cosine similarity by word2vec to achieve sentence-level retrieval).

# Instructions


MUST START STANFORD CORE-NLP LOCAL SERVER!!!!!!



1. Usage:
$cd src    
./ask article.txt num_questions   
./answer article.txt questions.txt  [NOT RECOMMENDED]

For answering, it is recommanded to put data in ./data

For details, SEE README in src folder. [MUST SEE!!]

Recommended way: in src folder

python answer.py set1/a1.txt question_file


The valid files are ask.py and answer.py.


2. Path and directory:
questions.txt and article.txt must be put in the same directory as the ask and answer file.

Not necessary for answering. [Details see README in src, MUST SEE!!]
