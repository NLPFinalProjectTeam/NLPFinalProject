# NLPFinalProject

This project is based on Python3, implemented basic question generation and question answering. For question answering we currently support Yes/No, what, who, where, when, how, whom, why question implemented by stanford corenlp. Becuase the package we're using for reference resolution uses a deterministic method and after we experimented with it, the accuracy is just unsatisfying so that we don't support coreference resolution currently. For question answering, we???.

# Instructions


MUST START STANFORD CORE-NLP LOCAL SERVER!!!!!!


To run our program you need to make sure you've installed stanford corenlp and Pattern package.
This project is based on Python3, so make sure you python version is correct first.
And the java version should be 8, if your system's java version is 9+, please downgrade your version, or replace the corenlp.py in our installed package by the corenlp.py in this repo.  

To successfully run stanford corenlp, please first download stanford corenlp from the link https://stanfordnlp.github.io/CoreNLP/. Put it in directory you like.  
Then in order to run it in Python environment, please install the following package which wrap the stanford corenlp server: 

pip install stanfordcorenlp .   

After you successfully install it, you can use it by declaring like: 

from stanfordcorenlp import StanfordCoreNLP   
nlp=StanfordCoreNLP("the_path_you_put_your_stanford_corenlp_+stanford-corenlp-full-2018-02-27") 

Detailed insturction can be referred at https://github.com/Lynten/stanford-corenlp.  

In order to successfully install Pattern in Python 3 (currently the stable version only support python 2), please use the following command: 

git clone https://github.com/clips/pattern   
cd pattern   
git fetch   
git checkout development  
pip install mysqlclient  
python setup.py install   

Then you can successfully use it like:  

from pattern.en import conjugate, lemma, lexeme,PRESENT,SG   
print (lemma('gave'))   
print (lexeme('gave'))  

Here you go! Now you can try the following command.  

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
