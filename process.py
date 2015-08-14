#!/usr/bin/python

import MySQLdb
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import numpy as np
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
import itertools

def classify(row):
    pitch_types = {}
    pitch_types['FA'] = "fastball"
    pitch_types['FF'] = "four-seam fastball"
    pitch_types['FT'] = "two-seam fastball"
    pitch_types['FC'] = "cutter"
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
    pitch_types['FT'] = "two-seam fastball"
    pitch_types['AB'] = "unknown"
    pitch_types['PO'] = "Pitch Out"
    pitch_types['FO'] = "Pitch out"
    results = {}

    results['In play, no out'] = "Hit"
    results['In play, run(s)'] = "Hit"
    results['In play, out(s)'] = "Out"
    results['Foul'] = "Foul"
    results['Ball'] = "Ball"
    results['Strike'] = "Srike"
    results['Called Strike'] = "Strike"
    results['Swinging Strike (Blocked)'] = "Strike"
    results['Ball In Dirt'] = "ignore"
    results['Swinging Strike'] = "Strike"
    results['Foul Tip'] = "Foul"
    results['Foul (Runner Going)'] = "Foul"
    results['Hit By Pitch'] = "Hit by pitch"
    results['Foul Bunt'] = "Foul Bunt"
    results['Missed Bunt'] = "Missed Bunt"
    results["Bunt"] = "Bunt"
    results["Pitchout"] = "Pitch Out"

    row = list(row)
    row[2] = results[row[2]]
    row[3] = pitch_types[row[3]]
    print row

    return row    

name = raw_input("Enter name: ")

connection = MySQLdb.connect(host = "127.0.0.1", user="root", passwd="", db = "stats")

query = "select * from information4 where name=\""+name+"\";"

c = connection.cursor()

c.execute(query)
values = []
for row in c:
    values.append(classify(row))

hxvalues = []
hyvalues = []
sxvalues = []
syvalues = []
bxvalues = []
byvalues = []
oxvalues = []
oyvalues = []
hits = []
balls = []
strikes = []
outs = []
for value in values:
    if value[2] == "Hit":
        hxvalues.append(value[4])
        hyvalues.append(value[5])
        hits.append([value[4],value[5]])
    elif value[2] == "Ball" and value[4] >= 20 and value[5] >= 20:
        bxvalues.append(value[4])
        byvalues.append(value[5])
        balls.append([value[4],value[5]])
    elif value[2] == "Strike":
        sxvalues.append(value[4])
        syvalues.append(value[5])
        strikes.append([value[4],value[5]])
    elif value[2] == "Out":
        oxvalues.append(value[4])
        oyvalues.append(value[5])
        outs.append([value[4],value[5]])

print hxvalues
#plt.plot(hxvalues,hyvalues,'go')
#plt.plot(bxvalues,byvalues,'bo')
#plt.plot(sxvalues,syvalues,'ro')
#plt.plot(oxvalues, oyvalues, 'bo')

hitsX = np.array(hits)
strikesX = np.array(strikes)
outsX = np.array(outs)

db = DBSCAN(eps = 5, min_samples = 5).fit(hitsX)

core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

print('Estimated number of clusters: %d' % n_clusters_)
#plt.show()

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = 'k'

    class_member_mask = (labels == k)

    xy = hitsX[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=14)

    xy = hitsX[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

def class_round(value, base=5):
    return int(base * round(float(value)/base))

def associate(values, passval, failval):

    high = {}
    low = {}

    count = 0
    for value in values:
        if count != 0:
            if value[2] == passval:
                high[count] = [value[2],value[3],class_round(value[4]),class_round(value[5]),class_round(value[6]),class_round(value[7])]
            elif value[3] == failval:
                low[count] = [value[2],value[3],class_round(value[4]),class_round(value[5]),class_round(value[6]),class_round(value[7])]
        count = count + 1

    high_ignore = []
    low_ignore = []
    support = {}
    confidence = {}

    r = 3
    l = 3
    while True:
        high_rule = {}
        low_rule = {}
        support = {}
        confidence = {}
    
        for key, value in high.items():
            for f in itertools.permutations(value, r):
                f = sorted(f)
                f = tuple(f)
                if high_rule.get(f):
                    if (f, key) not in high_ignore:
                        high_rule[f] = high_rule[f] + 1
                        high_ignore.append((f, key))

                else:
                    high_ignore.append((f, key))
                    high_rule[f] = 1
                
        for key, value in low.items():
            for f in itertools.permutations(value, r):
                f = sorted(f)
                f = tuple(f)
                if low_rule.get(f):
                    if (f, key) not in low_ignore:
                        low_rule[f] = low_rule[f] + 1
                        low_ignore.append((f, key))
                else:
                    low_ignore.append((f, key))
                    low_rule[f] = 1

        for key, value in high_rule.items():
            items = list(key)
            if high_rule[key] == 1:
                for item in items:
                    for ident in high.keys():
                        try:
                            high[ident].remove(item)
                        except ValueError:
                            pass
                del high_rule[key]
            else:
                supp = 0
                for ident, value in low.items():
                    if set(value).intersection(set(items)):
                        supp = supp + 1
                        
                if supp > 0:
                    confidence[key] = float(high_rule[key]) / float(supp)
                else:
                    confidence[key] = 1
                support[key] = float(high_rule[key]) / float(len(high) + len(low))
    
        r = r+1
        if r > l:
            break
        
    for key in confidence.keys():
        if confidence[key] > .6 and support[key] > .2:
            print str(key)+" Instances: "+str(high_rule[key])+" : Confidence: "+str(confidence[key])+" support: "+str(support[key])
    
associate(values, "Hit", "Strike")
