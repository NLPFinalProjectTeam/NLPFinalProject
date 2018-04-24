import sys, os, nltk, codecs



def segment_into_sentences(path):
	"""
		Example input: 'set1/a1.txt' or 'a1.txt'
	
	"""
	if "/" in path:
		set_num, txt_num = path.strip().split("/")
		sent_set_dir = os.path.join("../sentences/", set_num)
		if not os.path.isdir(sent_set_dir):
			os.mkdir(sent_set_dir)

		doc_dir = os.path.join(sent_set_dir, txt_num[:-4])
		if not os.path.isdir(doc_dir):
			os.mkdir(doc_dir)

		fname = os.path.join("../data/", path)

	else:
		doc_dir = os.path.join("../sentences/", path[:-4])
		if not os.path.isdir(doc_dir):
			os.mkdir(doc_dir)

		fname = os.path.join("../src/", path)

	f = codecs.open(fname, encoding="utf-8", errors="replace")
	lines = f.readlines()
	f.close()

	sent_list = []
	for line in lines:
		if len(line.strip()) > 0:
			sent_list += nltk.tokenize.sent_tokenize(line)

	for i, sent in enumerate(sent_list):
		f_i = codecs.open(os.path.join(doc_dir, str(i) + ".txt"), "w", "utf-8", errors="replace")
		f_i.write(sent)
		f_i.close()



def build_index(path):
	"""
		Example input: 'set1/a1.txt'
	
	"""

	sent_set_dir = os.path.join("../sentences/", path[:-4])
	if not os.path.isdir(sent_set_dir):
		segment_into_sentences(path)

	if "/" in path:
		set_num, txt_num = path.strip().split("/")
		index_set_dir = os.path.join("../index/", set_num)
		if not os.path.isdir(index_set_dir):
			os.mkdir(index_set_dir)

		index_dir = os.path.join(index_set_dir, txt_num[:-4])
		if not os.path.isdir(index_dir):
			os.mkdir(index_dir)

	else:
		index_dir = os.path.join("../index/", path[:-4])
		if not os.path.isdir(index_dir):
			os.mkdir(index_dir)

	cmd = 'java -cp ".:lucene-6.6.0/*" MyIndexer %s %s' % (sent_set_dir, index_dir)
	os.system(cmd)



if __name__ == '__main__':
	sets = ['set1', 'set2', 'set3', 'set4']
	docs = ['a1.txt', 'a2.txt', 'a3.txt', 'a4.txt', 'a5.txt', 'a6.txt', 'a7.txt', 'a8.txt', 'a9.txt', 'a10.txt']
	for s in sets:
		for d in docs:
			path = os.path.join(s, d)
			segment_into_sentences(path)
			build_index(path)





