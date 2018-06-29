# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 16:11:39 2018

@author: Jana
"""
import pylast
import operator


from credentials import lastfmKey, lastfmSecret

network = pylast.LastFMNetwork(api_key=lastfmKey, api_secret=lastfmSecret,
                               username='defektseit94')

me = pylast.User('defektseit94', network)

topTracks = me.get_top_tracks(limit = 1000)

tagsDict = {}
allTags = []

for track in topTracks:
    tags = track[0].get_top_tags()
    allTags += [str(t.item) for t in tags]
#         if tag in tagsDict:
#            tagsDict[tag] += 1
#        else:
#            tagsDict[tag] = 1
            
sorted_dict = sorted(tagsDict.items(), key=operator.itemgetter(1), reverse=True)
