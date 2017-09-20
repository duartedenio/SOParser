#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree
import re, cgi, os, pickle, logging, time
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import pdb

def main():
    minposts = 50
    quarter=True
    
    years = [2013, 2014]
    
    extractUsers(minposts, years)
    extractComments(years,quarter)

def extractComments(years,isQuarter=False):
    quarters=['1stQ','2ndQ','3rdQ','4thQ']
    users = set()
    usersFile = open('rawdata/userposts.txt', 'r')
    for userline in usersFile:
        [user, number] = userline.strip().split('\t')
        users.add(user)
    usersFile.close()

    for year in years:
        print ("Parsing year: " + str(year))

        if not isQuarter:        
            months = range(1,13)
        else:
            months = range(1,5) ## 4 quarters in a year
        ####    
        for month in months:
            start = time.time()
            if not isQuarter:
                strmonth=str(month).zfill(2)
            else:
                strmonth=quarters[month-1] 
            #####       
            yearmonth = str(year) + "-" + strmonth
            print(yearmonth)
            #######
            ## Dealing with qaurter instead of months vvvvv
            #######
            if month == 1:
                if not isQuarter:
                    lastmonth = str(year-1) + "-12"
                else:
                    lastmonth = str(year-1) + '-' + quarters[-1]
            else:
                if not isQuarter:
                    lastmonth = str(year) + "-" + str(month-1).zfill(2) 
                else:
                    lastmonth = str(year) + "-" + quarters[month-2]
            ###        
            lastmonthsquestiontitlesfile = "data/" + lastmonth + "-questiontitles.dict"
            lastmonthsquestiontagsfile = "data/" + lastmonth + "-questiontags.dict"
            if os.path.isfile(lastmonthsquestiontitlesfile):
                logging.info('loading title dictionary: %s', lastmonthsquestiontitlesfile)
                logging.info('loading tag dictionary: %s', lastmonthsquestiontagsfile)
                questiontitles = {}
                questiontags = {}
                with open(lastmonthsquestiontitlesfile, 'rb') as f:  ## add b
                    questiontitles = pickle.load(f)
                    logging.info("Elements in questiontitles: %s", len(questiontitles))
                with open(lastmonthsquestiontagsfile, 'rb') as f: ## add b
                    questiontags = pickle.load(f)
                    logging.info("Elements in questiontags: %s", len(questiontags))
            else:
                logging.info("creating new dictionaries")
                questiontitles = {}
                questiontags = {}
            #######
            ## ^^^^^ End
            #######
            monthusers = set()
            parsedpostsfile = open("data/"+ yearmonth + "-titles-tags-text.tsv","a")
            rawpostsfile = open("rawdata/" + yearmonth + ".Posts.xml", 'r')
            for post in rawpostsfile:
                post = post.rstrip('\n')
                if "row Id" not in post:
                    continue
                doc = xml.etree.ElementTree.fromstring(post)
                rowID = doc.get('Id')
                logging.debug('Parsing doc: %s', rowID)
                ownerUserID = doc.get('OwnerUserId')
                if ownerUserID not in users:
                    continue
                monthusers.add(ownerUserID)
                creationDate = doc.get('CreationDate')
                postTypeId = doc.get('PostTypeId')
                score = doc.get('Score')
                #text = doc.get('Body').encode('utf8').replace('\r\n','').replace('\n','')
                text = doc.get('Body').replace('\r\n','').replace('\n','')
                tagremove = re.compile(r'(<!--.*?-->|<[^>]*>)')
                text = cgi.escape(tagremove.sub('', re.sub('<code>[^>]+</code>', '', text)))

                parent = doc.get('ParentId')
                if 'Title' in doc.keys():
                    #title = doc.get('Title').encode('utf8')
                    title = doc.get('Title')
                    if type(title) is bytes:
                        print('>>>>>>>> Byte')
                        title=title.decode('utf8')
                else:
                    title = ''
                if 'Tags' in doc.keys():
                    #tags = doc.get('Tags').encode('utf8').replace("><", ",").replace("<","").replace(">","")
                    tags = doc.get('Tags').replace("><", ",").replace("<","").replace(">","")
                    if type(tags) is bytes:
                        print('>>>>>>>> Byte')
                        tags=tags.decode('utf8')
                else:
                    tags = ''
                ####
                ##pdb.set_trace()
                ####
                if postTypeId == "1":
                    questiontags[rowID] = tags
                    questiontitles[rowID] = title
                else:
                    try:
                        tags = questiontags[parent]
                        title = questiontitles[parent]
                    except KeyError:
                        continue
                line = rowID + '\t' + ownerUserID + '\t' + creationDate + '\t' + score + "\t" + title + '\t' + tags + '\t' + text + "\n"
                parsedpostsfile.write(line)
            parsedpostsfile.close()
            rawpostsfile.close()

            #pdb.set_trace()
            with open("data/"+ yearmonth + "-titles-users.txt", 'w') as f:  
                f.write("\n".join(monthusers))
            with open("data/" + yearmonth + "-questiontitles.dict", 'wb') as f: ## add b (binary mode)
                pickle.dump(questiontitles, f, pickle.HIGHEST_PROTOCOL)
            with open("data/" + yearmonth + "-questiontags.dict", 'wb') as f: ## add b (binary mode)
                pickle.dump(questiontags, f, pickle.HIGHEST_PROTOCOL)
            end = time.time() - start
            logging.info("Elapsed time (s): %s", end)



def extractUsers(minPostCount, years):
    users = {}
    for year in years:
        print ("Parsing year: " +str(year))
        posts = open("rawdata/"+str(year)+".Posts.xml", 'r')
        for post in posts:
            post = post.rstrip('\n')
            if "row Id" not in post:
                continue
            doc = xml.etree.ElementTree.fromstring(post)
            creationDate = doc.get('CreationDate')
            if int(creationDate[:4]) not in years:
                continue
            # rowID = doc.get('Id')
            # postTypeId = doc.get('PostTypeId')
            # acceptedAnswerId = doc.get('AcceptedAnswerId')
            # score = doc.get('Score')
            # viewCount = doc.get('ViewCount')
            # text = doc.get('Body').encode('utf8')
            ownerUserID = doc.get('OwnerUserId')
            # lastEditorUserID = doc.get('LastEditorUserId')
            # lastEditorDisplayName = doc.get('LastEditorDisplayName')
            # lastEditDate = doc.get('LastEditDate')
            # lastActivityDate = doc.get('LastActivityDate')
            # title = doc.get('Title').encode('utf8')
            # tags = doc.get('Tags').encode('utf8')
            # answerCount = doc.get('AnswerCount')
            # commentCount = doc.get('CommentCount')
            # favoriteCount = doc.get('FavoriteCount')
            # communityOwnedDate = doc.get('CommunityOwnedDate')
            try:
                users[ownerUserID] = users[ownerUserID] + 1
            except KeyError:
                users[ownerUserID] = 1

    userPosts = open("rawdata/userposts.txt", 'a')
    for user in users:
        if users[user] > minPostCount:
            userPosts.write(str(user) + "\t" + str(users[user]) + "\n")
    userPosts.close()
    return set(users.keys())

if __name__ == '__main__':
    main()

