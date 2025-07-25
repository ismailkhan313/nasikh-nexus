With yt-dlp and aria2c installed the below command is what is used in terminal to download an existing playlist from youtube. Before running the below command `cd` into the folder you want to download this audio first.

`yt-dlp --downloader aria2c --downloader-args "aria2c:-x16 -s16 -k1M" -x --audio-format mp3 https://www.youtube.com/playlist\?list\=PL4mTEQpP9b5FsKAbRwC9h1dJaUmV0mzd8`

The script dl-yt-audio.py does the same thing but reads from youtube-urls.txt when a youtube playlist doesn't exist and I have to recreate it. Otherwise use the above command.
