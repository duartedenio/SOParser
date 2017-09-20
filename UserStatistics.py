mergeDocs=False
dates = ['2013-1stQ','2013-2ndQ','2013-3rdQ','2013-4thQ','2014-1stQ','2014-2ndQ','2014-3rdQ','2014-4thQ']
topicthreshold = 0.3
dictionary = corpora.Dictionary.load("models/global-dictionary.dict")
document_users = {}
document_scores = {}
users = set()

if not mergeDocs:
	tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict.pdict"
else:
	tokenized_dictfile = "models/"+date+"-monthly-tokenized_dict-perUser.pdict"
####    
with open(tokenized_dictfile, 'rb') as f:
	tokenized_dict = cPickle.load(f)

usertopics = {}
userdoctopics = {}
usertopicscores = {}
documentfile = open("data/" + date + "-titles-tags-text.tsv")
topicfile = open("topics/" + date + "-topics.txt", 'w')
headerline = "UserID\ttopicID\tmeantopicvalue\tnumdocs\tmeantopicscore\ttopicword1\ttopicword2\ttopicword3\ttopicword4\ttopicword5\n"
topicfile.write(headerline)
lda = models.LdaMulticore.load("ldamodels/" + date + "-lda.model")

for doc in documentfile:
	[docid, userid, creationdate, score, title, tags, text] = doc.rstrip("\n").split("\t")
	if date == dates[0]:
		users.add(userid)
	else:
		if userid not in users:
			continue
	document_users[docid] = userid
	document_scores[docid] = score
	if not mergeDocs:
		sentence = tokenized_dict[docid]
	else:
		sentence = tokenized_dict[userid]
	bow = dictionary.doc2bow(sentence)
	documenttopics = lda[bow]
	for (topicid, topicvalue) in documenttopics:
		if topicvalue >= topicthreshold:
			try:
				userdoctopics[userid]
			except KeyError:
				userdoctopics[userid] = {}
				userdoctopics[userid][topicid] = []
				usertopicscores[userid] = {}
				usertopicscores[userid][topicid] = []
			try:
				userdoctopics[userid][topicid]
			except KeyError:
				userdoctopics[userid][topicid] = []
				usertopicscores[userid][topicid] = []
			userdoctopics[userid][topicid].append(topicvalue)
			usertopicscores[userid][topicid].append(int(score))
for userid in userdoctopics.keys():
	usertopics[userid] = {}
	for topicid in userdoctopics[userid].keys():
		meantopicvalue = numpy.mean(userdoctopics[userid][topicid])
		meantopicscore = numpy.mean(usertopicscores[userid][topicid])
		numdocs = len(userdoctopics[userid][topicid])
		if meantopicvalue < topicthreshold:
			continue
		usertopics[userid][topicid] = meantopicvalue
		topicterms = lda.get_topic_terms(topicid, topn=5)
		topicwords = ""
		for term in topicterms:
			topicwords += dictionary.get(term[0]).ljust(15) + "\t"
		resultline = str(userid)+"\t"+str(topicid)+"\t"+ str(meantopicvalue) + "\t" + str(numdocs) + "\t" + str(meantopicscore) + "\t" + str(topicwords) + "\n"
		# resultline = str(topicid) + "\t" + str(userid) + "\t" + str(meantopicvalue) + "\n"
		topicfile.write(resultline)
topicfile.close()
print('***** End (lookupTopics) ****')
