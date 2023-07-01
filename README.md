# API Documentation

This documentation provides an overview of the available endpoints and their usage in the API.

## Base URL

The base URL for all API endpoints is `http://127.0.0.1:8000`.

## Endpoints

### 1. Root

- **Endpoint**: `/`
- **Method**: GET
- **Description**: Returns a simple "Hello World" message.
- **Example**:
    ```http
    GET / HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 2. Scrape Channel

- **Endpoint**: `/scrape_channel/`
- **Method**: GET
- **Description**: Scrapes channel information based on the provided user ID and channel username.
- **Parameters**:
    - `userID` (required): User ID
    - `channelUsername` (required): Channel Username
- **Example**:
    ```http
    GET /scrape_channel/?userID=12345&channelUsername=mychannel HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 3. Scrape High-Level Comments

- **Endpoint**: `/scrape_hlcomments/`
- **Method**: GET
- **Description**: Retrieves high-level comments for a given channel.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```http
    GET /scrape_hlcomments/?channelID=12345 HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 4. Perform Sentiment Analysis

- **Endpoint**: `/perform_sentilytics/`
- **Method**: GET
- **Description**: Performs sentiment analysis on comments for a given channel.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```http
    GET /perform_sentilytics/?channelID=12345 HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 5. Perform YouTube Ranking

- **Endpoint**: `/perform_youtube_ranker/`
- **Method**: GET
- **Description**: Initiates YouTube ranking for a specific video and keyword.
- **Parameters**:
    - `videoID` (required): Video ID
    - `keyword` (required): Keyword for ranking
- **Example**:
    ```http
    GET /perform_youtube_ranker/?videoID=12345&keyword=mykeyword HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 6. Scrape Channel and Video Statistics

- **Endpoint**: `/cvstats/`
- **Method**: GET
- **Description**: Performs channel and video statistics for a given channel.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```http
    GET /cvstats/?channelID=12345 HTTP/1.1
    Host: http://127.0.0.1:8000
    ```
    
## 7. Get Videos

- **Endpoint**: `/get_videos/`
- **Method**: GET
- **Description**: Retrieves videos by channel ID.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```http
    GET /get_videos/?channelID=12345 HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 8. Get Comments

- **Endpoint**: `/get_comments/`
- **Method**: GET
- **Description**: Retrieves comments for a specific video.
- **Parameters**:
    - `comments` (required): Comment type ("hl" for only comments or "ll" for comments with reply)
    - `videoID` (required): Video ID
    - `sentiment` (optional): Sentiment type ("positive", "negative", "neutral")
- **Example**:
    ```http
    GET /get_comments/?comments=hl&videoID=12345&sentiment=positive HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 9. Get User Requests

- **Endpoint**: `/get_user_requests/`
- **Method**: GET
- **Description**: Retrieves all user requests.
- **Parameters**:
    - `userID` (required): User ID
- **Example**:
    ```http
    GET /get_user_requests/?userID=12345 HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 10. Get Completed Works

- **Endpoint**: `/get_completed_works/`
- **Method**: GET
- **Description**: Retrieves work progress for a given channel ID.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```http
    GET /get_completed_works/?channelID=abcde HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

## 11 .Get Pending Works

- **Endpoint**: `/get_pending_works/`
- **Method**: GET
- **Description**: Retrieves pending works for a given channel ID.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```http
    GET /get_pending_works/?channelID=abcde HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

