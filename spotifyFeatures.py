# -*- coding: utf-8 -*-
"""
Created on Mon Mar 05 10:38:58 2018

@author: Jana
"""

import spotipy
import spotipy.util as util

from credentials import spotifyClientID, spotifySecret, spotifyUsername

scopes = "playlist-read-private user-library-read user-top-read user-read-recently-played"
token = util.prompt_for_user_token(spotifyUsername, scopes,
                                   client_id=spotifyClientID,
                                   client_secret=spotifySecret,
                                   redirect_uri='http://localhost/')

spotify = spotipy.Spotify(auth=token)

def getPlaylistTracks(username,playlistID):
    res = spotify.user_playlist_tracks(username,playlistID)
    tracks = res['items']
    while res['next']:
        res = spotify.next(res)
        tracks.extend(res['items'])
    return tracks

def eliminateLocalTracks(tracks):
    new_tracks = tracks[:]
    for track in tracks:
        if track['is_local']:
            new_tracks.remove(track)
    return new_tracks

def getArtist(name):
    res = spotify.search(q='artist:' + name, type='artist')
    artists = res['artists']['items']
    if len(artists) == 1:
        return artists[0]
    elif len(artists) > 1:
        correctArtist = chooseCorrectArtist(artists)
        if correctArtist > 0:
            return artists[correctArtist-1]
        else:
            while res['artists']['next']:
                res = spotify.next(res['artists'])
                artists = res['artists']['items']
                correctArtist = chooseCorrectArtist(artists)
                if correctArtist > 0:
                    return artists[correctArtist-1]
    else:
        raise Exception("Artist not found")
        
def getAlbum(name):
    res = spotify.search(q='album:' + name, type='album')
    albums = res['albums']['items']
    if len(albums) == 1:
        return albums[0]
    elif len(albums) > 1:
        correctAlbum = chooseCorrectAlbum(albums)
        if correctAlbum > 0:
            return albums[correctAlbum-1]
        else:
            while res['albums']['next']:
                res = spotify.next(res['albums'])
                albums = res['albums']['items']
                correctAlbum = chooseCorrectAlbum(albums)
                if correctAlbum > 0:
                    return albums[correctAlbum-1]
    else:
        raise Exception("Album not found")        
        
def chooseCorrectArtist(artists):
    i = 1
    for artist in artists:
        print str(i) + ". " + artist['name']
        i += 1
    correctArtist = raw_input("Enter the number of the correct artist, 0 if none: ")
    correctArtist = int(correctArtist)
    return correctArtist

def chooseCorrectAlbum(albums):
    i = 1
    for album in albums:
        print str(i) + ". " + album['name'] + " by " + album['artists'][0]['name'] \
        + "; type: " + album['album_type']
        i += 1
    correctAlbum = raw_input("Enter the number of the correct album, 0 if none: ")
    correctAlbum = int(correctAlbum)
    return correctAlbum    
        
def getArtistAlbums(artist):
    albums = []
    res = spotify.artist_albums(artist['id'], album_type='album')
    albums.extend(res['items'])
    while res['next']:
        res = spotify.next(res)
        albums.extend(res['items'])
    return albums

def getAlbumTracks(album):
    tracks = spotify.album_tracks(album['id'])
    return tracks['items']
    
def getArtistTracks(artist):
    albums = getArtistAlbums(artist)
    tracks = []
    for album in albums:
        tracks.extend(getAlbumTracks(album))
    return tracks
    
def printAlbumTracks(album):
    tracks = getAlbumTracks(album)
    for track in tracks:
        print str(track['track_number']) + ". " + track['name']
        
def printArtistAlbums(artist):
    albums = getArtistAlbums(artist)
    for album in albums:
        print album['name']
    
def getTrackIDs(tracklist, isPlaylist):
    tracks = []
    for track in tracklist:
        if isPlaylist:
            tracks += [track['track']['uri']]
        else:
            tracks += [track['uri']]
        
    return tracks

def getFullTrackInfo(track_uri):
    return spotify.track(track_uri)

def avgFeatures_list(featuresList):
    numsongs = len(featuresList)
    avgFeatures = {'acousticness': 0, 'danceability': 0, 'energy': 0, 'liveness': 0,
               'speechiness': 0, 'tempo': 0, 'valence': 0}
    for key in avgFeatures:
        for i in range(numsongs):
            avgFeatures[key] += featuresList[i][key]
        avgFeatures[key] = avgFeatures[key]/float(numsongs)
        
    return avgFeatures

def avgPopularity(tracks):
    popularity = 0
    numsongs = len(tracks)
    for i in range(numsongs):
        track = getFullTrackInfo(tracks[i])
        popularity += track['popularity']
    popularity /= float(numsongs)
    
    return popularity

def getFeaturesTracks(tracklist):
    numsongs = len(tracklist)
    allFeatures = []
    
    if numsongs < 100:
        allFeatures = spotify.audio_features(tracklist)
    else:
        allFeatures = spotify.audio_features(tracklist[:100])
        numsongs -= 100
        i = 1
        while numsongs > 100:
            start = 100*i
            end = 100*(i+1)
            allFeatures += spotify.audio_features(tracklist[start:end])
            i += 1
            numsongs -= 100
        allFeatures += spotify.audio_features(tracklist[100*i:])
        
    return allFeatures
    
def avgFeatures(tracklist):
    numsongs = len(tracklist)
    avgFeatures = {'acousticness': 0, 'danceability': 0, 'energy': 0, 'liveness': 0,
               'speechiness': 0, 'tempo': 0, 'valence': 0}
    
    allFeatures = getFeaturesTracks(tracklist)

    for key in avgFeatures:
        for i in range(numsongs):
            avgFeatures[key] += allFeatures[i][key]
        avgFeatures[key] = avgFeatures[key]/float(numsongs)
        
    return avgFeatures        

#def avgFeatures_playlist(tracks):
#    noLocalTracks = eliminateLocalTracks(tracks)
#    avgFeaturesList = avgFeatures(getTrackIDs(noLocalTracks, True))    
#    return avgFeaturesList

         
def findPlaylistID(name):
    playlists = spotify.current_user_playlists()
    
    for playlist in playlists['items']:
        if playlist['name'] == name:
            return playlist['id']
    raise Exception("Playlist not found")    
        
        
def playlistFeatures(playlistName):
    try:
        playlist = findPlaylistID(playlistName)
        playlistTracks = getPlaylistTracks(spotifyUsername, playlist)
        noLocalTracks = eliminateLocalTracks(playlistTracks)
        trackIDs = getTrackIDs(noLocalTracks, True)
        return avgFeatures(trackIDs)
    except Exception:
        raise
        
def artistFeatures(artistName):
    try:
        artist = getArtist(artistName)
        tracks = getArtistTracks(artist)
        trackIDs = getTrackIDs(tracks, False)
        return avgFeatures(trackIDs)
    except Exception:
        raise


def tracksByArtist(playlistName):
    artists = {}
    
    allPlaylist = getPlaylistTracks(spotifyUsername, findPlaylistID(playlistName))

    for i in range(len(allPlaylist)):
        if not allPlaylist[i]['is_local']:
            artist = allPlaylist[i]['track']['artists'][0]['name']
            if artist in artists:
                artists[artist] += ["spotify:track:" + allPlaylist[i]['track']['id']]
            else:
                artists[artist] = ["spotify:track:" + allPlaylist[i]['track']['id']]
            
    return artists


def featuresByArtist(artists):
    artistFeatures = {}

    for artist in artists:
        if len(artists[artist]) < 100:
            artistFeatures[artist] = spotify.audio_features(artists[artist])
        else:
            tracks = len(artists[artist])
            artistFeatures[artist] = spotify.audio_features(artists[artist][:100])
            tracks -= 100
            i = 1
            while tracks > 100:
                artistFeatures[artist] += spotify.audio_features(artists[artist][100*i:100*(i+1)])
                i += 1
                tracks -= 100
            artistFeatures[artist] += spotify.audio_features(artists[artist][100*i:])
            
    return artistFeatures
        
def avgFeaturesByArtist(artists):
    artistFeatures = featuresByArtist(artists)        
    avgArtistFeatures = {}

    for artist in artistFeatures:
        avgArtistFeatures[artist] = avgFeatures_list(artistFeatures[artist])
        
    return avgArtistFeatures
    

def extremeFeatures(playlistName):
    artists = tracksByArtist(playlistName)
    avgArtistFeatures = avgFeaturesByArtist(artists)
    
    extremeFeatures = {'max_acousticness': (0, ""), 'max_danceability': (0, ""), 
                   'max_energy': (0, ""), 'max_liveness': (0, ""), 
                   'max_speechiness': (0, ""), 'max_tempo': (0, ""), 
                   'max_valence': (0, ""), 'min_acousticness': (1, ""), 
                   'min_danceability': (1, ""), 'min_energy': (1, ""), 
                   'min_liveness': (1, ""), 'min_speechiness': (1, ""), 
                   'min_tempo': (500, ""), 'min_valence': (1, "")}    
    
    for artist in avgArtistFeatures:
        for feature in extremeFeatures:
            if feature[:3] == "max" and \
            avgArtistFeatures[artist][feature[4:]] > extremeFeatures[feature][0]:
                extremeFeatures[feature] = (avgArtistFeatures[artist][feature[4:]], artist)
            elif feature[:3] == "min" and \
            avgArtistFeatures[artist][feature[4:]] < extremeFeatures[feature][0]:
                extremeFeatures[feature] = (avgArtistFeatures[artist][feature[4:]], artist)
                
    return extremeFeatures


def listAllPlaylists(username):
    playlists = spotify.user_playlists(username)
    i = 1
    for playlist in playlists['items']:
        print str(i) + ". " + playlist['name']
        i += 1


def extremeFeaturesSongs(tracklist):
    extremeFeatures = {'max_acousticness': (0, ""), 'max_danceability': (0, ""), 
                   'max_energy': (0, ""), 'max_liveness': (0, ""), 
                   'max_speechiness': (0, ""), 'max_tempo': (0, ""), 
                   'max_valence': (0, ""), 'min_acousticness': (1, ""), 
                   'min_danceability': (1, ""), 'min_energy': (1, ""), 
                   'min_liveness': (1, ""), 'min_speechiness': (1, ""), 
                   'min_tempo': (500, ""), 'min_valence': (1, "")}  

    features = getFeaturesTracks(tracklist)
    
    for feature in extremeFeatures:
        for i in range(len(features)):
            if feature[:3] == "max" and \
            features[i][feature[4:]] > extremeFeatures[feature][0]:
                extVal = features[i][feature[4:]]
                name = (getFullTrackInfo(tracklist[i]))['name']
                extremeFeatures[feature] = (extVal, name)
            if feature[:3] == "min" and \
            features[i][feature[4:]] < extremeFeatures[feature][0]:
                extVal = features[i][feature[4:]]
                name = (getFullTrackInfo(tracklist[i]))['name']
                extremeFeatures[feature] = (extVal, name)
                
    return extremeFeatures
        

def extremeFeaturesByTrackPlaylist(playlistName):
    playlist = findPlaylistID(playlistName)
    tracks = getPlaylistTracks(spotifyUsername, playlist)
    tracks = eliminateLocalTracks(tracks)
    tracklist = getTrackIDs(tracks, True)    

    return extremeFeaturesSongs(tracklist)

def extremeFeaturesByTrackArtist(artistName):
    artist = getArtist(artistName)
    tracks = getArtistTracks(artist)
    tracklist = getTrackIDs(tracks, False)
    
    return extremeFeaturesSongs(tracklist)

def extremeFeaturesByTrackAlbum(albumName):
    album = getAlbum(albumName)
    tracks = getAlbumTracks(album)
    tracklist = getTrackIDs(tracks, False)
    
    return extremeFeaturesSongs(tracklist)