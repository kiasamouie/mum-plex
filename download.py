import subprocess
import requests
from bs4 import BeautifulSoup
import re
import os

url = 'https://mbc21.tv/zalem-duble.php'

base_output_dir = os.path.join('/', 'media', 'kiaserver', 'Data', 'Tv Shows')
series_name = re.sub(r'[-_]', ' ', url.rsplit('/', 1)[-1].split('.')[0]).title() 
output_dir = os.path.join(base_output_dir, series_name)
os.makedirs(output_dir, exist_ok=True)

if not os.path.isdir(output_dir):
    exit("No save dir")

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')
videos = {}
rows = soup.select('tr')
for index, row in enumerate(rows):
    if index < 1:
        continue
    urls = []
    cells = row.find_all('td')
    for cell in cells:
        buttons = cell.find_all('button')
        for button in buttons:
            onclick_attr = button.get('onclick')
            if onclick_attr:
                url_pattern = re.search(r"window\.open\(['\"]([^'\"]+)", onclick_attr)
                if url_pattern:
                    video_url = f"https:{url_pattern.group(1)}"
                    urls.append(video_url)
    
    if urls:
        videos[index] = urls

base_command = 'yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" -o "{}" "{}"'
for index, url_list in videos.items():
    output_filename = os.path.join(output_dir, f"{index:02d}_%(title)s.%(ext)s")
    for url in url_list:
        command = base_command.format(output_filename, url)
        print(f"Trying URL for video {index}: {url}")
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Successfully downloaded video {index} using URL: {url}")
            break  
        except subprocess.CalledProcessError as e:
            print(f"Failed to download video {index} using URL: {url}. Error: {e}")
            continue  
    
print("Download process complete.")
