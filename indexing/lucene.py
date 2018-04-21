import os, sys, nltk, codecs, json, re


def case2paragraphs(casefile):
    paragraphs = []
    temp = []
    with open(casefile, 'rb') as f:
        for line in f:
            line = line.decode("utf-8", errors='replace').strip()
            # print(line)
            if not line:
                if temp:
                    paragraphs.append(' '.join(temp))
                    temp = []
            else:
                temp.append(line)

        if len(temp) > 0:
            paragraphs.append(' '.join(temp))


    the_i = -1
    for i, para in enumerate(paragraphs):
        if para.strip()[:len("REASONS AND BASES")] == "REASONS AND BASES":
            the_i = i
            break
    #paragraphs = [para in paragraphs if len(para.split()) > 10]

    if the_i >= 0:
    #print (paragraphs)
        paragraphs = [paragraphs[i] for i in range(the_i + 1, len(paragraphs))]
    #print (paragraphs)

    for i, para in enumerate(paragraphs):
        dirname = "./para/" + casefile[-11:-4]
        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        #wf = open(dirname + "/" + str(i+1) + ".txt", "w")
        #wf.write(para)
        #wf.close()

        with codecs.open(dirname + "/" + str(i+1) + ".txt", "w", "utf-8-sig") as wf:
            wf.write(para)


    #return paragraphs


def index(casefile, force=False):
    dirname = "./para/" + casefile[-11:-4] + "/"
    index_dir = "./index/" + casefile[-11:-4] + "/"


    if not os.path.isdir(index_dir):
        os.mkdir(index_dir)
    else:
        if not force:
            return

    cmd = 'java -cp ".:lucene-6.6.0/*" MyIndexer ' + dirname + ' ' + index_dir
    os.system(cmd)


def retrieve(casefile, queryfile):
    index_dir = "./index/" + casefile[-11:-4]
    #sys.stdout = open(casefile[-11:-4] + '_result.txt', "w")
    cmd = 'java -cp ".:lucene-6.6.0/*" MyRetriever ' + queryfile + ' ' + index_dir + ' > ' + casefile[-11:-4] + '_result.txt'
    os.system(cmd)
    #sys.stdout = sys.__stdout__



def get_result(casefile, force=False):
    queryfile = "./queryfile.txt"
    case2paragraphs(casefile)
    index(casefile, force)
    retrieve(casefile, queryfile)




def main(argv):
    if not os.path.isdir("./index"):
        os.mkdir("./index")
    if not os.path.isdir("./para"):
        os.mkdir("./para")

    force = False
    if len(argv) > 1 and argv[1] in ["f", "force", "Force"]:
        force = True
    for casefile in os.listdir("./casefiles"):
        get_result("./casefiles/" + casefile, force)





if __name__ == '__main__':
    main(sys.argv)