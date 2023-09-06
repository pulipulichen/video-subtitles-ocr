from moviepy.editor import VideoFileClip
from PIL import Image
from fuzzywuzzy import fuzz

import time

# Record the start time
start_time = time.time()

def compare_strings(str1, str2, threshold=20):
    # Calculate the similarity (edit distance) between the strings
    similarity = fuzz.ratio(str1, str2)

    # Check if the similarity is greater than or equal to the threshold
    return similarity >= threshold

# Input video file path
video_file = '/input/input.mp4'

# Output directory to save frames
output_directory = '/output/'

# Load the video file
video_clip = VideoFileClip(video_file)

from cnocr import CnOcr

import re
#img_fp = './docs/examples/fanti.jpg'
ocr = CnOcr(rec_model_name='db_mobilenet_v3')  # 识别模型使用繁体识别模型


# Initialize variables for subtitle numbering and start time
#subtitle_number = 1
#start_time = 0

last_start = 0
last_timestamp = None
last_subtitle = None
timestamp_ms = None

subtitles = []

skip_frames = 0

print(video_clip.fps)

# Iterate through each frame and extract it
#with open(subtitle_file, 'w', encoding='utf-8') as f:
for i, frame in enumerate(video_clip.iter_frames()):
    # if i > 2000:
    #     break

    if skip_frames > 0:
        skip_frames = skip_frames - 1
        continue

    # Get the dimensions of the frame
    width, height = frame.shape[1], frame.shape[0]

    # Calculate the crop height (80% from the top)
    crop_height_top = int(0.7 * height)
    crop_height_interval = int(0.97 * height)

    # Crop the frame to remove the top 80%
    cropped_frame = frame[crop_height_top:, :]

    # Convert the NumPy array (frame) to a Pillow Image
    frame_image = Image.fromarray(cropped_frame)
    out = ocr.ocr(frame_image)

    if len(out) == 0:
        subtitle_text = ''
    else:
        # frame_image.save(f'{output_directory}/frame_{i:04d}.png')

        # Extract "text" values into a list of strings
        text_list = [item['text'] for item in out if item['score'] > 0.8]

        # Join the list of strings into a single string
        subtitle_text = ' '.join(text_list).strip()

    # Calculate the timestamp in ms
    timestamp_ms = int(i * (1000 / video_clip.fps))

    if last_start is None:
        last_start = timestamp_ms

    if last_timestamp is None:
        last_timestamp = timestamp_ms    

    if compare_strings(last_subtitle, subtitle_text) is False:
        if last_subtitle is None:
           last_subtitle = subtitle_text
           continue

        if len(last_subtitle) > 0:
            s = {
                "subtitle": last_subtitle,
                "start": last_start,
                "end": last_timestamp
            }
            subtitles.append(s)
            print(s)

            skip_frames = len(last_subtitle) * int(video_clip.fps / 3)
            
            frame_image.save(f'{output_directory}/frame_{i:04d}.png')

        #if len(subtitle_text) > 0:
        last_subtitle = subtitle_text
        last_start = timestamp_ms
        last_timestamp = timestamp_ms
    else:
        last_timestamp = timestamp_ms

if len(last_subtitle) > 0:
    subtitles.append({
        "subtitle": last_subtitle,
        "start": last_start,
        "end": timestamp_ms
    })

# Close the video clip
video_clip.close()

output_filename = '/output/output.srt'

# Open the output file for writing
with open(output_filename, 'w', encoding='utf-8') as f:
    subtitle_number = 1  # Initialize the subtitle number

    for subtitle_info in subtitles:
        # Get subtitle text, start time, and end time
        subtitle_text = subtitle_info['subtitle']
        start_time_ms = subtitle_info['start']
        end_time_ms = subtitle_info['end']

        # Format the start and end times as HH:MM:SS,ms
        start_time = '{:02d}:{:02d}:{:02d},{:03d}'.format(
            start_time_ms // 3600000, (start_time_ms // 60000) % 60, (start_time_ms // 1000) % 60, start_time_ms % 1000)
        end_time = '{:02d}:{:02d}:{:02d},{:03d}'.format(
            end_time_ms // 3600000, (end_time_ms // 60000) % 60, (end_time_ms // 1000) % 60, end_time_ms % 1000)

        # Write subtitle number, start time, end time, and subtitle text
        f.write(str(subtitle_number) + '\n')
        f.write(start_time + ' --> ' + end_time + '\n')
        f.write(subtitle_text + '\n\n')

        # Increment the subtitle number
        subtitle_number += 1

print(f'Subtitles have been written to {output_filename}')

print(subtitles)


# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

# Print the results
print(f"Start Time: {start_time}")
print(f"End Time: {end_time}")
print(f"Elapsed Time: {elapsed_time} seconds")