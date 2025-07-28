With yt-dlp and aria2c installed the below command is what is used in terminal to download an existing playlist from youtube. Before running the below command `cd` into the folder you want to download this audio first.

`yt-dlp --downloader aria2c --downloader-args "aria2c:-x16 -s16 -k1M" -x --audio-format mp3 https://www.youtube.com/playlist\?list\=PL4mTEQpP9b5FsKAbRwC9h1dJaUmV0mzd8`

The script dl-yt-audio.py does the same thing but reads from youtube-urls.txt when a youtube playlist doesn't exist and I have to recreate it. Otherwise use the above command.

`yt-dlp --downloader aria2c --downloader-args "aria2c:-x16 -s16 -k1M" -x --audio-format mp3 https://youtu.be/_DBxxJJJJR0?list=PLn3BBa1B7JxAqftZiq2M5WE6Q8KBQgjHb`

## How to Check Available Transcripts Before Downloading

The quickest way to check is to use yt-dlp directly in your terminal with the --list-subs flag. This will list all available subtitle tracks without downloading anything.

Open your terminal or command prompt.

Run the following command, replacing <video_or_playlist_url> with the URL you want to check:

```
bash
yt-dlp --list-subs <video_or_playlist_url>
```

The output will show a table of available languages. Manual transcripts will just have the language name (e.g., ar). Auto-generated transcripts will be clearly marked (e.g., ar-orig).
