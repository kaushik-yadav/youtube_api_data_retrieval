# YouTube Data Fetcher and Analyzer

This Python program allows you to fetch detailed information about YouTube videos based on a specific genre. It collects metadata, statistics, captions, and location data for the videos using the YouTube Data API v3. The program also handles pagination to fetch up to 500 videos and saves the results in a CSV file for further analysis.

## Features

- Fetches video details such as title, description, tags, category, and more.
- Retrieves statistics like view count, comment count, and video duration.
- Downloads captions (if available) using the `youtube-transcript-api`.
- Extracts recording location data (latitude, longitude, and altitude).
- Handles pagination to retrieve data for up to 500 videos.
- Saves the collected data into a CSV file.

## Requirements

Make sure to install the necessary Python libraries by running the following command:

```bash
pip install requests pandas youtube-transcript-api
