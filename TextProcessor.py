from __future__ import print_function
from gensim import corpora, models
from gensim.parsing.preprocessing import STOPWORDS
import logging, re, numpy
import _pickle as cPickle ## Python 3 does not have cPickle
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

import pdb


def main():
    """Main entry."""
    global priorweight
    dates = ['2013-1stQ','2013-2ndQ','2013-3rdQ','2013-4thQ','2014-1stQ','2014-2ndQ','2014-3rdQ','2014-4thQ']
    #dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12',
    #         '2014-01', '2014-02', '2014-03', '2014-04', '2014-05', '2014-06', '2014-07', '2014-08', '2014-09', '2014-10', '2014-11', '2014-12']

    #dates = ['2013-01', '2013-02', '2013-03', '2013-04', '2013-05', '2013-06', '2013-07', '2013-08', '2013-09', '2013-10', '2013-11', '2013-12']

    numtopics = 40
    vocabsize = 2000

    priorweight = 0.05
    workers = 1
    
    merge=True
    ########
    filterUsers(dates)
    createDictionariesFromFiles(dates)
    createGlobalDictionaryFromMonthly(dates, vocabsize,merge)
    createMonthCorpuses(dates,merge)
    
    performTFIDF(dates,merge)
    #######
    performLDA(dates, numtopics, vocabsize, workers,merge)
    #######
    #lookupTopics(dates)

    #lookatdist(dates[1])
    #######


def lookatdist(date):
    lda = models.LdaModel.load("ldamodels/" + date + "-lda.model")
    # lda = models.LdaMulticore.load("ldamodels/" + date + "-lda.model")
    print(lda.LdaState.get_lambda())
    # ldalambda = lda.get_lambda()
    # print(ldalambda)

# run this to only get users that exist in all months
def filterUsers(dates):
    users = set()
    for date in dates:
        musers = set()
        for line in open("data/" + str(date) + "-titles-users.txt", "r"):  #"-title-users.txt", "r"):
            musers.add(line.strip("\n"))
        if len(users) == 0:
            users = musers
        else:
            users = set.intersection(users, musers)
    ufile = open("data/all-month-users.txt", "w")
    for user in users:
        ufile.write(user + "\n")
    ufile.close()


def readFile(date):
    original_sentences = {}
    for line in open("data/" + date + "-posts.tsv"):
        [id, postDate, type, score, title, text, tags] = line.split('\t')
        original_sentences[id] = text
    return original_sentences

def lookupLDATopics(date, docIDs, numTopics, mergeDocs=False):
    if not mergeDocs:
        tokenized_dictfile="models/global-tokenized_dict.pdict"
    else:
        tokenized_dictfile="models/global-tokenized_dict-perUser.pdict"
    #####    
    with open(tokenized_dictfile, 'rb') as f:
        tokenized_dict = cPickle.load(f)
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    lda = models.LdaModel.load("ldamodels/"+date+"-lda.model")
    for docID in docIDs:
        sentence = tokenized_dict[str(docID)]
        bow = dictionary.doc2bow(sentence)
        topics = lda[bow]
        topics_by_value = sorted(topics, key=lambda tup: tup[1], reverse=True)
        return topics_by_value[:numTopics]

def calculateEta(dates, date, numtopics, vocabsize,mergeDocs=False):
    priordate = dates[dates.index(date) - 1]
    if not mergeDocs:
	    suffix="-monthly-tokenized_dict.pdict"
    else:
        suffix="-monthly-tokenized_dict-perUser.pdict"
    tokenized_dictfile = "models/"+priordate+suffix
    with open(tokenized_dictfile, 'rb') as f:
        tokenized_dict = cPickle.load(f)
    dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
    priorlda = models.LdaMulticore.load("ldamodels/" + priordate + "-lda.model")

    countedwordtopics = []
    [countedwordtopics.append(0) for i in range(numtopics)]
    for docID in tokenized_dict.keys():
        doc = tokenized_dict[docID]
        bow = dictionary.doc2bow(doc)
        wordcount = len(bow)
        priordoctopics = priorlda[bow]
        for doctopic in priordoctopics:
            topicID = doctopic[0]
            topicvalue = wordcount * doctopic[1]
            countedwordtopics[topicID] = countedwordtopics[topicID] + topicvalue * priorweight

    indexes = priorlda.id2word
    priortopics = priorlda.show_topics(num_topics=-1, num_words=vocabsize, formatted=False)
    eta = numpy.zeros((numtopics, vocabsize))
    reverseindexes = dict(zip(indexes.values(), indexes.keys()))
    for priortopic in priortopics:
        topicID = priortopic[0]
        worddist = priortopic[1]
        for wordTuple in worddist:
            word = wordTuple[0]
            value = wordTuple[1]
            wordindex = reverseindexes[word]
            eta[topicID][wordindex] = value * countedwordtopics[topicID]
    return  eta

def calculateEta2(dates, date, numtopics, vocabsize, minpriorvalue):
    prioldafile = "ldamodels/" + dates[dates.index(date) - 1] + "-lda.model"
    logging.info("loading " + prioldafile)
    priorlda = models.LdaMulticore.load(prioldafile)
    eta = numpy.zeros((numtopics, vocabsize))

    topics = priorlda.show_topics(num_topics=-1, num_words=2000, formatted=False)
    indexes = priorlda.id2word
    reverseindexes = dict(zip(indexes.values(), indexes.keys()))
    for topic in topics:
        topicid = topic[0]
        wordlist = topic[1]
        for wordtuple in wordlist:
            word = wordtuple[0]
            value = wordtuple[1]
            if value < minpriorvalue:
                value = 0
            index = reverseindexes[word]
            eta[topicid][index] = value
    return eta

def performTFIDF(dates, mergeDocs=False):
    for date in dates:
        if not mergeDocs:
            suffix_tok="-tokenized.mm"
            suffix_tfidf_model="-tfidf.model"
            suffix_tfidf_corpus="-tfidf.mm"
        else:
            suffix_tok="-tokenizedUser.mm"
            suffix_tfidf_model="-tfidfUser.model"
            suffix_tfidf_corpus="-tfidfUser.mm"

        corpus = corpora.MmCorpus("models/" + date + suffix_tok)
        tfidf = models.TfidfModel(corpus)
        tfidf.save("models/"+date+ suffix_tfidf_model)
        tfidf_corpus = tfidf[corpus]
        corpora.MmCorpus.save_corpus("models/"+date+ suffix_tfidf_corpus, tfidf_corpus)

def performLDA(dates, numtopics, vocabsize, workers,mergeDocs=False):
    for date in dates:
        if not mergeDocs:
            suffix="-tfidf.mm"
        else:
            suffix="-tfidfUser.mm"
        print("performing lda on " + str(date))
        dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
        corpus = corpora.MmCorpus("models/" + date + suffix)
        if date != dates[0] and priorweight != 0:
            logging.info("Calculating eta based on prior month")
            eta = calculateEta(dates, date, numtopics, len(dictionary.keys()),mergeDocs)  ## vocabsize -> len(dictionary.keys()) SAFER!
            # pdb.set_trace()
            lda = models.LdaMulticore(corpus, id2word=dictionary, num_topics=numtopics, workers=workers, eta=eta)
        else:
            logging.info("Eta weighting factor too low or no prior months")
            lda = models.LdaMulticore(corpus, id2word=dictionary, num_topics=numtopics, workers=workers)
        lda_corpus = lda[corpus]
        corpora.MmCorpus.serialize('ldamodels/' + date + '-lda.mm', lda_corpus)
        lda.save('ldamodels/' + date + '-lda.model')

def tokenizeandstemline(text):
    stoplist = STOPWORDS
    stemmer = PorterStemmer()
    ### Python 3 does not have str.decode, and the method PorterStemmer.stem() has a bug
    #tokenized_line = [stemmer.stem(word.lower()) for word in word_tokenize(text.decode('utf-8'), language='english') if word not in stoplist and len(word) > 3 and re.match('^[\w-]+$', word) is not None]
    tokenized_line = [stemmer.stem(word.lower()) for word in word_tokenize(text, language='english') if word not in stoplist and len(word) > 3 and re.match('^[\w-]+$', word) is not None]
    ###
    return tokenized_line

def writecpicklefile(content, filename):
    with open(filename, 'wb') as f:
        cPickle.dump(content, f, -1) #cPickle.HIGHEST_PROTOCOL) ## Python 3 does not have the macro HIGHEST_PROTOCOL


def createGlobalDictionaryFromMonthly(dates, vocabsize, mergeDocs=False):
    global_tokenized_dict = {}
    for date in dates:
        if not mergeDocs:
            suffix="-monthly-tokenized_dict.pdict"
        else:
            suffix="-monthly-tokenized_dict-perUser.pdict"
        monthly_tokenized_dictfile = "models/" + date + suffix
        with open(monthly_tokenized_dictfile, 'rb') as f:
            logging.info("Opening file %s", monthly_tokenized_dictfile)
            global_tokenized_dict = merge_two_dicts(cPickle.load(f), global_tokenized_dict)
    logging.info("Creating corpora.Dictionary")
    dictionary = corpora.Dictionary(global_tokenized_dict.values())
    logging.info("Compressing dictionary of size: %s", len(dictionary))
    dictionary.filter_extremes(no_below=200, no_above=0.8, keep_n=vocabsize)
    dictionary.compactify()
    logging.info("Dictionary size: %s", len(dictionary))
    dictionary.save('models/global-dictionary.dict')

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def createDictionariesFromFiles(dates):
    for date in dates:
        print("parsing month: " + date)
        monthly_tokenized_dict = {}
        ####
        monthly_tokenized_byUser = {}
        ####
        monthly_original_dict = {}
        docids = {}
        for line in open("data/" + date + "-titles-tags-text.tsv"):
            [id, userid, postDate, score, title, tags, text] = line.split('\t')
            docids[id] = (userid, score)
            text = title + " " + tags + " " + text
            tokenized_line = tokenizeandstemline(text)
            monthly_tokenized_dict[id] = tokenized_line.copy()
            monthly_original_dict[id] = text
            #### merge all user's documents 
            if userid in monthly_tokenized_byUser:
                monthly_tokenized_byUser[userid].extend(tokenized_line.copy())
            else:
                monthly_tokenized_byUser[userid]=tokenized_line.copy()
            ####
        ### pdb.set_trace() ## just in case :)
        monthly_docids_dictfile = "models/"+date+"-docids.pdict"
        writecpicklefile(docids, monthly_docids_dictfile)
        monthly_tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict.pdict"
        writecpicklefile(monthly_tokenized_dict, monthly_tokenized_dictfile)
        ####
        monthly_tokenized_dictfile_perUser = "models/"+date+"-monthly-tokenized_dict-perUser.pdict"
        writecpicklefile(monthly_tokenized_byUser, monthly_tokenized_dictfile_perUser)
        ####
        monthly_original_dictfile = "models/"+date+"-monthly-original_dict.pdict"
        writecpicklefile(monthly_original_dict, monthly_original_dictfile)

def createMonthCorpuses(dates,mergeDocs=False):
    for date in dates:
        logging.info("Parsing date: %s", date)
        print("parsing month: " + date)
        if not mergeDocs:
            suffix_source="-monthly-tokenized_dict.pdict"
            suffix_target='-tokenized.mm'
        else:
            suffix_source="-monthly-tokenized_dict-perUser.pdict"
            suffix_target='-tokenizedUser.mm'
		    
        monthly_dict_file = "models/" + date + suffix_source
        with open(monthly_dict_file, 'rb') as f:
            tokenized_dict = cPickle.load(f)
        dictionary = corpora.Dictionary.load('models/global-dictionary.dict')
        corpus = [dictionary.doc2bow(sentence) for sentence in tokenized_dict.values()]
        corpora.MmCorpus.serialize('models/' + date + suffix_target, corpus)


if __name__ == '__main__':
    main()
