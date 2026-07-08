cat << 'EOF' > README.md
# 🎯 Sniper Daemon

A high-performance, system-agnostic extraction engine capable of pulling audio tracks, full playlists, and media content from YouTube and Instagram. Sniper automates metadata tagging, embeds synchronized or flat-text lyrics using the LRCLIB architecture, and formats outputs directly into localized `.opus` containers(youtube's native extension for audio files) and '.mp4' for "video+audio".
The daemon can handle single streams/videos up to 4gb in size, before breaking it down into multiple parts to further support it.

I found using yt-dlp alone really annnoying(this script is built upon yt-dlp by the way), since extracting pure audio from youtube videos was a nightmare, let alone synced Lyrics tagging.

The script is mainly used for downloading song tracks from youtube playlists at the highest possible audio quality(128-160kbps opus files, the maximum allowed at youtube), and automatically tags them with all public data/Embedded lyrics and images.

---

## ⚙️ Core Architecture & Operational Tiers

When initialized, Sniper parses the source URL and presents a **3 Tier text based questionaire** to Allow more control over the process:

### Tier 1:Audio or Video:
*  **question:** The very first tier asks us about wether we want to extract only audio or video.

### Tier 2:Thumbnail(idk impulsive check):
* **question** This asks us wether we want the thumbnail tagged on the file to be 1:1 ratio of the youtube thumbnail(cuts a clean square in middle) or the original thumbnail.

### Tier 3:Lyrics embedding(Flagship of my script):

*   **Description** The Third tier is used to parse lyrics into the opus files. This can be done in a total of 4 ways of control over the process, thus the Third tier derives into 4 smaller subsections.

*   
#### 1️⃣ Section 1: Full Snipe 🚀
*   **Execution:** Automated 4 mini tier sniping system.
*   **Pipeline:** Requests audio from *"LRCLIB"* (only synced lyrics if possible) -> If step 1 fails, moves on to grabbing the video's own "synchronised timestamped captions" -> if the previous step fails, Tries to grab Plain lyrics from *"LRCLIB"* -> If even that fails, finally tries to grab youtube's auto generated captions -> Saves completed track instantly to `~/Music/Downloads`.
*   **NOTE** This is the Main loop of the script and the recomended path for downloading playlists.PLs read the end note in case some videos fail to grab their lyrics even after the 4 step process.


#### 2️⃣ Section 2: Yt caption route💅
*   **Execution:** Choose this route if you know the video/playlist you are downloading all have Creator set proper timestamped captions.
*   **Pipeline:** Attaches the Actual official captions set by the video's creator himself. Note that you should not use this route if you are unsure of the creator having added actual captions.


#### 3️⃣ : Open source only 🔊
*   **Execution:** Pick this if you only want to grab lyrics from open source "LRCLIB". 
*   **Pipeline:** Pulls the Lyrics directly from *"LRCLIB"* , be it plain or synced(synced prioritized).
*   **NOTE** PLs read the end note in case some videos fail to grab their lyrics

#### 4️⃣ Tier 4: Manual pathway👷
*   **Execution:** If you want the script to annoy you at every step of the 4 process.
*   **Pipeline:** Performs **Section 1: FULL snipe**, but asks you for confirmation after each tier, effectively destroying the automation loop and allowing manual stoppage(phew writing this is a chore man).

---
### Tier 5:
This is the final tier(not really a tier idk anymore).
After the script finishes, it shows you a list of the audio files that couldnt grab their synced SONG lyrics from either *"LRCLIB"* or Youtube synced captions.
It also shows you a red list for the songs that couldnt get ANY lyrics of any form and presents you with the option of Renaming the song tracks and triggering section 1 again, or letting it go(see Note at end to understand why renaming).

---
## 🚀 Usage & Execution Workflows

Sniper is designed to Only run on linux or mobile for now, but i will add more Versions in the future.
### On linux:
The script is set to be executed globally across your environment using two distinct patterns:

### 🖥️ Method A: The Native Terminal Call
Pass any video, playlist, or Instagram URL directly as an execution argument from anywhere on your file system:
```bash
sniper "https://www.youtube.com/watch?v=EXAMPLE"
```

⚡ Method B: The Bare-Metal Keyboard Hotkey (Linux Desktop)

For an ultra-fluid desktop workflow, you can trigger Sniper via a global keyboard shortcut to automatically pull whatever link is copied into your system clipboard memory.

Ensure xclip is installed on your system

  ```bash
sudo apt install xclip -y 
  ```

  Open System Settings -> Keyboard -> Shortcuts -> Custom Shortcuts.

  Create a new entry mapping your preferred key combo (e.g., Super + Shift + D) to execute this native terminal string:
  

  gnome-terminal -- bash -c "sniper \$(xclip -selection clipboard -o); exec bash"

Now, simply copy any URL (Ctrl + C) and hit your macro binding to fire up the execution matrix instantly!
