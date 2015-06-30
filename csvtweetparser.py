import csv
import re

__author__ = 'charoy'

bbox="-74.5354,40.2275,-73.2567,40.9926"
uplong=-74.5354
uplat=40.2275
dlong=-73.2567
dlat=40.9926
date='2012-10-27'

localtweets=open(date+'localtweets.csv','w')
with open('C:/Users/charoy/Downloads/twitterdata_hurricaneSandy2012-20121027_000000-20121107_235959_GMT.tsv','rb') as csvfile:
    tweetreader=csv.reader(csvfile,delimiter='\t', quotechar='|')
    for row in tweetreader:
        lat=float(row[4])
        long=float(row[5])
        if (lat!=10000):
            cdate=re.split(' ',row[2])[0]
            if (cdate>date):
                date=cdate
                localtweets.close()
                localtweets=open(date+'localtweets.csv','w')
                print date
            if ((lat>uplat) & (lat<dlat) & (long>uplong) & (long<dlong)):
                print('.')
                localtweets.write(row[2]+";"+row[4]+";"+row[5]+"\n")
