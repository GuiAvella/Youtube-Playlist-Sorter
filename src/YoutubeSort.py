import sys
import os
from pathlib import Path
from functools import partial
import json
import subprocess
import gzip
import time
from tkinter import ALL, W
from pydantic import FilePath
import requests
from ytmusicapi import YTMusic, OAuthCredentials, setup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc
import dotenv
from tqdm import tqdm

_Searches_ = 3

CookiesWant = ["SOCS", "VISITOR_PRIVACY_METADATA", "VISITOR_INFO1_LIVE", "PREF", "VISITOR_INFO1_LIVE",
               "__Secure-ROLLOUT_TOKEN", "__Secure-1PSIDTS", "__Secure-3PSIDTS", "HSID", "SSID", "APISID",
               "SAPISID", "__Secure-1PAPISID", "__Secure-3PAPISID", "SID", "__Secure-1PSID", "__Secure-3PSID",
               "LOGIN_INFO", "SIDCC", "__Secure-1PSIDCC", "__Secure-3PSIDCC", "__Secure-YNID=14.YT", "YSC",
               "wide"]
CookiesWant.reverse()

JsonBrowser = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,pt-BR;q=0.8,pt;q=0.5,en;q=0.3",
    "authorization": "SAPISIDHASH 1765874332_20ddde88547630439bec4694c8a8a0e31ad623cf_u SAPISID1PHASH 1765874332_20ddde88547630439bec4694c8a8a0e31ad623cf_u SAPISID3PHASH 1765874332_20ddde88547630439bec4694c8a8a0e31ad623cf_u",
    "connection": "keep-alive",
    "content-encoding": "gzip",
    "content-type": "application/json",
    "cookie": "SOCS=CAISNQgDEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjUxMDI5LjA0X3AwGgJlbiACGgYIgJuVyAY; VISITOR_PRIVACY_METADATA=CgJERRIEEgAgYg%3D%3D; PREF=f6=40000080&tz=Europe.Berlin&f4=4000000&f7=100&repeat=NONE; VISITOR_INFO1_LIVE=Jn4VLYl-9Qo; __Secure-ROLLOUT_TOKEN=CIXG0OSHyImzARDjybyE1NGQAxihh4qdssGRAw%3D%3D; __Secure-1PSIDTS=sidts-CjQBflaCddJYRXrW8nDqUlq-dNIpHf00a8D6q_yye0icLjdJ4bw_vmd1yeonvK_1NPUrOfLcEAA; __Secure-3PSIDTS=sidts-CjQBflaCddJYRXrW8nDqUlq-dNIpHf00a8D6q_yye0icLjdJ4bw_vmd1yeonvK_1NPUrOfLcEAA; HSID=AH1Nkl6hCeLKD61Ug; SSID=Apb8hmCqDSc3XY8o_; APISID=D4JUtdpKjnrIL-Dv/ALeh5kIbLb5IgSFWh; SAPISID=ieaW0VFXNOWxI6fu/A2GMsbLhEyDhEmlxz; __Secure-1PAPISID=ieaW0VFXNOWxI6fu/A2GMsbLhEyDhEmlxz; __Secure-3PAPISID=ieaW0VFXNOWxI6fu/A2GMsbLhEyDhEmlxz; SID=g.a0004AgaeMoELS_eSXSPmSJfWAI7Ic5t-3llR2Ec7yYvp9s5fGHr33zmm5LWGjav8ct90d2IwQACgYKATASARMSFQHGX2MijSBCq3VHi49rwxz9RUDWERoVAUF8yKpE2tNWbttVW-sc6lbhKCvL0076; __Secure-1PSID=g.a0004AgaeMoELS_eSXSPmSJfWAI7Ic5t-3llR2Ec7yYvp9s5fGHrYxDUnjRy_a5yfl9j83T5mwACgYKAdwSARMSFQHGX2MiFOxZbxscKfM6xv6JnX2aMBoVAUF8yKr5y6PKwSJcwkAgnx-1aP1d0076; __Secure-3PSID=g.a0004AgaeMoELS_eSXSPmSJfWAI7Ic5t-3llR2Ec7yYvp9s5fGHrgPKXFPKdk9u91aYFvVPBPAACgYKAeISARMSFQHGX2MiE_4JhG8mU09OQZUbuQD3AhoVAUF8yKrdL_Sb5k-Og7ko5_o3Ze3r0076; LOGIN_INFO=AFmmF2swRQIhAKUR-LaWcL-P4b6-MtAe-LmHBmhRLOEuMB3e54TvoAsRAiAIcEBZLFT3WBJUnTKR4xCwslnXyTU-F_FW8W6xwh3ryA:QUQ3MjNmemNCSGd0bHhYdHhKcXpNSkVWNVZndlRPd3ZzZlIxcDFGT1lWSmxtSkU4YV9QZk93U0xaQUJvXzI1QWQtN0QwMlBoWDA2NEJjM2NnNHhkcXQ0REUwVnhkU3hiR29hOS1VMXlvSTRaV0VxQ1k3UGRBV3FodFNMRG8zZ01TWFJHWGZrdEdlTGZFT2kzTXVoZTBPRExWTngydDNYcTBB; SIDCC=AKEyXzXdRNpqeuFuFyHuE4WGgcifWE1S8hd3u_g58h9Kt7mf0FvBGJ-6tywlCzf9nhPNTo2V-yQ; __Secure-1PSIDCC=AKEyXzVmWY2v8W-pFtpW0pQJrBTiRmFpWuph5oxtaDEAso9bBXx3ZoPgdIHbn8THAt5x1-Bjzg; __Secure-3PSIDCC=AKEyXzWAYfy2xBQt9D7va2aaExT98NCbuzNqBeSooGJmrygkyuXWwSbQa4WP7ffLVStQdtAWCg; __Secure-YNID=14.YT=FM1hvMhIA6T8RCa5OwvDQs7IkRmEk2-NShIiSHgeEBMPexUsJmLYtlIAwULERH8tqQvh3O7Jrn1sv4ChetKqM2RF2gPjC5-OYkkAuldGfrRXPwMeQv6HyzRm0y33bUMyu_rE8Xf4_zn_XYoKQK0ANJfLwpalNmuUAJ3tjwYoepx2qAQiiz1DGdj557MN9QjbuI2yA1xN2YCi_Qhqc5DMQc28Y9nmG03cYb2dNHrRyNfj2iMCdfH5z_5jb_HlKhJ8Cq65RvNyOE6WAZdYMwAuLnZx_lT_BU-lF-1f91x-HgAPj9Z1CRTe5NEyVr6XqS4a9GHezYW8g7n_zxqVHJR9pw; YSC=HTxpOorRu2w; wide=0",
    "origin": "https://music.youtube.com",
    "priority": "u=0",
    "referer": "https://music.youtube.com/explore",
    "te": "trailers",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "x-goog-authuser": "0",
    "x-goog-visitor-id": "CgtKbjRWTFlsLTlRbyjmtITKBjIKCgJERRIEEgAgYmLfAgrcAjE0LllUPUZNMWh2TWhJQTZUOFJDYTVPd3ZEUXM3SWtSbUVrMi1OU2hJaVNIZ2VFQk1QZXhVc0ptTFl0bElBd1VMRVJIOHRxUXZoM083SnJuMXN2NENoZXRLcU0yUkYyZ1BqQzUtT1lra0F1bGRHZnJSWFB3TWVRdjZIeXpSbTB5MzNiVU15dV9yRThYZjRfem5fWFlvS1FLMEFOSmZMd3BhbE5tdVVBSjN0andZb2VweDJxQVFpaXoxREdkajU1N01OOVFqYnVJMnlBMXhOMllDaV9RaHFjNURNUWMyOFk5bm1HMDNjWWIyZE5IclJ5TmZqMmlNQ2RmSDV6XzVqYl9IbEtoSjhDcTY1UnZOeU9FNldBWmRZTXdBdUxuWnhfbFRfQlUtbEYtMWY5MXgtSGdBUGo5WjFDUlRlNU5FeVZyNlhxUzRhOUdIZXpZVzhnN25fenhxVkhKUjlwdw%3D%3D",
    "x-origin": "https://music.youtube.com",
    "x-youtube-bootstrap-logged-in": "true",
    "x-youtube-client-name": "67",
    "x-youtube-client-version": "1.20251210.03.00"
}

Ouath = False

def get_documents_folder() -> Path:
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        return Path(winreg.QueryValueEx(key, "Personal")[0])
    except ImportError:
        return Path.home() / "Documents"
    
def AddEnvVar(path,key):
    print(f"the key {key} is missing from the .env")
    value = input("Input key value: ")
    dotenv.set_key(path,key,value)
    dotenv.load_dotenv(os.path.join(Path(PathBase).parent, "YoutubeSorter.env"))
    var = os.getenv(key)
    return var

documents = get_documents_folder()

#BASE_DIR = os.path.join(os.getenv('LOCALAPPDATA'), "Youtube_playlist_Sorter")
BASE_DIR = os.path.join(documents, "Youtube_playlist_Sorter")
PathBase = os.path.dirname(os.path.realpath(__file__)) + os.sep
CACHE_FILE = os.path.join(BASE_DIR,"genre_cache.json")

s = requests.Session()
s.request = partial(s.request, timeout=600)

IgnoreWords = ("the ", "an ", "a ")

def loadVars():
    path = os.path.join(Path(PathBase).parent, "YoutubeSorter.env")
    dotenv.load_dotenv(path)
    Last_fm = os.getenv('API_KEY_Last_fm')
    OauthID = os.getenv("client_id")
    OauthSecret = os.getenv("client_secret")
    
    if not Last_fm:
        Last_fm = AddEnvVar(path,'API_KEY_Last_fm')
    

    if Ouath:
        if not OauthID:
            OauthID = AddEnvVar(path,'client_id')
        if not OauthSecret:
            OauthSecret = AddEnvVar(path,'client_secret')

    return Last_fm, OauthID, OauthSecret

def check_and_update_package(package_name):
    try:
        subprocess.check_call(["python", '-m', 'pip', 'install', '--upgrade', 'package_name'])
        # Check for outdated packages
        result = subprocess.run(
            ["python", "-m", "pip", "list", "--outdated"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if the package is in the outdated list
        outdated_packages = result.stdout
        if package_name in outdated_packages:
            print(f"Update available for {package_name}. Updating...")
            subprocess.check_call(["python", "-m", "pip", "install", "--upgrade", package_name])
            print(f"{package_name} has been updated.")
        else:
            print(f"{package_name} is already up to date.")
    
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def GetCookies():
    print("Log into your account, click a playlist, and when done enter DONE into the terminal")
    
    # Set up Chrome with performance logging
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    driver = uc.Chrome(desired_capabilities=capabilities)
    driver.get("https://music.youtube.com/")
    time.sleep(15)
    input("Enter DONE when logged in: ")
    
    # Get cookies from the browser
    cookies = driver.get_cookies()
    cookie_dict = {}
    for cookie in cookies:
        if cookie["name"] in CookiesWant:
            cookie_dict[cookie["name"]] = cookie["value"]
    
    # Build the cookie string for headers
    cookie_header = "; ".join([f"{name}={value}" for name, value in cookie_dict.items()])
    
    # Get the request headers from performance logs
    browserRequests = driver.get_log("performance")
    headers = None
    
    for BrowserRequest in browserRequests:
        try:
            message = json.loads(BrowserRequest.get("message", {}))
            tempMessage = message.get("message", {}).get("params", {}).get("request")
            
            if tempMessage:
                url = tempMessage.get("url", "")
                if "https://music.youtube.com/youtubei/v1/browse?prettyPrint=false" in url:
                    headers = tempMessage.get("headers", {})
                    request_body = headers["log"]["entries"][0]["request"]["postData"]["text"]
                    raw = request_body.encode("latin1")
                    headers = gzip.decompress(raw)
                    break
        except Exception:
            continue
    
    if not headers:
        print("Could not find the browse request headers. quiting.")
        sys.exit()
        
    
    # Add the cookie header
    headers["cookie"] = cookie_header
    
    # Filter out unwanted headers
    ignore_headers = {"host", "content-length", "accept-encoding"}
    headers = {k: v for k, v in headers.items() if k.lower() not in ignore_headers and not k.lower().startswith("sec")}
    
    # Convert headers to the format expected by setup()
    headers_lines = [f"{k}: {v}" for k, v in headers.items()]
    headers_raw = "\n".join(headers_lines)
    
    print("Generated headers:")
    print(headers_raw)
    
    try:
        # Save to browser.json
        result = setup(PathBase + "browser.json", headers_raw)
        print("Successfully saved headers to browser.json")
        driver.quit()
        return result
    except Exception as E:
        print(f"Error during setup: {E}")
        # Try to save manually as fallback
        with open(PathBase + "browser.json", "w") as f:
            json.dump(headers, f, indent=4)
        print("Saved headers manually to browser.json")
        return json.dumps(headers)

def SortPlaylist(playlist):
    sortedTracks = sorted(playlist["tracks"],
                          key=lambda d: d['title'].casefold(),)
    return sortedTracks

def CharacterTransform(Char):
    while ord(Char) < 65 or ord(Char) > 122:
        if ord(Char) > 122:
            Char = chr(ord(Char)-24)
        else:
            Char = chr(ord(Char)+24)
    return (Char)

def EscolhaUsuario(option = None):
    # if not sys.argv == []:
    if len(sys.argv) > 1:
        option = int(sys.argv[1])
    elif not option:
        option = int(input(
            "From which playlist. Options:\n1-From liked songs\n2-playlist ID\nChoice: "))
    if option == 1:
        playlist = YTMusic.get_liked_songs(ytmusic, None)
    elif option == 2:
        toSortId = input("Paste the playlist ID: ")
        if toSortId.startswith("https://music.youtube.com/playlist?list="):
            toSortId = toSortId.lstrip(
                "https://music.youtube.com/playlist?list=").split("&")[0]
        playlist = YTMusic.get_playlist(ytmusic, toSortId, None)
    else:
        print("fez merda")
        exit()
    return (playlist)

def organizaPlaylist(playlist,Name = "-A/Z",Description = f" Organized alphabetically at: {time.ctime()}"):
    for n, track in enumerate(playlist["tracks"]):
        TrackLowered = str(track["title"][0]).lower()
        if ord(track["title"][0]) < 65 or ord(track["title"][0]) > 122:
            novo = str("")
            for Letra in track["title"]:
                novo = novo + str(CharacterTransform(Letra))
            track["title"] = novo
        elif TrackLowered.startswith(IgnoreWords):
            SpliceLocation = TrackLowered.find(" ")
            novo = track[SpliceLocation+1::]
            track["title"] = novo
        playlist["tracks"][n] = track
            
    sortedTracks = SortPlaylist(playlist)

    filtered = list((d['videoId']) for d in sortedTracks)
    # filteredIds=list(filtered)
    filteredIds = list(dict.fromkeys(filtered))
    if not sys.argv == []:
        OldPlaylist = (sys.argv[2])
    else:
        OldPlaylist = (
            input("Input new Playlist ID, or leave empty to create new one: "))
    if not OldPlaylist == "":
        musicsOldPlaylist = YTMusic.get_playlist(
            ytmusic, OldPlaylist, limit=None)['tracks']
        tamanho = 500
        print("cleaning old songs")
        if len(musicsOldPlaylist) > tamanho:
            while len(musicsOldPlaylist) > tamanho:
                try:
                    ytmusic.remove_playlist_items(
                        OldPlaylist, musicsOldPlaylist[0:tamanho])
                    musicsOldPlaylist = YTMusic.get_playlist(
                        ytmusic, OldPlaylist, limit=None)['tracks']
                    # musicsOldPlaylist = musicsOldPlaylist[tamanho:]
                except Exception as e:
                    print(e)
                    if e.args == "('Server returned HTTP 400: Bad Request.\nPrecondition check failed.',)":
                        musicsOldPlaylist = YTMusic.get_playlist(
                            ytmusic, OldPlaylist, limit=None)['tracks']
                    elif tamanho > 100:
                        tamanho = tamanho - 100
            ytmusic.remove_playlist_items(OldPlaylist, musicsOldPlaylist)
        elif len(musicsOldPlaylist) > 0:
            try:
                ytmusic.remove_playlist_items(OldPlaylist, musicsOldPlaylist)
            except Exception as e:
                print(e)
        print("Playlist cleaned, now adding new ones")
        playlistId = ytmusic.add_playlist_items(
            OldPlaylist, filteredIds, duplicates=False)
        ytmusic.edit_playlist(playlistId=OldPlaylist, description=(
            f"{playlist['title']} Organized alphabetically at: {time.ctime()}"))
    else:
        playlistId = ytmusic.create_playlist(
            f"{playlist['title']} {Name}", 
            f"{playlist['title']} {Description}", 
            video_ids=filteredIds)
        #time.sleep(5)
        #new_playlist = YTMusic.get_playlist(ytmusic, playlistId, limit=None)

def showUnliked():
    playlist = EscolhaUsuario()
    sortedTracks = SortPlaylist(playlist)
    filteredNames = list((d['title'])
                         for d in sortedTracks if d['likeStatus'] != 'LIKE')
    for name in filteredNames:
        print(name)

def getSongs():
    nome_musica = []
    while True:
        user = input('Name of song or multiple at a time separating with ; or STOP# to stop: ')
        if user.upper() == "STOP#":
            return nome_musica
        elif user.count(";") >= 1:
            musics = user.split(";")
            nome_musica.extend(musics)
        else:
            nome_musica.append(user)

def addSongName(title, nome_musica):
    answer = "N"
    if autenticated:
        answer = input("do you want to check if songs are liked (it adds preference when searching) [Y]/N: ")
        Liked = answer.upper()=="Y"
    playlist = {"tracks":[]}
    print("Searching for songs:")
    for name in tqdm(nome_musica):
        music = YTMusic.search(ytmusic, name, 'songs')
        if Liked:
            for i, mu in enumerate(music):
                if mu["inLibrary"]:
                    playlist["tracks"].append({"videoId":mu['videoId'] ,'title':mu['title']})
                    break
                elif i > 10:
                    playlist["tracks"].append({"videoId":music[0]['videoId'] ,'title':music[0]['title']})
                    break
        else:
            playlist["tracks"].append({"videoId":music[0]['videoId'] ,'title':music[0]['title']})
    sortedTracks = SortPlaylist(playlist)
    filtered = list((d['videoId']) for d in sortedTracks)
    filteredIds = list(dict.fromkeys(filtered))
    playlistId = ytmusic.create_playlist(
        title, "added songs organized alphabetically", video_ids=filteredIds)

def likeMusicas():
    playlist = EscolhaUsuario()
    sortedTracks = sorted(playlist["tracks"], key=lambda d: d['title'])
    filteredIds = list((d['videoId'])
                       for d in sortedTracks if d['likeStatus'] != 'LIKE')
    # filtered = list((d['videoId']) for d in sortedTracks)
    # filteredIds=list(dict.fromkeys(filtered))
    for id in filteredIds:
        a = YTMusic.rate_song(ytmusic, id, 'LIKE')

def removeClones():
    remove = []
    playlist = EscolhaUsuario()
    sortedTracks = sorted(playlist["tracks"], key=lambda d: d['title'])
    for index, name in enumerate(sortedTracks):
        if index > 0:
            if name['videoId'] == name_old:
                remove.append(name)
        name_old = name['videoId']
    if playlist['id'] == "LM":
        for music in remove:
            YTMusic.rate_song(ytmusic, music, "DISLIKE")
    else:
        YTMusic.remove_playlist_items(ytmusic, playlist['id'], remove)

def autenticate(OauthID, OauthSecret):
    if Ouath:
        try:
            # ytmusic = YTMusic(path+"oauth.json",requests_session=s)
            yt = YTMusic(PathBase + "oauth.json", oauth_credentials=OAuthCredentials(
                client_id=OauthID, client_secret=OauthSecret), requests_session=s)
        except Exception:
            print('no oauth.json, run "ytmusicapi oauth" in CMD to create it')
    else:
        tryToFix = True
        while tryToFix:
            try:
                yt = YTMusic(PathBase+"browser.json", requests_session=s)
                tryToFix = False  # Success, exit the loop
            except Exception as e:
                print(f"Error loading browser.json: {e}")
                answ = input("Invalid Cookies, to fix Paste Headers[1], open browser[2], quit[3] or continue[4]. ([1]/[2]/[3]/[4]): ")
                if answ == "3":
                    print("Please follow: https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html")
                    exit()
                elif answ == "2":
                    GetCookies()
                    # After getting cookies, try again
                    continue
                elif answ == "1":
                    try:
                        setup(PathBase+"browser.json")
                        print("Headers saved, trying to initialize...")
                        continue  # Try again with new headers
                    except Exception as E:
                        print(f"Setup failed: {E}")
                        continue
                else:
                    yt = YTMusic()
                    return yt, False

    return yt, True

def get_genre_lastfm(album,artist, title):
        
    url = "https://ws.audioscrobbler.com/2.0/"
    parameters = [
        {"method": "track.getTopTags", "artist": artist, "track": title, "api_key": API_KEY_Last_fm, "format": "json"},
        {"method": "album.getTopTags", "artist": artist, "album": album, "api_key": API_KEY_Last_fm, "format": "json"},
        {"method": "artist.getTopTags", "artist": artist, "api_key": API_KEY_Last_fm, "format": "json"}]
    if not album:
        parameters.pop(1)
    tags = []
    for params in parameters:
        r = requests.get(url, params=params)
        if r.status_code == 404:
            print(f"error 404 on track {title}")
        tags += ( r.json().get("toptags", {}).get("tag", []))
        
    if tags:
        seen = set()
        tags = [d for d in tags if d["name"] not in seen and not seen.add(d["name"])]
        tagsOrig = tags
        for n, tag in enumerate(tags.copy()):
            tagList = tag["name"].split()
            if "brazilian" in tagList:
                tags.append({"name": "brazil"})
            if "funk" in tagList or "Funk" in tagList:
                if not tag["name"] == "funk":
                    tags.append({"name": "funk"})

            """ if len(tagList) > 1:
                for t in tagList:
                    if not t.lower() == "music":
                        tags.append({"name": t}) """
        seen = set()
        tags = [d for d in tags if d["name"] not in seen and not seen.add(d["name"])]
        tags = tags[:_Searches_]
        return [t["name"] for t in tags]  # top 3 genres
        
    print("no tags found")
    return []

def load_cache():
    return json.load(open(CACHE_FILE, encoding="utf-8")) if os.path.exists(CACHE_FILE) else {}

def save_cache(cache):
    json.dump(cache, open(CACHE_FILE, "w", encoding="utf-8"), indent=2)

def get_genre_cached(album,artist, title):
    cache = load_cache()
    key = f"{artist}|{title}".lower()
    if key not in cache or len(cache[key]) < _Searches_:
        cache[key] = get_genre_lastfm(album,artist, title)
        save_cache(cache)
    return cache[key]

def SortByGenre():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    playlist = EscolhaUsuario()
    ALLGenres = []
    tracks = playlist['tracks']

    for n, track in enumerate(tracks):
        artist = track['artists'][0]["name"]
        if track['album']:
            album = track['album']['name']
        else:
            album = ""
        SongGenre = get_genre_cached(album,artist,track['title'])
        print(f"Track: {track['title']}\nGenre: {SongGenre}")
        ALLGenres += SongGenre
        playlist['tracks'][n] = track | {"Genres": SongGenre}
    ALLGenres = list(set(ALLGenres))
    print(sorted(ALLGenres,key=lambda d: d.casefold()))
    choice = input("Chose one or more genres separating the names with a ',': ")
    choiceList = choice.split(",")
    playlist['tracks'] = [
        track for track in playlist['tracks']
        if any(genre in choiceList for genre in track.get('Genres', []))
        ]
    organizaPlaylist(playlist,Name=str(choice))

def makePlaylistByM3U():
    FilePath = input("input m3u path: ").strip("'").strip('"')
    title = FilePath[FilePath.rfind(os.sep) + 1 : FilePath.rfind(".")]
    with open(FilePath,"r",encoding="utf-8") as file:
        content = file.read()
    fullMusicNames = content.splitlines()
    musicNames = []
    for musicPath in fullMusicNames:
        music = musicPath[musicPath.rfind(os.sep) + 1 : musicPath.rfind(".")]
        musicNames.append(music)
    print(musicNames)
    addSongName(title, musicNames)


if __name__ == "__main__":
    API_KEY_Last_fm, OauthID, OauthSecret = loadVars()

    ytmusic, autenticated = autenticate(OauthID, OauthSecret)

    if sys.argv[0].endswith(".py"):
        sys.argv.pop(0)

        
        if sys.argv == []:
            a = (input("OPTIONS:\nsort playlist alphabetically(1)" \
            "\nlike all the musics in a playlist(2)" \
            "\nRemove clones(3)" \
            "\nShow unliked(4)" \
            "\nAdd songs by name(5)" \
            "\nSort songs by genre(6)" \
            "\nMake playlist by M3U file(7)" \
            "\nUpdade Package(U)" \
            "\nRemove Browser.json(R)" \
            "\nChoice: ")).upper()
        else:
            a = sys.argv[0]
            
        match a:
            case '1':
                print("Organizing Playlist")
                organizaPlaylist(EscolhaUsuario())
            case '2':
                print("Liking Songs")
                likeMusicas()
            case '3':
                print("Removing Clones")
                removeClones()
            case '4':
                showUnliked()
            case '5':
                title = input("Input a title to the playlist: ")
                addSongName(title, getSongs())
            case '6':
                SortByGenre()
            case '7':
                makePlaylistByM3U()
            case "R":
                os.remove(PathBase+"browser.json")
            case 'U':
                check_and_update_package("ytmusicapi")
        print("done")
