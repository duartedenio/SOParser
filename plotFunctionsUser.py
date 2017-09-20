### How to use it:
###  The dictionary userTop must be populated: userTop=buildDict(dates,'-topicuserdist.txt','topics/')
###      in the example dates are the dates of the files, '-topicuserdist.txt' are the suffix and 'topics/' the folder (optional)
### Available functions:
###  buildTopic(tpId, threshold) builds a list SxU (S: # of slice time, U: # of users)
##                               with the probabilities associated to users      
###  plotUservsTop (threshold), plots the number of user by topic in all time slices
###  oneVsone (statistic function, first time slice ,data returned by buildTopic,arguments for statistic function)
###      returns a list of  p-values of the samples (slice_i x slice_i+1, slice_i+1 x slice_i+2 ....)
###              and a list for labeling X axis
###
###  oneVsall (statistic function, first time slice ,data returned by buildTopic,arguments for statistic function)
###      returns a list of  p-values of the samples (slice_first x slice_i+1, slice_first x slice_i+2 ....)
###              and a list for labeling X axis
###  PlotStats(statisc function, start, label of the graph, call oneVsAll (True) or oneVsone (False), threshold, list of topics, arguments for function)
###      plots a line graph with p-values of the samples being compared
###      calls buildTop, oneVsall or oneVsone for every topic and plots the result
###  Examples
###   t=buildTopic(10,.7) -> t is a list with 24 slices of time and n user probabilities for topic 10 
###   PlotStats(stats.ttest_ind,1,"Student's T test")
###      plots the p-values using t-test for all topics comparing the first slice with all others
###   PlotStats(stats.ttest_ind,1,"Student's T test",False)
###      plots the p-values using t-test for all topics comparing the two consective time slices from the fisrt one
###   PlotStats(stats.ttest_ind,1,"Student's T test",False,[3,4,5])
###      The same above but it plots only for topics 3,4, and 5.
import numpy as np
from scipy import stats

import matplotlib.pyplot as pl

def main():
  global userTop
  global colors
  global vslices
  userTop={}
  vslices=['Jan13','Feb13','Mar13','Apr13','May13','Jun13','Jul13','Aug13','Sep13','Oct13','Nov13','Dec13',
         'Jan14','Feb14','Mar14','Apr14','May14','Jun14','Jul14','Aug14','Sep14','Oct14','Nov14','Dec14']
  #
  dates=['2013-01','2013-02','2013-03','2013-04','2013-05','2013-06','2013-07','2013-08','2013-09','2013-10','2013-11','2013-12',
       '2014-01','2014-02','2014-03','2014-04','2014-05','2014-06','2014-07','2014-08','2014-09','2014-10','2014-11','2014-12']
  #
  colors=['yellow',   'orange', 'pink','black','blue','brown','coral','crimson','cyan','darkblue',
        'darkgreen','fuchsia','gold','green','grey','indigo','red','yellowgreen','navy','olive',
        'azure','orchid','beige','plum','purple','lavender','salmon','silver','violet','aqua','magenta']

  userTop=buildDict(dates,'-topicuserdist.txt','topics/')
  plotUservsTop(.5) ## plot the number of topics per user as time goes by
  ## plot the p-value from bartlett test for all topics from the first
  ## time slice
  PlotStats(stats.bartlett,1,"Bartlett's test",False)

       

### Create a dict "userTop" with all the probabilities
###      of a user to be associated to topics in 24 slices of time
###   userTop[0] refers to the first time slice
####     userTop[0][0] refers to users probabilities in the first topic in time slice 0
####
def buildDict(dates,filesuf,fileprex=''):
  userT={}
  for i in range(len(dates)):
    file=fileprex+dates[i]+filesuf
    lines=[line.split() for line in open(file)]
    matprob=[]
    for j in range(len(lines)):
       probs=[float(n) for n in lines[j]]
       matprob.append(probs)
    matprob=np.array(matprob)
    userT[i]=matprob
  return userT
###

####################### USERS and TOPICS
def plotUservsTop(trh=0.001):
  uvst=[]
  for i in range(20):
    t=[]
    for j in range(len(userTop)):
        t.append(np.count_nonzero(userTop[j][i]>trh))
    uvst.append(t)
  plist=[]
  for topId in range(20):
    plist.append(pl.plot(uvst[topId],color=colors[topId]))
  ltup=()
  ctup=()
  for i in range(20):
    ntup=(plist[i][0],)
    ltup=ltup+ntup
    ntup=('T'+str(i),)
    ctup=ctup+ntup
  pl.legend(ltup,ctup)
  pl.xticks(np.arange(0,len(userTop)),np.arange(1,len(userTop)+1))
  pl.ylabel('# of Users')
  pl.xlabel('Slices of time')
  pl.grid(True)
  pl.title('Threshold '+str(trh))
  pl.show()    


### Extract the user probabilities of the given topic tId for all time slices (24)
def buildTopic(tId,thres=0.001):
   tn=[]   ## stores the probabilities
   for i in range(24):
      tn.append(userTop[i][tId,userTop[i][tId]>=thres])
   return tn 

### given a stastic function (fct), a initial time slice, a dataset, the label correspondig to fct, and a topic tp
### plot the p-value from the start to point to all older ones.
def oneVsallPlot(fct,start,data,label,tp,**args):
  Xlabels=[]
  start=start-1
  for i in range(start+1,len(vslices)):
     Xlabels.append(vslices[start]+'x'+vslices[i])  ### labels
     
  pval=[]
  for i in range(1,len(Xlabels)+1):
     if not args:
        t,p=fct(data[start],data[start+i])
     else:
        t,p=fct(data[start],data[start+i],alternative='two-sided')
     pval.append(p)
  pl.plot(pval)
  pl.xticks(np.arange(0,len(Xlabels)),Xlabels,rotation=90)
  pl.title(label+"\nTopic: "+str(tp))
  pl.show()

def oneVsall(fct,start,data,**args):
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

def oneVsone(fct,start,data,**args):
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


def PlotStats(fct,start,label,oneXall=True,th=0,topics=None,**args):
    t=[]
    eTop=[]
    if topics is None:
       for i in range(20):
          eTop.append(i)
    else:
       eTop=topics
    for i in eTop:
       t.append(buildTopic(i,th))
    #
    plist=[]
    for i in range(len(t)):
       if not args:
          if oneXall:
             pv,xl=oneVsall(fct,start,t[i])
          else:
             pv,xl=oneVsone(fct,start,t[i])  
       else:
          if oneVsall:
             pv,xl=oneVsall(fct,start,t[i],**args)
          else:
             pv,xl=oneVsone(fct,start,t[i],**args)
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
    pl.title(label+'\nUsers in Topics - Threshold: '+str(th))
    pl.show()       


if __name__ == '__main__':
    main()
    
### Paired test must be done in samples having the same shape
    
######## KRUSKAL
## The Kruskal-Wallis H-test tests the null hypothesis that the population median of all of the groups are equal. 
## It is a non-parametric version of ANOVA. The test works on 2 or more independent samples, which may have different sizes. 
## Note that rejecting the null hypothesis does not indicate which of the groups differs. 
## Post-hoc comparisons between groups are required to determine which groups are different.
#ToneVsall(stats.kruskal,15,'Kruskal')  
#ToneVsall(stats.kruskal,15,'Kruskal',.5,[9,11,13,15]) ## probability >=.5 and topics 9,11,13,15  


##### STUDENT'S T TEST
## Calculates the T-test for the means of two independent samples of scores.
## This is a two-sided test for the null hypothesis that 2 independent samples have identical average (expected) values. 
## This test assumes that the populations have identical variances by default.
#ToneVsall(stats.ttest_ind,15,"Student's t test")

##### MANN-WHITNEY U
## The Mann-Whitney U test is a nonparametric test that allows two groups or conditions or treatments to be 
## compared without making the assumption that values are normally distributed. 
## So, for example, one might compare the speed at which two different groups of people can run 100 metres, 
## where one group has trained for six weeks and the other has not. 
#ToneVsall(stats.mannwhitneyu,15,'Mann Whitney',alternative='two-sided')
#ToneVsall(stats.mannwhitneyu,15,'Mann Whitney',.5,[9,11,13,15],alternative='two-sided')

##### KOLMOGOROV-SMIRNOV
## The Kolmogorov-Smirnov test (KS-test) tries to determine if two datasets differ significantly. 
## The KS-test has the advantage of making no assumption about the distribution of data. (Technically speaking it is non-parametric and distribution free.) 
## Note however, that this generality comes at some cost: other tests (for example Student's t-test) may be more sensitive if the 
## data meet the requirements of the test. 
#ToneVsall(stats.ks_2samp,15,'Kolmogorov-Smirnov')



### ToneVsall(stats.wilcoxon,15,'Wilcoxon') Not for samples with different sizes
### ToneVsall(stats.ttest_rel,15,"T test on Two Related") Not for samples with different sizes

### BARTLETT
## Bartlett’s test tests the null hypothesis that all input samples are from populations with equal variances
#ToneVsall(stats.bartlett,15,"Bartlett's test")

### LEVENE
## Perform Levene test for equal variances.
## The Levene test tests the null hypothesis that all input samples are from populations with equal variances. 
## Levene’s test is an alternative to Bartlett’s test bartlett in the case where there are significant deviations from normality.
#ToneVsall(stats.levene,15,"Levene's test")
