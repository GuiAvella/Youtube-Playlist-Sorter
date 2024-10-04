from ytmusicapi import YTMusic
import os
path = os.path.dirname(os.path.realpath(__file__)) + os.sep
try:
    ytmusic = YTMusic(path+"oauth.json")
except:
    print('no oauth.json, run "ytmusicapi oauth" in CMD to create it')
    

def EscolhaUsuario():
    option=int(input("From which playlist. Options:\n1-From liked songs\n2-playlist ID\nChoice: "))
    if option == 1:
        playlist=YTMusic.get_liked_songs(ytmusic,None)
    elif option == 2:
        toSortId=input ("Paste the playlist ID: ")
        playlist=YTMusic.get_playlist(ytmusic,toSortId,None)
    else:
        print("fez merda")
        exit()
    return(playlist)

def organizaPlaylist():
    playlist=EscolhaUsuario()
    sortedTracks=sorted(playlist["tracks"],key=lambda d: d['title'])
    
    filtered = list((d['videoId']) for d in sortedTracks)
    filteredIds=list(dict.fromkeys(filtered))
    playlistId = ytmusic.create_playlist(playlist['title']+"-A/Z",playlist['title']+" Organized alphabetically",video_ids=filteredIds)
    new_playlist=YTMusic.get_playlist(ytmusic,playlistId,None)


def likeMusicas():
    playlist=EscolhaUsuario()
    sortedTracks=sorted(playlist["tracks"],key=lambda d: d['title'])
    filteredIds=list((d['videoId']) for d in sortedTracks if d['likeStatus']!='LIKE')
    #filtered = list((d['videoId']) for d in sortedTracks)
    #filteredIds=list(dict.fromkeys(filtered))
    for id in filteredIds:
        a=YTMusic.rate_song(ytmusic,id,'LIKE')
  


if True:
    a=int(input("sort playlist alphabetically(1) or like all the musics in a playlist(2): "))
    if a == 1:
        organizaPlaylist()
        print("done")
    else:
        likeMusicas()
        print("liked")