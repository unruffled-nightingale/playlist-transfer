#!/usr/bin/python
import httplib2
import sys
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

class User(object):

    def __init__(self, auth):
        flow = flow_from_clientsecrets(auth,
                                        message='client_secrets.json not found.',
                                        scope="https://www.googleapis.com/auth/youtube")

        storage = Storage("transfer-playlist-oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
             flags = argparser.parse_args()
             credentials = run_flow(flow, storage, flags)

        self.youtube = build("youtube", "v3",  http=credentials.authorize(httplib2.Http()))

    def get_playlists(self, channel_id):
        res = self.youtube.playlists().list(part='snippet', channelId=channel_id, maxResults="50")
        data = res.execute()
        playlists = [(i['snippet']['title'], i['id']) for i in data['items']]
        while 'nextPageToken' in data:
            res = self.youtube.playlists().list(part='snippet', channelId =channel_id, maxResults="50", pageToken=data['nextPageToken'])
            data = res.execute()
            current_page = [(i['snippet']['title'], i['id']) for i in data['items']]
            playlists.extend(current_page)
        return playlists

    def get_songs(self, playlist_id):
        res = self.youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults="50")
        data = res.execute()
        songs = [ i['snippet']['resourceId']['videoId'] for i in data['items']]
        while 'nextPageToken' in data:
            res = self.youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults="50", pageToken=data['nextPageToken'])
            data = res.execute()
            current_page = [ i['snippet']['resourceId']['videoId'] for i in data['items'] ]
            songs.extend(current_page)
        return songs


    def create_playlist(self, playlist):
        res = self.youtube.playlists().insert(part="snippet,status",  body=dict(
                                                                    snippet=dict( title=playlist,
                                                                        ),
                                                                        status=dict(
                                                                          privacyStatus="public"
                                                                        )
                                                                      )
                                                                    )
        data = res.execute()
        return data['id']


    def insert_song(self, playlist_id, song_id):
        try:
            res = self.youtube.playlistItems().insert(part="snippet", body = {"snippet": {
                                                                            "playlistId": playlist_id,
                                                                            "resourceId": {
                                                                              "kind": "youtube#video",
                                                                              "videoId": song_id
                                                                            }
                                                                         }})
            res.execute()
        except:
            print('ERRORED - ' + song_id)

    def delete_playlist(self, playlist_id):
        res = self.youtube.playlists().delete(id=playlist_id)
        res.execute()


    def delete_all_playlists(self, auth, channel):
        playlists = self.get_playlists(channel)
        for i in playlists:
            self.delete_playlist(i[1])

    def copy_library(self, src_channel):
        src_playlists = self.get_playlists(src_channel)
        src_library = []
        for title, id in src_playlists:
            playlist = {}
            playlist['id'] = id
            playlist['title'] = title
            playlist['songs'] = self.get_songs(id)
            src_library.append(playlist)
        return src_library

    def paste_library(self, src_library, user_channel):
        user_playlists = {k:v for k, v in self.get_playlists(user_channel)}
        for src_playlist in src_library:
            # FUNCTION - create playlist - (new_playlist, exisiting_playlists) - user_playlist_id
            if src_playlist['title'] not in list(user_playlists.keys()):
                user_playlist_id = self.create_playlist(src_playlist['title'])
            else:
                user_playlist_id = user_playlists[src_playlist['title']]
            user_songs = self.get_songs(user_playlist_id)
            print('inserting songs into - '+src_playlist['title'])
            for song_id in src_playlist['songs']:
                # FUNCTION - create song - (new_song, exisiting_songs) - None
                if song_id not in user_songs:
                    self.insert_song(user_playlist_id, song_id)

    def run(self, src_channel, user_channel):
        src_library = self.copy_library(src_channel)
        self.paste_library(src_library, user_channel)



if __name__=='__main__':

    user = User('client_secrets.json')
    user.run('UC1eOi_4jVFP5IPnjogNiAWg','UCinjL5fVqwd6NVZquwYD9EA')









