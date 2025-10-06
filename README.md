# YouTube Video Downloader

A Python script for downloading YouTube videos, shorts,

## Features

- Download YouTube Shorts from any channel
- Download all videos from a channel
- Download videos from a text file list
- Streaming downloads (videos download as they're found)
- Multiple quality options (Best, Good, Low)
- Bot detection bypass with realistic browser headers
- Automatic retry on failures
- Progress tracking and statistics
- MP4 format output

## Requirements

- Python 3.7 or higher
- yt-dlp
- FFmpeg (optional, for format conversion)

. Install FFmpeg (optional but recommended):
   - Windows: Download from https://ffmpeg.org/download.html
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

### Menu Options

1. **Download shorts from channel**
   - Enter a YouTube channel URL
   - Script will find and download all shorts (videos under 60 seconds)
   - Downloads start immediately as shorts are found

2. **Download all videos from channel**
   - Enter a YouTube channel URL
   - Downloads all videos regardless of length
   - Useful for archiving entire channels

3. **Download from text file**
   - Create a text file with one YouTube URL per line
   - Script will download all videos from the list
   - Example format:
     \`\`\`
     https://www.youtube.com/watch?v=VIDEO_ID_1
     https://www.youtube.com/watch?v=VIDEO_ID_2
     https://www.youtube.com/shorts/SHORT_ID_1
     \`\`\`

4. **View previous downloads**
   - Shows statistics from your last download session

5. **Load from saved list**
   - Load a previously saved list of videos to download

6. **Settings**
   - Configure download quality (Best/Good/Low)
   - Set custom output directory
   - Adjust download delays

7. **Exit**
   - Quit the program

### Quality Settings

- **Best Quality**: Downloads highest available quality
- **Good Quality**: Balanced quality and file size
- **Low Quality**: Smallest file size, lower quality

### Output Directory

By default, videos are saved to `./downloads/`. You can change this in the Settings menu.

### Download Delays

Random delays between downloads help avoid rate limiting. Default is 2-5 seconds.

## Troubleshooting

### "Sign in to confirm you're not a bot" Error

This happens when YouTube detects automated downloads. Solutions:
- Increase download delays in Settings
- Download fewer videos at once
- Wait a few hours before trying again
- Use a VPN to change your IP address

### "Requested format is not available" Error

The video format you requested isn't available. The script should handle this automatically, but if it persists:
- Try a different quality setting
- Update yt-dlp: `pip install --upgrade yt-dlp`

### Slow Downloads

- Check your internet connection
- Try a different quality setting (lower quality = faster downloads)
- Reduce concurrent downloads

### Script Crashes

- Make sure you have the latest version of yt-dlp
- Check that FFmpeg is installed correctly
- Verify the channel URL is correct

## Notes

- The script respects YouTube's terms of service
- Downloads are for personal use only
- Some videos may be unavailable due to geographic restrictions
- Private or deleted videos cannot be downloaded

## Updates

Keep yt-dlp updated for best results:
\`\`\`bash
pip install --upgrade yt-dlp
\`\`\`
