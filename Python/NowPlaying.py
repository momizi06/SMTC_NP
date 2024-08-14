"""SMTC (System Media Transport Controls) から曲情報を取得し、Misskeyに投稿する

Details:
    SMTC_NowPlaying.exeを実行し、なうぷれを自動でMisskeyに投稿するスクリプト。
    Apple Musicのみ、曲情報を元にApple Musicの曲URLを取得し、投稿本文に追加する事が可能。

Constants:
    SMTC_EXE (str): SMTC_NowPlaying.exeのパス
    APM_URL_ADD (bool): Apple Musicの曲URLを投稿本文に追加するかどうか
    COUNTRY_CODE (str): Apple Musicの国コード
    APM_PATTERN (str): Apple MusicのSMTC内部IDのパターン
    SERVER (str): MisskeyインスタンスのURL
    TOKEN (str): APIトークン

"""

import re
import requests
import urllib.parse
import json
import subprocess

from logging import getLogger, StreamHandler, INFO, Formatter

# ログの設定
handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(
    Formatter("[%(asctime)s] : %(funcName)s (%(lineno)s) | %(message)s")
)
logger = getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)


SMTC_EXE = "SMTC_NowPlaying/bin/Release/net8.0-windows10.0.22621.0/SMTC_NowPlaying.exe"
APM_URL_ADD = True
COUNTRY_CODE = "jp"
APM_PATTERN = r"AppleInc"

SERVER = "https://misskey.io"
TOKEN = "(Write your API token here)"


def getSongInfo() -> dict:
    """曲情報をSMTC_EXEから取得する

    Details:
        SMTC_EXEを実行し、標準出力に出力されたJSON形式の曲情報を取得する

    Returns:
        dict: 曲情報が含まれる辞書
    """
    try:
        logger.info(f"Getting song information")
        logger.info(f"SMTC_EXE: {SMTC_EXE}")
        result = subprocess.run([SMTC_EXE], stdout=subprocess.PIPE)
    except Exception as e:
        logger.error(e)
        return None
    result_json = result.stdout.decode("utf-8")
    if "No session found." in result_json:
        logger.info("No session found (Not playing music).")
        return None
    else:
        return json.loads(result_json)


def getSongUrl(title: str, artist: str, album: str) -> str:
    """Apple Musicの曲URLを取得する

    Args:
        title (str): 曲名(タイトル)
        artist (str): アーティスト名
        album (str): アルバム名

    Returns:
        str: Apple Musicの曲URL
    """
    text = urllib.parse.quote(f"{title} {artist} {album}")
    logger.info(f"Searching Apple Music URL")
    logger.info(f"Search Text: {text}")
    url = f"https://music.apple.com/{COUNTRY_CODE}/search?term={text}"
    try:
        response = requests.get(url)
        pattern = rf"https://music.apple.com/{COUNTRY_CODE}/album/.*/.*\?i=[0-9]*"
        string = response.text
        return re.search(pattern, string, flags=0).group()
    except Exception as e:
        logger.error(e)
        return ""


def makePostText(songInfo: dict) -> str:
    """投稿するテキストを作成する

    Args:
        songInfo (dict): 曲情報が含まれる辞書

    Returns:
        str: 投稿するテキスト
    """
    song_title = songInfo["Title"]
    song_artist = songInfo["Artist"]
    song_albumartist = songInfo["AlbumArtist"]
    song_album = songInfo["AlbumTitle"]
    song_url = ""
    smtc_id = songInfo["Id"]

    if re.match(APM_PATTERN, smtc_id, flags=0) is not None:
        song_artist = song_albumartist.split(" — ")[0]
        song_album = song_albumartist.split(" — ")[1]
        if APM_URL_ADD:
            song_url = getSongUrl(song_title, song_artist, song_album)
    else:
        match song_artist, song_albumartist:
            case "", "":
                song_artist = "None"
            case "", _:
                song_artist = song_albumartist
            case _, "":
                song_artist = song_artist
            case _, _:
                song_artist = song_artist

        match song_album:
            case "":
                song_album = "None"
            case _:
                song_album = song_album

    return f"#NowPlaying: {song_title} / {song_artist} - {song_album}\n{song_url}"


def post_new_note(text: str, token: str, server: str) -> None:
    """新しいノートを投稿する

    Args:
        text (str): 投稿するテキスト
        token (str): APIトークン(最低でも「ノートの作成・削除」権限が必要)
        server (str): MisskeyインスタンスのURL
    """
    url = f"{server}/api/notes/create"
    headers = {"Content-Type": "application/json"}
    data = {"i": token, "text": text}
    logger.info(f"Posting a new note")
    logger.info(f"URL: {url}")
    logger.info(f"Text: {text}")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        logger.error(response.json())
    else:
        logger.info("Successfully posted a new note.")


songInfo = getSongInfo()
if songInfo is None:
    logger.error("Failed to get song information.")
    exit(1)
post_text = makePostText(songInfo)
post_new_note(post_text, TOKEN, SERVER)
