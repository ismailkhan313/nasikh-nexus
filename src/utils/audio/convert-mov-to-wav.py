import subprocess
import os
import sys
import math


def get_duration(input_file):
    """Gets the duration of the input file using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_file,
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return float(result.stdout)


def convert_and_split(input_path):
    # Fixed Output Directory
    output_dir = "/Users/viz1er/Movies/Trading Sessions"

    # Ensure the directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    # Configuration for < 200MB chunks
    # WAV (16-bit, 44.1kHz, Stereo) = ~176.4 KB/s
    # 200MB / 176.4 KB/s = ~1188 seconds.
    # We use 1100 seconds (~185MB) to stay safely under the limit.
    chunk_duration_seconds = 1100

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    total_duration = get_duration(input_path)
    num_chunks = math.ceil(total_duration / chunk_duration_seconds)

    print(f"--- Processing: {base_name} ---")
    print(
        f"Total Duration: {total_duration:.2f}s | Splitting into {num_chunks} parts..."
    )

    for i in range(num_chunks):
        start_time = i * chunk_duration_seconds
        output_filename = f"{base_name}-part-{str(i+1).zfill(2)}.wav"
        full_output_path = os.path.join(output_dir, output_filename)

        # ffmpeg command
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-t",
            str(chunk_duration_seconds),
            "-i",
            input_path,
            "-vn",  # No video
            "-acodec",
            "pcm_s16le",  # Standard 16-bit WAV
            "-ar",
            "44100",  # 44.1kHz sample rate
            "-ac",
            "2",  # Stereo
            full_output_path,
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"Saved: {full_output_path}")

    print("\nAll parts successfully saved to Trading Sessions folder!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        path = (
            input("Drag and drop the .mov file here (or enter path): ")
            .strip()
            .strip("'")
            .strip('"')
        )
    else:
        path = sys.argv[1].strip("'").strip('"')

    convert_and_split(path)
