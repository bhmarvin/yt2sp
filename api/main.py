import os
import pathlib
from config import SONGS_FOLDER
from flask import jsonify, Flask, request
from __init__ import yt2sp
from pytube import YouTube
from pydub import AudioSegment
from werkzeug.exceptions import BadRequest
import platform
import pygetwindow as gw
import subprocess


@yt2sp.route('/api/v1/', methods=['GET'])
def home():
    """Home function."""
    print("Request received")
    return jsonify({
        "download": "/api/v1/download/",
        "add": "/api/v1/add/",
        "url": "/api/v1/"
    })

@yt2sp.route('/api/v1/download/', methods=['GET'])
def download():
    """Downloads song"""
    try:
        video_url = request.args.get('url')
        song_name = request.args.get('name')
    except BadRequest as e:
        return f"Bad Request: {e.description}", 400
    yt_obj = YouTube(video_url)
    video_length = yt_obj.length
    audio_streams = yt_obj.streams.filter(only_audio=True, file_extension='mp4')
    if audio_streams is None or len(audio_streams) == 0:
        return "No available streams", 404
    sorted_streams = sorted(audio_streams, key=lambda x: int(x.abr[:-4]), reverse=True)
    best_stream = sorted_streams[0]
    #download mp4 to songs folder
    best_stream.download(output_path=SONGS_FOLDER, filename=song_name + '.mp4')
    #convert to mp3
    mp4_path = SONGS_FOLDER / f"{song_name}.mp4"
    audio = AudioSegment.from_file(mp4_path, format="mp4")
    #eventually add hnadling for custom cropping
    start_time = 0
    end_time = video_length
    trimmed_audio = audio[start_time*1000:end_time*1000]
    output_path = SONGS_FOLDER / f"{song_name}.mp3"
    trimmed_audio.export(output_path, format="mp3")
    #CONVERTED TO MP3 DELETE MP4
    os.remove(mp4_path)

    context = {"status":200, "message":"Successfully downloaded mp3"}
    bring_spotify_to_front()


    return jsonify(context)

@yt2sp.route('/api/v1/add/', methods=['POST'])
def add():
    """Adds song to playlist"""
    try:
        playlists = request.args.get('playlists')
        song_name = request.args.get('name')
    except BadRequest as e:
        return f"Bad Request: {e.description}", 400
    #now focus the spotify window
    bring_spotify_to_front()


def bring_spotify_to_front():
    system_platform = platform.system()

    if system_platform == "Windows":
        windows = gw.getWindowsWithTitle("Spotify")
        if windows:
            window = windows[0]
            window.activate()
    elif system_platform == "Darwin":  # macOS
        subprocess.run(['osascript', '-e', f'tell application "Spotify" to activate'])
    else:
        print("Unsupported platform")


if __name__ == "__main__":
    yt2sp.run(host='localhost', port=8000, debug=True)
