import unittest

from run import User

class TestUser(unittest.TestCase):

    def test_init(self):
        user = User('client_secrets.json')

    def test_get_playlist(self):
        user = User('client_secrets.json')
        playlists = user.get_playlists('UC1eOi_4jVFP5IPnjogNiAWg')
        print (playlists)

    def test_get_songs(self):
        user = User('client_secrets.json')
        songs = user.get_songs('PLXZGpzbl0dxjz8NJbqWEO0lCPdeI8-Qyv')
        print (songs)

    def test_create_playlist(self):
        user = User('client_secrets.json')
        response = user.create_playlist('test20170427')
        print(response)

    def test_insert_song(self):
        user = User('client_secrets.json')
        user.insert_song('PLbG37lFgYx86iCaJvUx4mmBQTue_zbp06', 'c7Fv9pzu8ps')


    def test_delete_playlist(self):
        user = User('client_secrets.json')
        user.delete_playlist('PLbG37lFgYx86iCaJvUx4mmBQTue_zbp06')

if __name__ == '__main__':
    unittest.main()
