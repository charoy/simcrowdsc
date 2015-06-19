__author__ = 'charoy'
from datetime import datetime, date, time
import time
import sys
import csv
import utils
import loaddata
import random




def tweetsreader(dumpname,result,latbnumber,longbnumber,latbsize,longbsize,area,bucketnumber):
    mintime=1500000000000
    maxtime=0
    milestone=0
    tweets=[]
    progress=[]
    bucket = [[0 for col in range(longbnumber+1)] for row in range(latbnumber+1)]
    counter=0
    with open(dumpname) as csvfile:
        reader=csv.reader(csvfile,delimiter=';',quotechar='"')
        for item in reader:
            if (len(item)<5):
                continue
            date=int(item[1])
            if (date>maxtime):
                maxtime=date
            if (date<mintime):
                mintime=date
                milestone=date+3600000
            if date>milestone:
                milestone=milestone+3600000
                progress.append([milestone,counter,utils.bucketcoverage(bucket)])
                result.write("%s;%s;%s\n" % (counter,utils.bucketcoverage(bucket),str((float(utils.bucketcoverage(bucket))/bucketnumber)*100)))
            lat=float(item[3])
            long=float(item[4])
            if (utils.belongs(area,lat,long)):
                latpos=lat-area[0][0];
                longpos=long-area[0][1];
                i=int(latpos/latbsize)
                j=int(longpos/longbsize)
                bucket[int(i)][int(j)]+=1
                tweets.append([date,latpos,longpos])
                counter+=1
    return [counter,tweets,bucket,progress,mintime,maxtime]

def photoquality(tweets,latbnumber,longbnumber,latbsize,longbsize):
    photos=[]
    photos = [[[] for col in range(longbnumber+1)] for row in range(latbnumber+1)]
    for tweet in tweets:
        latpos=tweet[1]
        longpos=tweet[2];
        i=int(latpos/latbsize)
        j=int(longpos/longbsize)
        photos[i][j].append(utils.picturequality())
    return photos

def initvotes(photos,lat,long):
    votes = [[[] for col in range(long+1)] for row in range(lat+1)]
    for i in range (0,lat):
        for j in range (0,long):
            votes[i][j]=[0 for row in range(len(photos[i][j]))]
    return votes

def bestphotovote(nbvote,photos, k,latbnumber,longbnumber,workerquality):
    votes=initvotes(photos,latbnumber,longbnumber)
    for v in range (0,nbvote):
        cf=utils.countfinalvotes(votes,k)
        if (latbnumber*longbnumber==cf):
            print "tous les buckets ont eu un vote suffisant"
            return votes
        b=utils.selectvalidplace(photos,votes,latbnumber,longbnumber,k)
        if (b==None):
            print "plus de place"
            return votes
        photos[b[0]][b[1]].sort(reverse=True)
        #print photos[b[0]][b[1]]
        v=utils.photovote(photos[b[0]][b[1]],workerquality)
        if (v>=0):
            votes[b[0]][b[1]][v]+=1
    return votes

def getbestphotos(photos,votes,k,latbnumber,longbnumber):
    pictures= [[0 for col in range(longbnumber+1)] for row in range(latbnumber+1)]
    pvoted=0
    for i in range (0,latbnumber+1):
        for j in range(0,longbnumber+1):
            indice=utils.bestvote(votes[i][j],k)
            if (indice>=0):
                pictures[i][j]=photos[i][j][indice]
                pvoted+=1
            else:
                pictures[i][j]=-1
    return pictures

def getrealbestphotos(photos,latbnumber,longbnumber):
    pictures= [[0 for col in range(longbnumber+1)] for row in range(latbnumber+1)]
    for i in range (0,latbnumber+1):
        for j in range(0,longbnumber+1):
            if len(photos[i][j])>0:
                best=max(photos[i][j])
                if (best>=0):
                    pictures[i][j]=best
                else:
                    pictures[i][j]=-1
            else:
                pictures[i][j]=-1
    return pictures

def comparephotos(realbestphotos, bestphotos,latbnumber,longbnumber):
    countbest=0
    countdiff=0
    squarediff=0
    for i in range (0,latbnumber+1):
        for j in range(0,longbnumber+1):
            if bestphotos[i][j]>=0:
                if realbestphotos[i][j]==bestphotos[i][j]:
                    countbest=countbest+1
                else:
                    squarediff+=(realbestphotos[i][j]-bestphotos[i][j])**2
                    countdiff+=1
    return [countbest,countdiff,squarediff]

def photograding(nbgrad,pictures,lat,long,scale,k,wquality,groundtruth):
    print "%s %s " % (lat,long)
    photograde= [[[] for col in range(long+1)] for row in range(lat+1)]
    for i in range (0,lat+1):
        for j in range (0,long+1):
            if pictures[i][j]>=0:
                photograde[i][j]=[0 for row in range(len(scale)+1)]
    for tweet in range (0,nbgrad):
        cf=utils.countfinalvotes(photograde,k)
        if (lat*long==cf):
            print "tous les buckets ont eu un vote suffisant"
            return photograde
        b=utils.selectvalidplace(pictures,photograde,lat,long,k)
        if (b==None):
            print "plus de place"
            return photograde
        sc=list(scale)
        sc[0]=groundtruth[b[0]][b[1]]
        sc[groundtruth[b[0]][b[1]]]=0
        v=utils.photorank(pictures[b[0]][b[1]],sc,wquality)
        if v>=0:
            photograde[b[0]][b[1]][v]+=1
    return photograde

def finalresult(photoselection,votecount,lat,long,groundtruth):
    finalcounter=0
    exactresult=0
    finalresult=[[0 for col in range(long+1)] for row in range(lat+1)]
    for i in range (0,lat):
        for j in range (0,long):
            if (photoselection[i][j]==[]):
                continue
            v=max(photoselection[i][j])
            if (v>=votecount):
                finalresult[i][j]=photoselection[i][j].index(v)
                finalcounter+=1
                if finalresult[i][j]==groundtruth[i][j]:
                    exactresult+=1
            else:
                finalresult[i][j]=-1
    return [finalcounter,exactresult,finalresult]

def processdata(id,votecount,workerquality,area,bsize,prop):
    result=open("%s-%s-result.csv" % (id,votecount),'a+')
    result.write("statistics for dataset %s\n" % id)
    result.write("time %d\n" % time.time())
    result.write("vote count %s\n" % votecount)
    result.write("---\n")

    # Bucket size in meter
    result.write("Bucket size %s m\n" % bsize)
    latdiff=area[1][0]-area[0][0]
    longdiff=area[1][1]-area[0][1]
    latsize=utils.distance_on_unit_sphere(area[0][0],area[0][1],area[1][0],area[0][1],6373000)
    longsize=utils.distance_on_unit_sphere(area[0][0],area[0][1],area[0][0],area[1][1],6373000)
    #Number of bucket for lat and long
    latbnumber=int(latsize/bsize)
    longbnumber=int(longsize/bsize)
    #number of bucket regarding the lat and long dimension
    latbsize=latdiff/latbnumber
    longbsize=longdiff/longbnumber
    result.write("grid = %s x %s\n" % (latbsize,longbsize))
    bucketnumber=latbnumber*longbnumber
    result.write("bucket number = %s\n" % bucketnumber)

    rankcount=5
    result.write("vote , rank = %s, %s\n" % (votecount,rankcount))


    result.write("nbtweet;nbnonvide;pourcentage\n")
    dumpname="%sdump.csv" % id
    print dumpname
    tweetresult=tweetsreader(dumpname,result,latbnumber,longbnumber,latbsize,longbsize,area,bucketnumber)
    counter=tweetresult[0]
    tweets=tweetresult[1]
    bucket=tweetresult[2]
    progress=tweetresult[3]
    mintime=tweetresult[4]
    maxtime=tweetresult[5]

    result.write("Debut %s\n" % utils.dateMicrosTimestampTexte(mintime))
    result.write("Fin %s\n" % utils.dateMicrosTimestampTexte(maxtime))

    result.write("Nombre de tweet : %s\n" % counter)
    result.write("Couverture %s\n" % utils.bucketcoverage(bucket))
    result.write("Pourcentage couvert %s\n" % str((float(utils.bucketcoverage(bucket))/bucketnumber)*100))

    utils.savebucket(bucket,result)

    photos=photoquality(tweets,latbnumber,longbnumber,latbsize,longbsize)

    votes=bestphotovote(int(2*counter*prop),photos,votecount,latbnumber,longbnumber,workerquality)

    bestphotos=getbestphotos(photos,votes,votecount,latbnumber,longbnumber)
    realbestphotos=getrealbestphotos(photos,latbnumber,longbnumber)



    accuracy=comparephotos(realbestphotos,bestphotos,latbnumber,longbnumber)
    print accuracy
    result.write("True positive %s\n" % accuracy[0])
    result.write("Not accurate %s\n" % accuracy[1])

    result.write("Square diff %s\n" % accuracy[2])
    pcoverage=utils.photocoverage(bestphotos)
    averagequality=utils.averagequality(bestphotos)
    utils.savebucket(bestphotos,result)
    print pcoverage
    print averagequality
    result.write("Couverture photo %s\n" % pcoverage)
    result.write("Average Quality %s\n" % averagequality)

    groundtruth=utils.generateGroundTruth(latbnumber,longbnumber,2)
    photograde=photograding(int(2*counter*(1-prop)),bestphotos,latbnumber,longbnumber,[0,1,2],votecount,workerquality,groundtruth)
    finalvalue=finalresult(photograde,votecount,latbnumber,longbnumber,groundtruth)
    print "final %s" % finalvalue[0]
    result.write("final result\n")
    utils.savebucket(finalvalue[2],result)


    final=open("%seval.csv" % id,'a+')
    final.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % (votecount,bucketnumber,bsize,workerquality,prop,pcoverage,averagequality,accuracy[0],accuracy[1],accuracy[2],finalvalue[0],finalvalue[1]))
    final.close()
    result.close()

    print "done"

def loop(id,area):
    count=[1,3,5,7]
    wquality=[0.8]
    bsize=[50,100,200]
    proportion=[0.5,0.55,0.6,0.65,0.7,0.75,0.80]
    for k in bsize:
        print k
        for i in count:
            print i
            for j in wquality:
                print j
                for l in proportion:
                    print l
                    processdata(id,i,j,area,k,l)

if __name__ == "__main__":
    id = 54
#    votecount = int(sys.argv[2])
#    workerquality=float(sys.argv[3])
    area=loaddata.load_data(id)
    loop(id,area)

