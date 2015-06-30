import flickr_api
# Copy images from flickr based on a bounding box and dates

__author__ = 'charoy'


user = flickr_api.Person.findByUserName("francois54")
print(user)

p= flickr_api.Photo.search(bbox="-74.5354,40.2275,-73.2567,40.9926",min_upload_date='1351468800',max_upload_date='1351555200',page=1)
print(p)
print p.info.pages # the number of available pages of results
print p.info.page  # the current page number
print p.info.total # total number of photos
result=open("positions.csv","w")
for j in range(p.info.pages):
    for i in p:
        try:
        # print i
            loc=flickr_api.Photo.getLocation(i)
            print(loc)
            result.write(str(loc.latitude)+";"+str(loc.longitude)+"\n")
            i.save("images/"+str(i.id)+".jpg",size_label = 'Medium 640')
        except:
            print "Unexpected error"
            pass

    p= flickr_api.Photo.search(bbox="-74.5354,40.2275,-73.2567,40.9926",min_upload_date='1351468800',max_upload_date='1351555200',page=j)
    print(p)

f.close()