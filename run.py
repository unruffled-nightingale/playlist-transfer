#!/usr/bin/python
import httplib2
import sys
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


flow = flow_from_clientsecrets("client_secrets.json",
                                message='client_secrets.json not found.',
                                scope="https://www.googleapis.com/auth/youtube")

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  flags = argparser.parse_args()
  credentials = run_flow(flow, storage, flags)

youtube = build("youtube", "v3",  http=credentials.authorize(httplib2.Http()))

def get_playlists():
    res = youtube.playlists().list(part = 'snippet', channelId ='UCinjL5fVqwd6NVZquwYD9EA', maxResults="50")
    data = res.execute()
    print(data['items'][0]['snippet']['title'])


def get_songs():
    res = youtube.playlistItems().list(part="snippet", playlistId='PLbG37lFgYx86iCaJvUx4mmBQTue_zbp06', maxResults="50")
    data = res.execute()
    print(data['items'])

def create_playlist():
    res = youtube.playlists().insert(part="snippet,status",  body=dict(
                                                                snippet=dict( title="Test Playlist2",
                                                                    ),
                                                                    status=dict(
                                                                      privacyStatus="public"
                                                                    )
                                                                  )
                                                                ).execute()
    data=res.execute()
    print(data)

def insert_song():
    res = youtube.playlistItems().insert(part="snippet", body = {"snippet": {
                                                                    "playlistId": "PLbG37lFgYx86iCaJvUx4mmBQTue_zbp06",
                                                                    "resourceId": {
                                                                      "kind": "youtube#video",
                                                                      "videoId": "ppQPw-iUgkU"
                                                                    }
                                                                 }})
    data = res.execute()
    print(data)

insert_song()