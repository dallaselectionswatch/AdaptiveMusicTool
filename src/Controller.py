"""
Author: Isaiah Mercado
Purpose: Driver file
Desired Outcome: Connects to user's spotify account and updates playlist based on user prefs

playlists must be made collaborative and visible on the profile of the user
"""
import spotipy
from datetime import timedelta
from Models.Preferences import Preferences
from Models.Account import Account
from spotipy.oauth2 import SpotifyOAuth
import datetime

SPOTIPY_CLIENT_ID='fe921ddf76d440e48f8766f8d040e71d'
SPOTIPY_CLIENT_SECRET='464ab682558e4d3ea49be40d4efc2294'


"""
isDuplicate
Goal: Check for duplicates of songs within a playlist
song: title of track (String)
playlist: list of track titles (List of Strings)

returns true if song is a duplicate, false if not found in playlist
"""
def isDuplicate(song, playlist):
    if(song in playlist):
        return True
    return False

"""
pickPlaylistToUpdate
Goal: Make user decide which singular playlist they want to update

Reason: Temporary functionality for testing
Notes: Will update this function to communicate with the front-end

:userPlaylists - list of all the current user's playlists
Returns : Playlist object
"""
def pickPlaylistToUpdate(userPlaylists):
    print("Please choose a playlist by entering the number next to it.")
    playlistIndex = 0
    for playlist in userPlaylists:
        print(str(playlistIndex) + " : " + playlist["name"])
        playlistIndex+=1

    indexOfPlaylist = input('Your Selection: ')
    return userPlaylists[int(indexOfPlaylist)]

"""
timeToUpdate

goal: check if enough time has passed since last update to merit an update
parameters:
    - user (object)
    
:returns
    - true if we should update
    - false if we should not update
"""

def timeToUpdate():
    now = datetime.datetime.now()
    minimumUpdateDate = user.lastUpdate + timedelta(days=prefs.refreshPeriod)
    if (now < minimumUpdateDate):
        return True
    return False

def pointShuffleArtist(seed):
    contributingArtists = seed["track"]["artists"]
    chosenArtist = contributingArtists[0]
    topTracksByArtist = sp.artist_top_tracks(chosenArtist["id"], country='US')["tracks"]
    sortedByPopularity = sorted(topTracksByArtist, key=lambda x: x["popularity"], reverse=True)
    return sortedByPopularity

def pointShuffleAlbum(albumTracks):
    trackIDs = [x['id'] for x in albumTracks["items"]]
    fullTracks = sp.tracks(trackIDs)['tracks']
    sortedByPopularity = sorted(fullTracks, key=lambda x: x['popularity'], reverse=True)
    return sortedByPopularity

def isDuplicateInEitherPlaylist(track, trackNamesInPlaylist, trackNamesInNewPlaylist):
    if (isDuplicate(track["name"], trackNamesInPlaylist) or isDuplicate(track["name"], trackNamesInNewPlaylist)):
        return True
    return False



"""
pickNewSong

:returns a spotify track

parameters
- seed: track from original playlist
- pointOfCommonality: artist, album, etc

Notes:
When the album is a single, we default to point shuffle around artist
"""
def pickNewSong(seed, playlistTracks, updatedTracks, pointOfCommonality):
    albumID = seed['track']["album"]["id"]
    albumTracks = sp.album_tracks(albumID)


    trackNamesInNewPlaylist = []
    for track in updatedPlaylistTracks:
        trackNamesInNewPlaylist.append(track["track"]["name"])

    trackNamesInPlaylist = []
    for track in playlistTracks:
        trackNamesInPlaylist.append(track["track"]["name"])

    if(pointOfCommonality == "ALBUM" and len(albumTracks["items"]) > 1):
        sortedByPopularity = pointShuffleAlbum(albumTracks)
    else:
        sortedByPopularity = pointShuffleArtist(seed)

    for track in sortedByPopularity:
        if (not isDuplicateInEitherPlaylist(track, trackNamesInPlaylist, trackNamesInNewPlaylist)):
            print("new: " + track["name"])
            return track
    # Default track to return - may be a duplicate
    if len(sortedByPopularity) == 0:
        return "nope"
    return sortedByPopularity[0]

scope = "playlist-modify-private"

# initialize a spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,redirect_uri='https://localhost:8888/callback'))
userID = sp.me()['id']

# Preferences(refresh period in days, update style, save or update)
pointShuffleTypeSelection = input("Perform point shuffle around:\n1 ARTIST\n2 Album\n")
if (pointShuffleTypeSelection == 1):
    pointShuffleType = "ARTIST"
else:
    pointShuffleType = "ALBUM"

prefs = Preferences("ARTIST", "SAVE")
userPlaylists = sp.current_user_playlists(limit=50, offset=0)["items"]

# preferences, playlists, lastUpdate, userID
user = Account(prefs, userPlaylists, userID)

# iterate through the playlists
playlist = pickPlaylistToUpdate(userPlaylists)
# compare lastUpdated for each playlist to the refreshPeriod and the current datetime


# name of new/temp playlist -- in the future we should use a version or date naming convention (ex: name_v1, name_sept10)
existingName = playlist["name"]
updatedName = existingName + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
updatedDescription = "newest version of " + existingName
print("adding songs to playlist: " + updatedName)
updatedPlaylist = sp.user_playlist_create(user.userID, updatedName, public=False, collaborative=True, description=updatedDescription)

# iterate through the songs in the playlist -- fix syntax
playlistTracks = sp.playlist_items(playlist["id"])["items"]
for song in playlistTracks:
    updatedPlaylistTracks = sp.playlist_items(updatedPlaylist["id"])["items"]
    # call the songSelection method - pass the Song obj and the Update Style
    # song selection method should
    newSong = pickNewSong(song, playlistTracks, updatedPlaylistTracks, user.preferences.pointShuffleType)
    if newSong == "nope":
        print("skipping")
        continue
    sp.playlist_add_items(updatedPlaylist["id"], items=[newSong["uri"]], position=None)
if (user.preferences.saveOrUpdate == "UPDATE"):
    sp.current_user_unfollow_playlist(playlist["id"])
    sp.playlist_change_details(playlist["id"], name=playlist["name"])
