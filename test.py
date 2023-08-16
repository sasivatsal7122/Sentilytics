import os
import googleapiclient.discovery
from googleapiclient.errors import HttpError
#hfjsdfkjsjk
def get_channel_statistics(api_key, channel_id):
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    try:
        response = youtube.channels().list(
            part='statistics',
            id=channel_id
        ).execute()
        print(response)
        items = response.get('items', [])
        if items:
            channel_data = items[0]['statistics']
            view_count = channel_data.get('viewCount', 0)
            video_count = channel_data.get('videoCount', 0)
            subscriber_count = channel_data.get('subscriberCount', 0)

            print(f'View Count: {view_count}')
            print(f'Video Count: {video_count}')
            print(f'Subscriber Count: {subscriber_count}')
        else:
            print('Channel not found or no statistics available.')

    except HttpError as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    API_KEY = "AIzaSyC6APVUSvLKRhNMyp5P9eRu56G4i-P2idg"
    CHANNEL_ID = "UCfdNM3NAhaBOXCafH7krzrA"
    get_channel_statistics(API_KEY, CHANNEL_ID)
