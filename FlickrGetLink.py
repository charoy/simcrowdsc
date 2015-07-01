__author__ = 'charoy'
import re

list=open("flickrfilename",'r')

for line in list:
    fid=re.sub(r'^day[0-9]*-([0-9]*)\.jpg',r'\1',line)
    print fid

