"""
Author: Isaiah Mercado
Purpose: Driver file
Desired Outcome: Connects to user's spotify account and updates playlist based on user prefs
"""
import spotipy
import datetime
from datetime import timedelta
from Preferences import Preferences
from Account import Account

from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

# initialize a spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# fetch a FAKE user
prefs = Preferences("7", "ALBUM", "SAVE")
userPlaylists = sp.current_user_playlists(limit=50, offset=0)
user = Account(prefs, userPlaylists, 0)

# iterate through the playlists
for playlist in userPlaylists:

    # compare lastUpdated for each playlist to the refreshPeriod and the current datetime
    now = datetime.datetime.now()
    minimumUpdateDate = user.lastUpdate + timedelta(days=prefs.refreshPeriod)
    if(now < minimumUpdateDate):
        continue
    # iterate through the songs in the playlist -- fix syntax
    for song in playlist:
        # call the songSelection method - pass the Song obj and the Update Style

        # song selection method should

            # fetch the full album or the artist's discography

            # decide on a song to update with

            # add the song to a new playlist

    # new playlist should be created by now

    # final decision phase begins

    # show the user the new playlist

    # ask user if they want to...
        # update old playlist
        # delete the old playlist and create the new one
        # allow auto-update to decide based on their chosen preferences

    # carry out the final decision
        # update function (old playlist, new playlist)
        # delete/create function (old playlist, new playlist)

# move on to another playlist

