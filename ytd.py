#!/usr/bin/env python3

import os
import sys
import json
import subprocess
import time
import random
from pathlib import Path
from typing import List, Dict, Any

def install_yt_dlp():
    try:
        import yt_dlp
        return True
    except ImportError:
        print("Installing yt-dlp...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            import yt_dlp
            return True
        except Exception as e:
            print(f"Failed to install yt-dlp: {e}")
            return False

def get_yt_dlp_options():
    return {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
        },
        'socket_timeout': 60,
        'retries': 5,
        'fragment_retries': 5,
        'sleep_interval': 1,
        'max_sleep_interval': 5,
        'ignoreerrors': True,
        'no_warnings': False,
    }

def try_get_cookies():
    return None

def add_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def get_channel_videos(channel_url: str, shorts_only: bool = True) -> List[Dict[str, Any]]:
    try:
        import yt_dlp
        
        base_opts = get_yt_dlp_options()
        cookies = try_get_cookies()
        
        if cookies:
            base_opts['cookiesfrombrowser'] = cookies
        
        if shorts_only:
            base_opts['match_filter'] = lambda info: None if (info.get('duration') and 0 < info.get('duration') <= 60) else "Not a short"
        
        ydl_opts = {
            **base_opts,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }
        
        print(f"Using bot detection bypass...")
        if cookies:
            print(f"Using browser cookies for authentication")
        else:
            print(f"No cookies available - using anonymous access")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_type = "shorts" if shorts_only else "videos"
            print(f"Fetching {video_type} from: {channel_url}")
            
            try:
                add_delay(2, 4)
                channel_info = ydl.extract_info(channel_url, download=False)
            except Exception as e:
                error_msg = str(e).lower()
                if 'sign in' in error_msg or 'bot' in error_msg or 'cookies' in error_msg:
                    print(f"YouTube bot detection triggered!")
                    print(f"SOLUTIONS:")
                    print(f"  1. Wait 10-15 minutes before trying again")
                    print(f"  2. Try a smaller/different channel")
                    print(f"  3. Use a VPN to change your IP address")
                    return []
                else:
                    print(f"Failed to fetch channel info: {e}")
                    print("Try using a different channel URL format:")
                    print("  - https://youtube.com/@channelname")
                    print("  - https://youtube.com/c/channelname")
                    return []

            if not channel_info or 'entries' not in channel_info:
                print("No videos found in channel or invalid channel")
                return []
            
            valid_entries = [entry for entry in channel_info['entries'] if entry is not None]
            
            if not valid_entries:
                print(f"No {video_type} found in this channel")
                return []
                
            print(f"Found {len(valid_entries)} {video_type}")
            
            videos = []
            for entry in valid_entries:
                videos.append({
                    'url': entry.get('webpage_url', entry.get('url', '')),
                    'title': entry.get('title', 'Unknown'),
                    'duration': entry.get('duration', 0),
                    'upload_date': entry.get('upload_date', 'Unknown'),
                    'view_count': entry.get('view_count', 0),
                    'id': entry.get('id', '')
                })
            
            return videos
            
    except KeyboardInterrupt:
        print(f"\nOperation cancelled by user")
        return []
    except Exception as e:
        print(f"Critical error: {e}")
        return []

def download_videos_streaming(channel_url: str, settings: Dict[str, Any], shorts_only: bool = True):
    try:
        import yt_dlp
        
        Path(settings['output_dir']).mkdir(exist_ok=True)
        
        base_opts = get_yt_dlp_options()
        cookies = try_get_cookies()
        
        if cookies:
            base_opts['cookiesfrombrowser'] = cookies
        
        download_opts = {
            **base_opts,
            'outtmpl': f"{settings['output_dir']}/%(title)s [%(id)s].%(ext)s",
            'format': 'best',
            'quiet': False,
            'no_warnings': False,
            'writeinfojson': False,
            'writethumbnail': False,
        }
        
        scan_opts = {
            **base_opts,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        video_type = "shorts" if shorts_only else "videos"
        print(f"\nSTREAMING DOWNLOAD MODE")
        print("-" * 40)
        print(f"Channel: {channel_url}")
        print(f"Output: {settings['output_dir']}")
        print(f"Type: {video_type}")
        print(f"Quality: Best available format")
        print(f"Bot bypass: {'Enabled with cookies' if cookies else 'Enabled without cookies'}")
        print("-" * 40)
        print(f"Scanning and downloading {video_type} as found...")
        print("Press Ctrl+C to stop at any time")
        print("-" * 40)

        downloaded = 0
        failed = 0
        processed = 0
        
        with yt_dlp.YoutubeDL(scan_opts) as scan_ydl:
            try:
                print("Preparing to scan channel...")
                add_delay(3, 5)
                
                channel_info = scan_ydl.extract_info(channel_url, download=False)
                
                if not channel_info or 'entries' not in channel_info:
                    print("No videos found in channel")
                    return
                
                valid_entries = [entry for entry in channel_info['entries'] if entry is not None]
                total = len(valid_entries)
                print(f"Found {total} total videos in channel")
                print(f"Now checking each video and downloading {video_type} immediately...\n")
                
                for i, entry in enumerate(valid_entries, 1):
                    try:
                        processed += 1
                        
                        detail_opts = {
                            **get_yt_dlp_options(),
                            'quiet': True,
                            'no_warnings': True,
                            'socket_timeout': 10,
                            'retries': 1,
                        }
                        
                        add_delay(0.5, 1.0)
                        
                        with yt_dlp.YoutubeDL(detail_opts) as detail_ydl:
                            video_info = detail_ydl.extract_info(entry['url'], download=False)
                            duration = video_info.get('duration', 0)
                            title = video_info.get('title', 'Unknown')
                            
                            if i % 10 == 0:
                                print(f"Progress: {i}/{total} checked | Downloaded: {downloaded} | Failed: {failed}")
                            
                            should_download = False
                            if shorts_only:
                                should_download = duration and 0 < duration <= 60
                            else:
                                should_download = True
                            
                            if should_download:
                                print(f"\nFOUND {video_type.upper()} #{downloaded + 1}")
                                print(f"Title: {title}")
                                if duration:
                                    print(f"Duration: {duration}s")
                                print("Downloading now...")
                                
                                try:
                                    add_delay(1, 2)
                                    
                                    with yt_dlp.YoutubeDL(download_opts) as download_ydl:
                                        download_ydl.download([entry['url']])
                                    
                                    downloaded += 1
                                    print(f"Downloaded successfully!")
                                    
                                    video_data = {
                                        'url': entry['url'],
                                        'title': title,
                                        'duration': duration,
                                        'upload_date': video_info.get('upload_date', 'Unknown'),
                                        'view_count': video_info.get('view_count', 0),
                                        'id': video_info.get('id', ''),
                                        'downloaded': True
                                    }
                                    
                                    log_file = Path('downloaded_videos.json')
                                    if log_file.exists():
                                        with open(log_file, 'r') as f:
                                            log_data = json.load(f)
                                    else:
                                        log_data = []
                                    
                                    log_data.append(video_data)
                                    with open(log_file, 'w') as f:
                                        json.dump(log_data, f, indent=2)
                                    
                                except Exception as e:
                                    failed += 1
                                    error_msg = str(e).lower()
                                    if 'sign in' in error_msg or 'bot' in error_msg:
                                        print(f"Bot detection triggered during download!")
                                        print(f"Stopping to avoid further detection")
                                        break
                                    else:
                                        print(f"Download failed: {e}")
                                
                                print("-" * 40)
                        
                    except KeyboardInterrupt:
                        print(f"\nStopped by user at video {i}/{total}")
                        break
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'sign in' in error_msg or 'bot' in error_msg:
                            print(f"\nBot detection triggered at video {i}")
                            print(f"Stopping to avoid further detection")
                            break
                        continue
                
                print(f"\nSTREAMING DOWNLOAD COMPLETE!")
                print("=" * 50)
                print(f"Videos processed: {processed}/{total}")
                print(f"Downloaded: {downloaded}")
                print(f"Failed: {failed}")
                print(f"Location: {os.path.abspath(settings['output_dir'])}")
                print(f"Download log: downloaded_videos.json")
                print("=" * 50)
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'sign in' in error_msg or 'bot' in error_msg:
                    print(f"YouTube bot detection triggered!")
                    print(f"SOLUTIONS:")
                    print(f"  1. Wait 10-15 minutes before trying again")
                    print(f"  2. Use a VPN to change your IP address")
                    print(f"  3. Make sure you're logged into YouTube in Chrome")
                    print(f"  4. Try a different channel or smaller channel")
                else:
                    print(f"Error scanning channel: {e}")
                
    except KeyboardInterrupt:
        print(f"\nOperation cancelled by user")
        print(f"Downloaded {downloaded} videos before stopping")
    except Exception as e:
        print(f"Critical error: {e}")

def download_from_text_file(file_path: str, settings: Dict[str, Any]):
    try:
        import yt_dlp
        
        if not Path(file_path).exists():
            print(f"File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            links = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not links:
            print("No valid links found in file")
            return
        
        Path(settings['output_dir']).mkdir(exist_ok=True)
        
        base_opts = get_yt_dlp_options()
        cookies = try_get_cookies()
        
        if cookies:
            base_opts['cookiesfrombrowser'] = cookies
        
        download_opts = {
            **base_opts,
            'outtmpl': f"{settings['output_dir']}/%(title)s [%(id)s].%(ext)s",
            'format': settings['quality'],
            'quiet': False,
            'no_warnings': False,
            'writeinfojson': False,
            'writethumbnail': False,
        }
        
        print(f"\nDOWNLOAD FROM TEXT FILE")
        print("-" * 40)
        print(f"File: {file_path}")
        print(f"Links found: {len(links)}")
        print(f"Output: {settings['output_dir']}")
        print(f"Quality: {settings['quality']}")
        print(f"Bot bypass: {'Enabled with cookies' if cookies else 'Enabled without cookies'}")
        print("-" * 40)
        print("Starting downloads...")
        print("Press Ctrl+C to stop at any time")
        print("-" * 40)
        
        downloaded = 0
        failed = 0
        
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            for i, link in enumerate(links, 1):
                try:
                    print(f"\n[{i}/{len(links)}] Downloading: {link}")
                    
                    add_delay(1, 2)
                    ydl.download([link])
                    
                    downloaded += 1
                    print(f"Downloaded successfully!")
                    
                except KeyboardInterrupt:
                    print(f"\nStopped by user at video {i}/{len(links)}")
                    break
                except Exception as e:
                    failed += 1
                    error_msg = str(e).lower()
                    if 'sign in' in error_msg or 'bot' in error_msg:
                        print(f"Bot detection triggered!")
                        print(f"Stopping to avoid further detection")
                        break
                    else:
                        print(f"Download failed: {e}")
                
                print("-" * 40)
        
        print(f"\nDOWNLOAD COMPLETE!")
        print("=" * 50)
        print(f"Total links: {len(links)}")
        print(f"Downloaded: {downloaded}")
        print(f"Failed: {failed}")
        print(f"Location: {os.path.abspath(settings['output_dir'])}")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print(f"\nOperation cancelled by user")
        print(f"Downloaded {downloaded} videos before stopping")
    except Exception as e:
        print(f"Error: {e}")

def get_text_file_path():
    print("\nTEXT FILE INPUT")
    print("-" * 30)
    print("Enter the path to your text file with video links")
    print("Format: One URL per line")
    print("Example file content:")
    print("  https://youtube.com/watch?v=xxxxx")
    print("  https://youtube.com/watch?v=yyyyy")
    print("  https://youtube.com/shorts/zzzzz")
    print("-" * 30)
    
    while True:
        file_path = input("File path (or 'cancel' to go back): ").strip()
        
        if file_path.lower() == 'cancel':
            return None
        
        if not file_path:
            print("Please enter a file path")
            continue
        
        if not Path(file_path).exists():
            print(f"File not found: {file_path}")
            create = input("Create example file? (y/n): ").strip().lower()
            if create == 'y':
                try:
                    with open(file_path, 'w') as f:
                        f.write("# Add your YouTube video links here, one per line\n")
                        f.write("# Lines starting with # are ignored\n")
                        f.write("# Example:\n")
                        f.write("# https://youtube.com/watch?v=xxxxx\n")
                    print(f"Created example file: {file_path}")
                    print("Please edit the file and add your links, then run again")
                    return None
                except Exception as e:
                    print(f"Failed to create file: {e}")
            continue
        
        return file_path

def show_banner():
    print("\n" + "="*60)
    print("YOUTUBE VIDEO DOWNLOADER")
    print("="*60)
    print("Download shorts or all videos from any YouTube channel")
    print("="*60 + "\n")

def show_main_menu():
    print("MAIN MENU")
    print("-" * 30)
    print("1. Download shorts from channel")
    print("2. Download all videos from channel")
    print("3. Download from text file")
    print("4. View previous downloads")
    print("5. Load from saved list")
    print("6. Settings")
    print("7. Exit")
    print("-" * 30)

def get_user_choice():
    while True:
        try:
            choice = input("Enter your choice (1-7): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return int(choice)
            else:
                print("Invalid choice. Please enter 1-7.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)

def get_channel_url():
    print("\nCHANNEL INPUT")
    print("-" * 30)
    print("Enter the YouTube channel URL:")
    print("Examples:")
    print("  - https://youtube.com/@channelname")
    print("  - https://youtube.com/c/channelname")
    print("  - https://youtube.com/channel/UCxxxxxxxxx")
    print("-" * 30)
    
    while True:
        url = input("Channel URL: ").strip()
        if not url:
            print("Please enter a URL")
            continue
        
        if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
            print("Invalid YouTube URL. Please try again.")
            continue
        
        return url

def get_download_settings():
    print("\nDOWNLOAD SETTINGS")
    print("-" * 30)
    
    default_dir = "downloads"
    output_dir = input(f"Output directory (default: {default_dir}): ").strip() or default_dir
    
    print("\nVideo quality options:")
    print("1. Best available quality")
    print("2. Good quality") 
    print("3. Standard quality")
    
    while True:
        quality_choice = input("Choose quality (1-3, default: 1): ").strip() or "1"
        if quality_choice in ['1', '2', '3']:
            break
        print("Invalid choice. Please enter 1-3.")
    
    quality_map = {
        '1': 'best',
        '2': 'best',
        '3': 'worst'
    }
    
    return {
        'output_dir': output_dir,
        'quality': quality_map[quality_choice],
        'save_metadata': False,
        'save_thumbnails': False
    }

def view_previous_downloads():
    print("\nPREVIOUS DOWNLOADS")
    print("-" * 30)
    
    downloads_dir = Path("downloads")
    if not downloads_dir.exists():
        print("No downloads directory found.")
        return
    
    video_files = list(downloads_dir.glob("*.mp4")) + list(downloads_dir.glob("*.webm"))
    
    if not video_files:
        print("No downloaded videos found.")
        return
    
    print(f"Found {len(video_files)} downloaded videos:")
    for i, file in enumerate(video_files[:10], 1):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  {i}. {file.stem} ({size_mb:.1f} MB)")
    
    if len(video_files) > 10:
        print(f"  ... and {len(video_files) - 10} more")
    
    input("\nPress Enter to continue...")

def load_from_saved_list():
    print("\nLOAD FROM SAVED LIST")
    print("-" * 30)
    
    list_file = Path("downloaded_videos.json")
    if not list_file.exists():
        print("No saved video list found.")
        input("Press Enter to continue...")
        return
    
    try:
        with open(list_file, 'r') as f:
            videos = json.load(f)
        
        print(f"Found saved list with {len(videos)} videos")
        
        for video in videos[:5]:
            print(f"  - {video['title']} ({video.get('duration', 'N/A')}s)")
        
        if len(videos) > 5:
            print(f"  ... and {len(videos) - 5} more")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"Error loading saved list: {e}")
        input("Press Enter to continue...")

def main():
    if not install_yt_dlp():
        print("Failed to install required dependencies")
        return
    
    while True:
        show_banner()
        show_main_menu()
        
        choice = get_user_choice()
        
        if choice == 1:
            channel_url = get_channel_url()
            settings = get_download_settings()
            
            try:
                download_videos_streaming(channel_url, settings, shorts_only=True)
                input("\nPress Enter to continue...")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"Error: {e}")
                input("Press Enter to continue...")
        
        elif choice == 2:
            channel_url = get_channel_url()
            settings = get_download_settings()
            
            try:
                download_videos_streaming(channel_url, settings, shorts_only=False)
                input("\nPress Enter to continue...")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"Error: {e}")
                input("Press Enter to continue...")
        
        elif choice == 3:
            file_path = get_text_file_path()
            if file_path:
                settings = get_download_settings()
                try:
                    download_from_text_file(file_path, settings)
                    input("\nPress Enter to continue...")
                except KeyboardInterrupt:
                    print("\n\nOperation cancelled by user")
                    input("Press Enter to continue...")
                except Exception as e:
                    print(f"Error: {e}")
                    input("Press Enter to continue...")
        
        elif choice == 4:
            view_previous_downloads()
        
        elif choice == 5:
            load_from_saved_list()
        
        elif choice == 6:
            print("\nSETTINGS")
            print("-" * 30)
            print("Settings are configured per download session.")
            print("Future versions will include persistent settings.")
            input("Press Enter to continue...")
        
        elif choice == 7:
            print("\nThank you for using YouTube Video Downloader!")
            break

if __name__ == "__main__":
    main()
