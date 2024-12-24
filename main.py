import pandas as pd
import requests
from youtube_transcript_api import YouTubeTranscriptApi




# Function to fetch video details in batches of 50
def fetch_video_details(video_ids):
    results = []
    for i in range(0, len(video_ids), 50):
        batch_ids = ','.join(video_ids[i:i+50])
        response = requests.get(
            BASE_URL,
            params={
                'part': PARTS,
                'id': batch_ids,
                'key': API_KEY
            }
        )
        if response.status_code == 200:
            results.extend(response.json().get('items', []))
        else:
            print(f"Error {response.status_code}: {response.text}")
    return results


def get_list_of_categories(api_key):
    ## function for mapping a genre to an video category id
    ## using US for sample region code
    region_code = "US"
    ## specify the base url
    url = "https://www.googleapis.com/youtube/v3/videoCategories"
    ## specifying the parameters including part, region code and our api key
    params = {
        "part": "snippet",
        "regionCode": region_code,
        "key": api_key
    }
    ## using requests library for GET command for url
    response = requests.get(url, params=params)
    response.raise_for_status()

    ## getting a list of dictionary fro json api format
    categories = response.json().get("items", [])
    return categories

def get_video_category_id(api_key, genre_name):
    categories = get_list_of_categories(api_key)
    ## if genre name matches we use its id
    ## we cannot directly map the genre(category) name to the data so we have to first get the id of category
    for category in categories:
        if category["snippet"]["title"].lower() == genre_name.lower():
            return category["id"]
    return None

def get_video_category_from_id(api_key, category_id):
    ## function to map the video category from category id
    categories = get_list_of_categories(api_key)

    ## mapping the categories name to id
    category_map = {category["id"] : category["snippet"]["title"] for category in categories}
    category_name = category_map.get(category_id,"No Cateogry like this")
    return category_name



def videos_data(api_key, video_ids):## video_ids is string of all video id's using a "." separator
        url = "https://www.googleapis.com/youtube/v3/videos"
        ## number of videos needed for any genre
        ## specifying the parameters
        params = {
            "part": "snippet,statistics,contentDetails,topicDetails,recordingDetails",
            "id": video_ids,
            "key": api_key
        }
        ## using GET method for url using requests and also raising an error if status code is not a good one
        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json().get("items",[])

## code to get the recording location
def get_recording_location(video):
    location = video.get("recordingDetails", {}).get("location")
    if location:
        latitude = location.get("latitude", "N/A")
        longitude = location.get("longitude", "N/A")
        altitude = location.get("altitude", "N/A")
        return f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}"
    return "No location provided"

## for calculating the video duration in HH:MM:SS form
def calculate_duration(video):
    video_duration = video["contentDetails"]["duration"][2:]
    video_duration = [i for i in video_duration]
    duration = ""
    for i in video_duration:
        if i == "H":
            duration += " Hours "
        elif i == "M":
            duration += " Minutes "
        elif i == "S":
            duration += " Seconds"
        else:
            duration += i
    return duration

## for getting and downloading the captions we need youtube transcript api
def get_captions(video):
    captions = "No captions"
    try :
        transcript = YouTubeTranscriptApi.get_transcript(video["id"])
        if transcript:
            captions = " ".join([entry["text"] for entry in transcript])
    except Exception:
        return "No Captions"
    return captions

## actual main code block for getting all data related to video
def get_videos_data(api_key, genre_name):
    try:
        ## Initially tried taking the genre name and then mapping to a predefined id
        ## but it will not work for any specific sub-genre of any genre.
        ## For example, it will work for the music genre but not its sub-genres like pop, rock, jazz, etc.
        ## So instead, we used "q" for keyword-based searching in the parameters.

        ## Base URL for YouTube search
        url = "https://www.googleapis.com/youtube/v3/search"
        all_videos = []
        ## for pagination we need token of next page
        next_page_token = None
        ## the amount of videos data we need
        video_count = 500

        # Pagination to fetch multiple pages
        ## as initially it was difficult to get data of 500 videos so we use pagination
        ## to get 50 videos at a time

        ## Fetch multiple pages of video data until we have video_count(500) videos or exhaust all results
        while len(all_videos) < video_count:
            params = {
                "part": "snippet",
                "type": "video",
                "q": genre_name,
                "maxResults": 50,
                "order": "viewCount",
                "pageToken": next_page_token,
                "key": api_key,
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            videos = response.json().get("items", [])
            all_videos.extend(videos)

            ## get the next page if available or else exhaust
            next_page_token = response.json().get("nextPageToken")
            if not next_page_token:
                break
        ## Process the first video_count(here 500) video IDs for detailed data
        video_ids = [video["id"]["videoId"] for video in all_videos[:video_count]]
        detailed_videos = fetch_video_details(video_ids)

        ## fetching all required data
        data_required = []
        for video in detailed_videos:
            video_id = video["id"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_title = video["snippet"].get("title", "No Title")
            description = video["snippet"].get("description", "No Description")
            channel_title = video["snippet"].get("channelTitle", "No Channel Title")
            if video["snippet"].get("tags"):
                keyword_tags = ",".join(video["snippet"].get("tags", []))  
            else :
                keyword_tags = "No Tags"
            youtube_category = get_video_category_from_id(api_key, video["snippet"].get("categoryId", ""))
            topic_details = ", ".join(video.get("topicDetails", {}).get("topicCategories", [])) or "No Topic Details"
            video_published_at = video["snippet"]["publishedAt"].replace("T", " ").replace("Z", "")
            duration = calculate_duration(video)
            view_count = video["statistics"].get("viewCount", "0")
            comment_count = video["statistics"].get("commentCount", "0")
            caption_available = video["contentDetails"].get("caption")
            if video["contentDetails"].get("caption"):
                captions = get_captions(video)
            else:
                captions = "No captions"
            recording_location = get_recording_location(video)

            data_required.append({
                "Video URL": video_url,
                "Title": video_title,
                "Description": description,
                "Channel Title": channel_title,
                "Tags": keyword_tags,
                "Category": youtube_category,
                "Topic Details": topic_details,
                "Published At": video_published_at,
                "Duration": duration,
                "View Count": view_count,
                "Comment Count": comment_count,
                "Captions Available": caption_available,
                "Captions": captions,
                "Recording Location": recording_location,
            })

        return pd.DataFrame(data_required)

    except Exception as e:
        print(f"An error occurred: {e}")

API_KEY = "API_KEY"
GENRE_NAME = "jazz music"
OUTPUT_FILE = "youtube_analysis.csv"
## base URL for the YouTube Data API v3 for fetching video details
BASE_URL = 'https://www.googleapis.com/youtube/v3/videos'
## parts of the video data we want to retrieve:
PARTS = 'snippet,statistics,contentDetails,topicDetails,recordingDetails'

df = get_videos_data(API_KEY, GENRE_NAME)
if df.empty:
    print("Not Data to save")
else:
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print("Data successfully saved")

