#!/usr/bin/python

import MySQLdb
import urllib2
import StringIO
import xml.etree.ElementTree as ET
import pickle
import hashlib
import time

attempts = 0
stats = []

pitch_types = {}

pitch_types['FA'] = "fastball"
pitch_types['FF'] = "four-seam fastball"
pitch_types['FT'] = "two-seam fastball"
pitch_types['FC'] = "fastball (cutter)"
pitch_types['FS / SI / SF'] = "fastball (sinker, split-fingered)"
pitch_types['SL'] = "slider"
pitch_types['CH'] = "changeup"
pitch_types['CU'] = "curveball"
pitch_types['CB'] = "curveball"
pitch_types['KC'] = "knuckle-curve"
pitch_types['KN'] = "knuckleball"
pitch_types['EP'] = "eephus"
pitch_types['S'] = "Slider"
pitch_types['FS'] = "Sinker"
pitch_types['SF'] = "Split-fingered"
pitch_types['SI'] = "Sinker"
results = {}

results['In play, no out'] = "Hit"
results['In play, run(s)'] = "RBI"
results['In play, out(s)'] = "Out"
results['Foul'] = "Foul"
results['Ball'] = "Ball"
results['Strike'] = "Swinging Srike"
results['Called Strike'] = "Called Strike"
results['Swinging Strike (Blocked)'] = "Swinging Strike"
results['Ball In Dirt'] = "Ball in Dirt"
results['Swinging Strike'] = "Swinging Strike"
results['Foul Tip'] = "Foul Tip"
results['Foul (Runner Going)'] = "Foul, runner going"
results['Hit By Pitch'] = "Hit by pitch"
results['Foul Bunt'] = "Foul Bunt"
results['Missed Bunt'] = "Missed Bunt"
results["Bunt"] = "Bunt"

hits = ["Single", "Double", "Triple", "Home Run"]

def get_games():
    response = urllib2.urlopen("http://gd2.mlb.com/components/game/mlb/year_2015/")
    content = response.read()
    months = []
    games = []
    x = content.split("<a href=")
    for f in x:
        y = f.split('"> ')
        if "month" in y[0] and ("3" not in y[0]):
            months.append(y[0].replace('"',"").replace("'",""))
    for month in months:
        days = []
        response = urllib2.urlopen("http://gd2.mlb.com/components/game/mlb/year_2015/"+month)
        content = response.read()
        x = content.split("<a href=")
        for t in x:
            y = t.split('"> ')
            if "day" in y[0]:
                days.append(y[0].replace('"',"").replace("'",""))
        for day in days:
             path = "http://gd2.mlb.com/components/game/mlb/year_2015/"+month+day
             response = response = urllib2.urlopen(path)
             content = response.read()
             x = content.split("<a href=")
             for t in x:
                 y = t.split('"> ')
                 if "gid_2015" in y[0] and "aaa" not in y[0]:
                     games.append(path + y[0].replace('"',"").replace("'",""))

    with open("paths.txt", 'wb') as f:
        pickle.dump(games, f)

    return games

#with open("paths.txt", 'r') as f:
   #games = [line.rstrip('\n') for line in f]

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

information = {}

games = get_games()
filename_append = 0

for f in games:
    print f
    input = ""
    stats = []
    attempts = 0
    while attempts < 3:
        try:
            response = urllib2.urlopen(f+"/inning/inning_all.xml", timeout = 5)
            content = response.read()
            break
        except urllib2.URLError as e:
            attempts += 1
            time.sleep(1)
            print "Error connecting"
   

    root = ET.parse(StringIO.StringIO(content)).getroot()
    for child in root.findall("./inning/top/atbat"):
        stats.append([child.tag, child.attrib, child])
    for child in root.findall("./inning/bottom/atbat"):
        stats.append([child.tag, child.attrib, child])
    filename = "./sql/output"+str(filename_append)+".sql"
    for stat in stats:
        pitches = []
        for pitch in stat[2].findall("./pitch"):
            pitches.append(pitch.attrib)
        splited = stat[1]['des'].split()
        if splited[1].endswith("."):
            name = splited[0]+splited[1]+" "+splited[2]
        else:
            name = splited[0]+" "+splited[1]
        
        key = hashlib.md5(name.encode())
        Key = key.hexdigest()

        for pitch in pitches:
            pitch_type = pitch.get('pitch_type', "Unknown")
            des = pitch.get('des', "Unknown")
            x = pitch.get('x', "Unknown")
            y = pitch.get('y', "Unknown")
            start_speed = pitch.get('start_speed', "Unknown")
            end_speed = pitch.get('end_speed', "Unknown")
            if start_speed != "Unknown" or pitch_type != "Unknown":
                print pitch
                input = "INSERT INTO information4 VALUES (\""
                input = input + Key +"\",\""
                input = input + name + "\",\""
                input = input + des + "\",\""
                input = input + pitch_type + "\",\""
                input = input + x +"\",\""
                input = input + y +"\",\""
                input = input + start_speed +"\",\""
                input = input + end_speed +"\");\n"
                print input
                try:
                    with open(filename, "a") as myfile:
                        myfile.write(input)
                except IOError:
                    with open(filename, "w+") as myfile:
                        myfile.write(input)
                myfile.close()
        
        try:
            if file_len(filename) >= 1000:
                filename_append = int(filename_append)+1
        except:
            continue
