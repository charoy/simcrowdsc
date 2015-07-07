import flickr_api
# Copy images from flickr based on a bounding box and dates

__author__ = 'charoy'


user = flickr_api.Person.findByUserName("francois54")
print(user)
area="-74.5354,40.2275,-73.2567,40.9926"
starttime=1351468800 # Mon, 29 Oct 2012 00:00:00 GMT
duration=86400 # one day

for d in range(7):
    p= flickr_api.Photo.search(bbox=area,min_taken_date=str(starttime),max_taken_date=str(starttime+duration),page=1)
    print ("Day "+str(d))
    print(p)
    print p.info.pages # the number of available pages of results
    print p.info.page  # the current page number
    print p.info.total # total number of photos
    result=open(str(d)+"spositions.csv","w")
    for j in range(p.info.pages):
        for i in p:
            try:
                # print i
                loc=flickr_api.Photo.getLocation(i)
                print(loc)
                link=flickr_api.Photo.getPhotoFile(i,size_label = 'Large')
                info=flickr_api.Photo.getInfo(i)
                print info
                result.write(link+";"+str(loc.latitude)+";"+str(loc.longitude)+"\n")
                i.save("images/"+"day"+str(d+1)+"-"+str(i.id)+".jpg",size_label = 'Large')
            except:
                print "Unexpected error"
                pass
        try:
            p= flickr_api.Photo.search(bbox=area,min_taken_date=str(starttime),max_taken_date=str(starttime+duration),page=j)
            print(p)
        except:
            print("search error "+j+" "+d)
    starttime=starttime+duration
    result.close()
