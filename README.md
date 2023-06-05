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

### 2. Scrape Channel

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

### 3. Get Latest 20

- **Endpoint**: `/get_latest20/`
- **Method**: GET
- **Description**: Retrieves the latest 20 records.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```http
    GET /get_latest20/?channelID=abcde HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

### 4. Get High-Level Comments

- **Endpoint**: `/get_hlcomments/`
- **Method**: GET
- **Description**: Retrieves high-level comments for a specific video.
- **Parameters**:
    - `videoID` (required): Video ID
- **Example**:
    ```http
    GET /get_hlcomments/?videoID=12345 HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

### 5. Get Low-Level Comments

- **Endpoint**: `/get_llcomments/`
- **Method**: GET
- **Description**: Retrieves low-level comments for a specific video.
- **Parameters**:
    - `videoID` (required): Video ID
- **Example**:
    ```http
    GET /get_llcomments/?videoID=12345 HTTP/1.1
    Host: http://127.0.0.1:8000
    ```

### 6. Perform Sentilytics

- **Endpoint**: `/perform_sentilytics/`
- **Method**: GET
- **Description**: Performs sentiment analysis on comments for a specific video.
- **Parameters**:
    - `videoID` (required): Video ID
- **Example**:
    ```http
    GET /perform_sentilytics/?videoID=12345 HTTP/1.1
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
