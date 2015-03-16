__author__ = 'Brian Jones'
from shapely import geometry
import numpy as np
import random
from datetime import datetime, timedelta
import csv
import codecs

def detectionMaker(animals=(1,1), ping_rate=30, seed=random.randint(0,10000), animal_speed=(1,1),
                   animal_treks=(10,10), animal_lat = (0,10), animal_long=(0,10),
                   receiver_p1 = (0, 0), receiver_p2 = (10, 10),
                   receiver_range=0.1, receiver_split = 10, start_date= None,
                   csvfile=None):

    #Randomness
    random.seed(seed)

    #Animals
    animal_speed = animal_speed
    animal_treks = animal_treks
    animals = animals
    animal_lat = animal_lat
    animal_long = animal_long
    ping_rate = ping_rate
    if start_date:
        start_date = datetime(*start_date)
    else:
        start_date = datetime.now()

    #Receivers
    receiver_p1 = receiver_p1
    receiver_p2 = receiver_p2
    receiver_split = receiver_split
    receiver_range = receiver_range

    csvfile = csvfile

    #Animal Path
    paths = []
    for anml in range(random.randint(*animals)):
        paths.append( {'path':geometry.LineString([(random.uniform(*animal_long),
                                                   random.uniform(*animal_lat))
                                                  for x in range(random.randint(*animal_treks))]),
                      'name':'A%s' % anml})

    #Split into Lines
    lines = []
    for path in paths:
        for x,y in zip(path['path'].coords[:-1],path['path'].coords[1:]):
            lines.append({'line':geometry.LineString((x, y)),
                          'name':path['name']})

    # Split lines into treks
    trek = []
    date_elapse = start_date
    adname = lines[0]['name']
    #For each line create bounds
    for num, line in enumerate(lines):
        aname = line['name']
        if aname != adname:
            adname = aname
            date_elapse = start_date
        dt = date_elapse
        llen = line['line'].length
        tname = 'T%s' % num
        speed = random.uniform(*animal_speed)
        if speed == 0: speed = 0.01
        #Calculate time for line segment
        date_elapse = dt + timedelta(hours=llen/speed)
        trek.append({'name': tname,
                     'animal':aname,
                     'speed': speed,
                     'starttime': dt,
                     'endtime': date_elapse,
                     'line':line['line']})

    #Receiver Line
    l = geometry.LineString((receiver_p1, receiver_p2))
    points = []
    for x in np.arange(0, l.length, l.length/receiver_split):
        points.append(l.interpolate(x))
    points.append(l.interpolate(l.length))
    #Name the points
    names = ['P%s'%x for x,y in enumerate(points)]
    npoints = zip(names,points)

    #Define detections
    detections = []
    uid = 0
    for name, point in npoints:
        for line in trek:
            #print name, line['name']
            intersect = line['line'].intersection(point.buffer(receiver_range))
            if not intersect.is_empty:
                #Intersection boundary
                bpoints = intersect.boundary
                #Start of trek line
                start = line['line'].boundary[0]
                #distance between start and first intersec point
                distance = start.distance(bpoints[0])
                starttime = line['starttime'] + timedelta(hours=distance/line['speed'])
                endtime = starttime + timedelta(hours=intersect.length/line['speed'])
                t =  starttime
                while t < endtime:
                    detections.append({'uid':uid,
                                       'time':t,
                                       'position':point,
                                       'station':name,
                                       'animal':line['animal']})
                    t = t + timedelta(seconds=ping_rate)
                    uid += 1

    if csvfile:
        with codecs.open(csvfile,'wb','utf-8') as csvfileh:
            spamwriter = csv.writer(csvfileh, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow(['station','unqdetecid','datecollected',
                                 'catalognumber','longitude','latitude'])
            for line in detections:
                spamwriter.writerow([line['station'], line['uid'],
                                     line['time'].strftime("%Y-%m-%d %H:%M:%S"),  line['animal'],
                                     round(line['position'].coords[0][1],5),round(line['position'].coords[0][0],5)])
    else:
        return detections, seed

if __name__ == '__main__':
    detectionMaker(receiver_split=10,
                    seed=5,
                    animals=(0,10),
                    animal_speed=(0.1,0.2),
                    csvfile='example.csv')
