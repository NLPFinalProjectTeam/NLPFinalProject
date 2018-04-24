import os, sys, codecs
from build_index import segment_into_sentences, build_index




def retrieve(path, query, num_of_sent):
	temp_file = "retrieve_temp_file.txt"
	query_file = "query_temp.txt"
	index_dir = os.path.join("../index/", path[:-4])
	if not os.path.isdir(index_dir):
		build_index(path)

	qf = codecs.open(query_file, "w", "utf-8", errors="replace")
	qf.write(query)
	qf.close()

	cmd = 'java -cp ".:lucene-6.6.0/*" MyRetriever %s %s %d > %s' % (query_file, index_dir, num_of_sent, temp_file)
	os.system(cmd)

	result = []
	f = codecs.open(temp_file, encoding="utf-8", errors="replace")
	lines = f.readlines()
	i = 0
	while i < num_of_sent * 2 and i < len(lines) - 1:
		score = float(lines[i].strip())
		sent = lines[i+1].strip()
		result.append((score, sent))
		i += 2

	return result



if __name__ == '__main__':
	print (retrieve("a2.txt", "unlike his father?", 5))