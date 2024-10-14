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

def showUnliked():
    playlist=EscolhaUsuario()
    sortedTracks=sorted(playlist["tracks"],key=lambda d: d['title'])
    filteredNames=list((d['title']) for d in sortedTracks if d['likeStatus']!='LIKE')
    for name in filteredNames:
        print(name)

def addSongName():
    musicas = []
    nome_musica=[]
    while True:
        user = input('Name of song or STOP# to stop: ')
        if user.upper() == "STOP#":
            break
        else:
            nome_musica.append(user)
    for name in nome_musica:
        a = YTMusic.search(ytmusic,name, 'songs',limit= 1)
        musicas.append(a[0])
    sortedTracks=sorted(musicas,key=lambda d: d['title'])
    filtered = list((d['videoId']) for d in sortedTracks)
    filteredIds=list(dict.fromkeys(filtered))
    playlistId = ytmusic.create_playlist("added songs","added songs organized alphabetically",video_ids=filteredIds)

def likeMusicas():
    playlist=EscolhaUsuario()
    sortedTracks=sorted(playlist["tracks"],key=lambda d: d['title'])
    filteredIds=list((d['videoId']) for d in sortedTracks if d['likeStatus']!='LIKE')
    #filtered = list((d['videoId']) for d in sortedTracks)
    #filteredIds=list(dict.fromkeys(filtered))
    for id in filteredIds:
        a=YTMusic.rate_song(ytmusic,id,'LIKE')
  
def removeClones():
    remove=[]
    playlist=EscolhaUsuario()
    sortedTracks=sorted(playlist["tracks"],key=lambda d: d['title'])
    for index , name in enumerate(sortedTracks):
        if index > 0:
            if name['videoId'] == name_old:
                remove.append(name)
        name_old = name['videoId']
    YTMusic.remove_playlist_items(ytmusic,playlist['id'],remove)

while True:
    a=(input("OPTIONS:\nsort playlist alphabetically(1)\nlike all the musics in a playlist(2)\nRemove clones(3)\nShow unliked(4)\nAdd songs by name(5)\nOr #QUIT to quit\nChoice: "))
    if a == '1':
        organizaPlaylist()
        print("done")
    elif a == '2':
        likeMusicas()
        print("liked")
    elif a == '3':
        removeClones()
        print("done")
    elif a == '4':
        showUnliked()
    elif a == '5':
        addSongName()
    elif a == "#QUIT":
        break
        