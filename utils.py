__author__ = 'charoy'
import math
import random
import time


def belongs(area,lat,long):
    if ((lat<area[0][0])):
        return False
    if (lat>area[1][0]):
        return False
    if (long<area[0][1] or long>area[1][1]):
        return False
    return True

def dateMicrosTimestampTexte(micros):
	return str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(micros)/1000)))

def bucketcoverage(bucket):
    notempty=0
    for x in bucket:
        for y in x:
            if (y>0):
                notempty+=1
    return notempty

def savebucket(bucket,f):
    for x in bucket:
        for y in x:
            f.write("%s;" % y)
        f.write("\n")

# picture quality : normal distribution with a mean of 0.7
def picturequality():
    result=random.gauss(0.7,0.15)
    if (result>1):
        result=1
    return result

# selection model for the photo selection.
# the utility function needs to be discussed
def photovote(photonumbers,workerquality):
    if (len(photonumbers)==0):
        return -1
    wquality=random.gauss(workerquality,0.10)
    if (wquality>1):
        wquality=1
    res=0
    utility=[]
    for p in photonumbers:
        u=random.gauss(p,1-wquality)
        utility.append(u)
    # print "-----------------------"
    # print wquality
    # print photonumbers
    # print utility
    return utility.index(max(utility))

# if we don't select the ground truth, other values have equal chances to be retrieved
# this has to be discussed as well
def photorank(photo,scale,workerquality):
    wquality=random.gauss(workerquality,0.10)
    if (wquality>1):
        wquality=1
    p=photo*wquality
    r=random.random()
    if (p>r):
        return scale[0]
    v=random.randint(1,len(scale)-1)
    return scale[v]



def selectplace(photos,lat,long):
    while True:
        i=random.randint(0,lat)
        j=random.randint(0,long)
        if (photos[i][j]
                !=[] and photos[i][j]>0):
            return [i,j]

# return a groudtruth value between 0 and n
# the higher the value, the less probable
def gettruth(n):
    v=random.expovariate(0.5)
    if (v>1):
        v=1
    return int(round(v*n,0))


def distance_on_unit_sphere(lat1, long1, lat2, long2,r):
    #from http://www.johndcook.com/blog/python_longitude_latitude/
    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc*r

def getdbconnection():
    return psycopg2.connect(database='geotweet', user='postgres', host='127.0.0.1', password='A0Z9E8');



def truepositive(groundtruth,results):
    counter=0
    for i in range(0,len(groundtruth)):
        for j in range(0,len(groundtruth[i])):
            if (groundtruth[i][j]==results[i][j]):
                counter+=1
    return counter

def bestvote(photovote, k):
    if (len(photovote)==0):
        return -1
    indice=photovote.index(max(photovote))
    if photovote[indice]<k:
        return -1
    else:
        return indice
    return -1


def nextPlace(place,lat,long):
    place[0]+=1;
    if (place[0]>lat-1):
        place[0]=0
        place[1]+=1
        if (place[1]>long-1):
            place[1]=0
    return place

def selectvalidplace(photos,votes,lat,long,k):
    place=[]
    iplace=selectplace(photos,lat,long)
    place=list(iplace)
    while True:
        if photos[place[0]][place[1]] >0:
            res=bestvote(votes[place[0]][place[1]],k)
            if (res<0):
                return place
        place=nextPlace(place,lat,long)
        if (place[0]==iplace[0] and place[1]==iplace[1]):
            print "plus de place"
            return None

def countfinalvotes(votes,k):
    counter=0
    for i in votes:
        for vote in i:
            if (len(vote)==0):
                continue
                indice=vote.index(max(vote))
                if (photovote[indice]<k):
                    continue
                else:
                    counter+=1
    return counter

def voteneeded(votes,k):
    for i in votes:
        for vote in i:
            if (len(vote)==0):
                continue
                indice=vote.index(max(vote))
                if (photovote[indice]<k):
                    continue
                else:
                    counter+=1
    return counter


def generateGroundTruth(lat,long,scale):
    groundtruth= [[[] for col in range(long+1)] for row in range(lat+1)]
    for i in range (0,lat+1):
        for j in range(0,long+1):
            groundtruth[i][j]=gettruth(scale);
            #print groundtruth[i][j]
    return groundtruth

def photocoverage(photos):
    count=0
    for row in photos:
        for v in row:
            if v>=0:
                count+=1
    return count

def averagequality(photos):
    count=0
    quality=0
    for row in photos:
        for v in row:
            if v>=0:
                count+=1
                quality+=v
    return quality/count

if __name__ == "__main__":
    print distance_on_unit_sphere( 48.817, 2.248, 48.904, 2.428,6373)
    print distance_on_unit_sphere( 48.817, 2.248, 48.817, 2.248,6373)
    print distance_on_unit_sphere( 48.817, 2.248, 48.904, 2.248,6373)
    print distance_on_unit_sphere( 48.817, 2.2480000000000002, 48.817, 2.4279999999999999,6373)
    print distance_on_unit_sphere( 48.817, 2.2480000000000002, 48.904000000000003, 2.4279999999999999,6373)
    print distance_on_unit_sphere( 48.817, 2.2480000000000002, 48.904000000000003, 2.4279999999999999,6373)


