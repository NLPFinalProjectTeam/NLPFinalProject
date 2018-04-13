# NLPFinalProject

This project is based on Python3, implemented basic question generation and question answering. For question answering we currently support Yes/No, what and who question implemented by NLTK's NER and POS, we'll use stanford NLP to generate more accurate and various question types with reference resolution in our next stage (this project already includes a standford NLP basic method). For question answering currently we simply match the questions with answers that are already generated regarding that article by the number of overlapping words. If no match is found, then the article's title is returned as the default answer. We'll implement information retrieval method (cosine similarity by word2vec to achieve sentence-level retrieval).

# Instructions
1. Usage:    

./ask article.txt num_questions   
./answer article.txt questions.txt  
You must run ask first then run answer in case of possible errors.
2. Path and directory:
questions.txt and article.txt must be put in the same directory as the ask and answer file.
