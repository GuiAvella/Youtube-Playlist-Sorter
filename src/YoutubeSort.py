from ytmusicapi import YTMusic
import os
path = os.path.dirname(os.path.realpath(__file__)) + os.sep
try:
    ytmusic = YTMusic(path+"oauth.json")
except:
    print('no oauth.json, run ytmusicapi oauth to create it')
    

def EscolhaUsuario():
    option=int(input("opcoes:\n1-pegar musicas curtidas\n2-id de playlist especifica "))
    if option == 1:
        playlist=YTMusic.get_liked_songs(ytmusic,None)
    elif option == 2:
        toSortId=input ("Id da playlist para organizar: ")
        playlist=YTMusic.get_playlist(ytmusic,toSortId,None)
    else:
        print("fez merda")
        exit()
    return(playlist)

def organizaPlaylist():
    playlist=EscolhaUsuario()
    sortedTracks=sorted(playlist["tracks"],key=lambda d: d['title'])
    playlistId = ytmusic.create_playlist(playlist['title']+"-A/Z",playlist['title']+" organizada alfabeticamente")
    filtered = list((d['videoId']) for d in sortedTracks)
    filteredIds=list(dict.fromkeys(filtered))
    #aa=ytmusic.add_playlist_items(playlistId,filteredIds,duplicates=True)
    aa=ytmusic.add_playlist_items(playlistId,filteredIds)

def likeMusicas():
    playlist=EscolhaUsuario()
    sortedTracks=sorted(playlist["tracks"],key=lambda d: d['title'])
    filteredIds=list((d['videoId']) for d in sortedTracks if d['likeStatus']!='LIKE')
    #filtered = list((d['videoId']) for d in sortedTracks)
    #filteredIds=list(dict.fromkeys(filtered))
    for id in filteredIds:
        a=YTMusic.rate_song(ytmusic,id,'LIKE')
  


if True:
    a=int(input("quer organizar uma playlist(1) ou dar like nas musicas(2)"))
    if a == 1:
        organizaPlaylist()
        print("feito")
    else:
        likeMusicas()
        print("likeado")