### How to use it:
###  The dictionary userTop must be populated: docTop=buildDict(dates,'-doctopicdist.txt','topics/DocDistrib/')
###      in the example dates are the dates of the files, '-doctopicdist.txt' are the suffix and 'topics/DocDistrib/' the folder (optional)
### Available functions:
###  buildDocTopic(tpId, threshold) builds a list SxD (S: # of slice time, D: # of documents)
###                               with the probabilities associated to documents      
###  plotDocrvsTop (threshold), plots the number of documents by topic in all time slices
###  oneVsoneDocs (statistic function, first time slice ,data returned by buildTopic,arguments for statistic function)
###      returns a list of  p-values of the samples (slice_i x slice_i+1, slice_i+1 x slice_i+2 ....)
###              and a list for labeling X axis
###
###  oneVsallDocs (statistic function, first time slice ,data returned by buildTopic,arguments for statistic function)
###      returns a list of  p-values of the samples (slice_first x slice_i+1, slice_first x slice_i+2 ....)
###              and a list for labeling X axis
###  PlotStatsDocs(statisc function, start, label of the graph, call oneVsAll (True) or oneVsone (False), threshold, list of topics, arguments for function)
###      plots a line graph with p-values of the samples being compared
###      calls buildTop, oneVsall or oneVsone for every topic and plots the result
###  Examples
###   t=buildTopic(10,.7) -> t is a list with 24 slices of time and n document probabilities for topic 10 
###   PlotStatsDocs(stats.ttest_ind,1,"Student's T test")
###      plots the p-values using t-test for all topics comparing the first slice with all others
###   PlotStatsDocs(stats.ttest_ind,1,"Student's T test",False)
###      plots the p-values using t-test for all topics comparing the two consective time slices from the fisrt one
###   PlotStatsDocs(stats.ttest_ind,1,"Student's T test",False,[3,4,5])
###      The same above but it plots only for topics 3,4, and 5.

import numpy as np
from scipy import stats
import matplotlib.pyplot as pl

def main():
  global docTop
  global colors
  global vslices
  docTop={}
  vslices=['Jan13','Feb13','Mar13','Apr13','May13','Jun13','Jul13','Aug13','Sep13','Oct13','Nov13','Dec13',
         'Jan14','Feb14','Mar14','Apr14','May14','Jun14','Jul14','Aug14','Sep14','Oct14','Nov14','Dec14']

  dates=['2013-01','2013-02','2013-03','2013-04','2013-05','2013-06','2013-07','2013-08','2013-09','2013-10','2013-11','2013-12',
       '2014-01','2014-02','2014-03','2014-04','2014-05','2014-06','2014-07','2014-08','2014-09','2014-10','2014-11','2014-12']
  #
  colors=['yellow',   'orange', 'pink','black','blue','brown','coral','crimson','cyan','darkblue',
        'darkgreen','fuchsia','gold','green','grey','indigo','red','yellowgreen','navy','olive',
        'azure','orchid','beige','plum','purple','lavender','salmon','silver','violet','aqua','magenta']

  docTop=buildDict(dates,'-doctopicdist.txt','topics/DocDistrib/')
  plotDocvsTop(.5) ## plot the number of topics per topic per time slice
  ## plot the p-value from bartlett test for all topics from the first
  ## time slice
  PlotStatsDocs(stats.bartlett,1,"Bartlett's test",False,.05,[3,5,7,9,11])

### build a dictionary with all probabilities and documents
### docTop size is 24 (24 slices of time)
### doctop[n] is 20 (20 topics in slice n)
### doctop[n][t] is the probabilities of documents to be associated to
###   topic t in slice n
def buildDict(dates,filesuf,fileprex=''):
  #### topics vs docs
  docT={}
  for i in range(len(dates)):
     file=fileprex+dates[i]+filesuf
     lines=[line.split() for line in open(file)]
     matprob=[]
     for j in range(len(lines)):
         probs=[float(n) for n in lines[j]]
         matprob.append(probs[1:])
     matprob=np.array(matprob)
     docT[i]=matprob
  return docT   
### Build the doc probabilities by topic

## plot the number of documents per topic in each slice of time
## thr is the probability threshold
def plotDocvsTop(thr=0.01):
  plist=[]
  for i in range(len(docTop[0])):
    p=[]
    for j in range(len(docTop)):
      p.append(len([i for i in docTop[j][i] if i > thr]))
    plist.append(pl.plot(p))
  ltup=()
  ctup=()
  for i in range(len(plist)):
     ntup=(plist[i][0],)
     ltup=ltup+ntup
     ntup=('T'+str(i),)
     ctup=ctup+ntup
  pl.legend(ltup,ctup)
  pl.ylabel('# of documents')
  pl.xticks(np.arange(0,24),np.arange(1,24))
  pl.grid(True)
  pl.title('Documents per topics\n Threshold: '+str(thr))
  pl.show()       


### build list for the documents probabilities in a given topic (tId)
### and a given threshol (thres)
### the list NxP, where N is the slice number and P the documents
### probabilities for tId in that slice (P is not fixed in the slices)
def buildDocTopic(tId,thres=0.001):
   tn=[]   ## stores the probabilities
   for i in range(24):
      tn.append([i for i in docTop[i][tId] if i > thres])
   return tn 

def oneVsallDocsPlot(fct,start,data,tp,label,**args):
  Xlabels=[]
  start=start-1
  for i in range(start+1,len(vslices)):
     Xlabels.append(vslices[start]+'x'+vslices[i])  ### labels
     
  pval=[]
  for i in range(1,len(Xlabels)+1):
     if not args:
        t,p=fct(data[start],data[start+i])
     else:
        key=list(args)[0]
        val=args.get(key)
        args={key:val}  
        t,p=fct(data[start],data[start+i],**args)
     pval.append(p)
  pl.plot(pval)
  pl.xticks(np.arange(0,len(Xlabels)),Xlabels,rotation=90)
  pl.title(label+"\nTopic: "+str(tp))
  pl.show()
     
  

### Returns the p-value for fct (stats.<function>), comparing <start> (1 is the first) to all following time slices
### for the document probabilities in a topic defined by data
### args is used as parameters for fct (if it is necessary)   
def oneVsallDocs(fct,start,data,**args):
  Xlabels=[]
  start=start-1
  for i in range(start+1,len(vslices)):
     Xlabels.append(vslices[start]+'x'+vslices[i])  ### labels
     
  pval=[]
  for i in range(1,len(Xlabels)+1):
     if not args:
        t,p=fct(data[start],data[start+i])
     else:
        key=list(args)[0]
        val=args.get(key)
        args={key:val}  
        t,p=fct(data[start],data[start+i],**args)
     pval.append(p)
  return pval,Xlabels

### Returns the p-value for fct (stats.<function>), from <start> (1 is the first) to all following time slices
### comparing two slices in a row: jan13xfev13, fev13xmar13, and so on
### for the document probabilities in a topic defined by data
### args is used as parameters for fct (if it is necessary)   
def oneVsoneDocs(fct,start,data,**args):
  Xlabels=[]
  start=start-1
  for i in range(start,len(vslices)-1):
     Xlabels.append(vslices[i]+'x'+vslices[i+1])  ### labels
     
  pval=[]
  for i in range(start,len(Xlabels)+start):
     if not args:
        t,p=fct(data[i],data[i+1])
     else:
        key=list(args)[0]
        val=args.get(key)
        args={key:val}  
        t,p=fct(data[i],data[i+1],**args)
     pval.append(p)
  return pval,Xlabels

### Plots all topics in slices from <start> (1 is the first), with p-value
### calculate by fct. label is the name of the statistical function to
### appear in the title, topics is a list of topics to be plot (none=all)
### args is to be passed to fct
def PlotStatsDocs(fct,start,label,oneVsall=True,th=0,topics=None,**args):
    t=[]
    eTop=[]
    if topics is None:
       for i in range(20):
          eTop.append(i)
    else:
       eTop=topics
    for i in eTop:
       t.append(buildDocTopic(i,th))
    #
    plist=[]
    for i in range(len(t)):
       if not args:
          if oneVsall:
             pv,xl=oneVsallDocs(fct,start,t[i])
          else:
             pv,xl=oneVsoneDocs(fct,start,t[i])  
       else:
          if oneVsall:
             pv,xl=oneVsallDocs(fct,start,t[i],**args)
          else:
             pv,xl=oneVsoneDocs(fct,start,t[i],**args)
       plist.append(pl.plot(pv,color=colors[i]))
    #
    ltup=()
    ctup=()
    j=0
    for i in range(len(plist)):
       ntup=(plist[i][0],)
       ltup=ltup+ntup
       eTop[j]
       ntup=('T'+str(eTop[j]),)
       j=j+1
       ctup=ctup+ntup
    #
    pl.legend(ltup,ctup)
    pl.ylabel('p-value')
    pl.grid(True)
    pl.xticks(np.arange(0,len(xl)),xl,rotation=90)
    pl.title(label+'\nDocuments in Topics - Threshold: '+str(th))
    pl.show()       

if __name__ == '__main__':
    main()
