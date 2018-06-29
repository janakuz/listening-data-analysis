# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 18:41:13 2018

@author: Jana
"""

import credentials
import pylast
import math

network = pylast.LastFMNetwork(api_key=credentials. lastfmKey, 
                               api_secret=credentials. lastfmSecret,
                               username='defektseit94')

me = pylast.User('defektseit94', network)

#    artist1 = network.get_artist(raw_input("Enter first artist: "))
#    artist2 = network.get_artist(raw_input("Enter second artist: "))


def makeTagList(artist, tagArray):
    try:
        for tag in artist.get_top_tags():
            tagArray += [str(tag.item)]
    except pylast.WSError:
        raise
        
def makeArtistList(artist, artistArray, limit):
    try:
        for artist in artist.get_similar(limit=limit):
            artistArray += [str(artist.item)]
    except pylast.WSError:
        raise

#similarity based on tags the two artists have in common
def calculateTagSimilarity(a1, a2):     
    artist1 = network.get_artist(a1)
    artist2 = network.get_artist(a2)

    artist1Tags = []
    artist2Tags =  []
    
    try:
        makeTagList(artist1, artist1Tags)
    except pylast.WSError:
        print "Artist 1 could not be found"
        return
    try:
        makeTagList(artist2, artist2Tags)
    except pylast.WSError:
        print "Artist 2 could not be found"
        return

    numberTagsA1 = len(artist1Tags)
    numberTagsA2 = len(artist2Tags)

    a1t = {}
    a2t = {}
    
    for tag in artist1Tags:
        a1t[tag] = numberTagsA1-artist1Tags.index(tag)
    for tag in artist2Tags:
        a2t[tag] = numberTagsA2-artist2Tags.index(tag)

    terms = set(a1t).union(a2t)
    dotprod = sum(a1t.get(k, 0) * a2t.get(k, 0) for k in terms)
    magA = math.sqrt(sum(a1t.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(a2t.get(k, 0)**2 for k in terms))
    cosSim = dotprod / (magA * magB)

#
#    commonTags = 0
#    commonTagsWeighted = 0
#    totalTags = len(artist1Tags) + len(artist2Tags)
#    tagsAvg = (numberTagsA1 + numberTagsA2)/2.0
#    totalTagsWeighted = tagsAvg*(tagsAvg+1)/2.0
#
#    for tag in artist1Tags:
#        if tag in artist2Tags:
#            commonTags += 1
#            commonTagsWeighted += (numberTagsA1-artist1Tags.index(tag) + \
#                                   numberTagsA2-artist2Tags.index(tag))/2.0
#        
#    #we divide byt the average number of tags per artist        
#    tagSimilarity = commonTags*2/float(totalTags)
#    tagSimilarityWeighted = commonTagsWeighted/totalTagsWeighted
    
    return cosSim

#similarity based on similar artists the two artists have in common
def calculateSASimilarity(a1, a2):
    artist1 = network.get_artist(a1)
    artist2 = network.get_artist(a2)

    artist1SimilarArtists = []
    artist2SimilarArtists =  []

    try:
        makeArtistList(artist1, artist1SimilarArtists, 20)
    except pylast.WSError:
        print "Artist 1 could not be found"
        return
    try:
        makeArtistList(artist2, artist2SimilarArtists, 20)
    except pylast.WSError:
        print "Artist 2 could not be found"
        return
        
    
    a1t = {a1: 20}
    a2t = {a2: 20}
    
    for tag in artist1SimilarArtists:
        a1t[tag] = 20-artist1SimilarArtists.index(tag)
    for tag in artist2SimilarArtists:
        a2t[tag] = 20-artist2SimilarArtists.index(tag)

    terms = set(a1t).union(a2t)
    dotprod = sum(a1t.get(k, 0) * a2t.get(k, 0) for k in terms)
    magA = math.sqrt(sum(a1t.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(a2t.get(k, 0)**2 for k in terms))
    cosSim = dotprod / (magA * magB)
    
#    commonArtists = 0
#    commonArtistsWeighted = 0
#    
#    for artist in artist1SimilarArtists:
#        if artist in artist2SimilarArtists:
#            commonArtists += 1
#            commonArtistsWeighted += (20-artist1SimilarArtists.index(artist) + \
#                                      20-artist2SimilarArtists.index(artist))/2.0
#    if a1 in artist2SimilarArtists:
#        commonArtists += 1
#        commonArtistsWeighted += (20+20-artist2SimilarArtists.index(a1))/2.0
#    if a2 in artist2SimilarArtists:
#        commonArtists += 1
#        commonArtistsWeighted += (20+20-artist2SimilarArtists.index(a1))/2.0
#           
#    artistSimilarity = commonArtists/20.0
#    artistSimilarityWeighted = commonArtistsWeighted/210.0
    
    return cosSim
    
def calculateSimilarity(a1, a2):
    return calculateTagSimilarity(a1, a2)*0.5 + calculateSASimilarity(a1, a2)*0.5