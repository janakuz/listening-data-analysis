# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 22:30:49 2018

@author: Jana
"""
import pylast
import ArtistsSimilarityPercentage
from credentials import lastfmKey, lastfmSecret

network = pylast.LastFMNetwork(api_key=lastfmKey, api_secret=lastfmSecret,
                               username='defektseit94')

me = pylast.User('defektseit94', network)

myTopArtists = [str(artist.item) for artist in me.get_top_artists(limit=10)]

maxSim = 0
mostSimilar = ""
minSim = 1
leastSimilar = ""
allSim = [0 for i in range(10)]


for artist1 in range(10):
    for artist2 in range(artist1 + 1, 10):
        allSim[artist1] += ArtistsSimilarityPercentage.calculateSimilarity(
                myTopArtists[artist1], myTopArtists[artist2])
        allSim[artist2] += ArtistsSimilarityPercentage.calculateSimilarity(
                myTopArtists[artist1], myTopArtists[artist2])


avgs = [total/10 for total in allSim]

maxI = max(avgs)

myTopArtists[avgs.index(maxI)]