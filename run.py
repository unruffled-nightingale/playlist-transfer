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


if __name__=='__main__':

    def copy_channel(auth, channel):
        src = User(auth)
        playlists = src.get_playlists(channel)
        library = []
        for title, id in playlists:
            playlist = {}
            playlist['id'] = id
            playlist['title'] = title
            playlist['songs'] = src.get_songs(id)
            library.append(playlist)
        for playlist in library:
            new_playlist_id = src.create_playlist(playlist['title'])
            print(new_playlist_id)
            for song in playlist['songs']:
                src.insert_song(new_playlist_id, song)

    def delete_all_playlists(auth, channel):
        src = User(auth)
        playlists = src.get_playlists(channel)
        for i in playlists:
            id = i[1]
            print(id)
            src.delete_playlist(id)

    copy_channel('client_secrets.json', 'UC1eOi_4jVFP5IPnjogNiAWg')





