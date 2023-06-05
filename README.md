# API Documentation

This documentation provides an overview of the available endpoints and their usage in the API.

## Base URL

The base URL for all API endpoints is `http://your-api-domain.com`.

## Endpoints

### 1. Root

- **Endpoint**: `/`
- **Method**: GET
- **Description**: Returns a simple "Hello World" message.
- **Example**:
    ```
    GET / HTTP/1.1
    Host: your-api-domain.com
    ```

### 2. Scrape Channel

- **Endpoint**: `/scrape_channel/`
- **Method**: GET
- **Description**: Scrapes channel information based on the provided user ID and channel username.
- **Parameters**:
    - `userID` (required): User ID
    - `channelUsername` (required): Channel Username
- **Example**:
    ```
    GET /scrape_channel/?userID=12345&channelUsername=mychannel HTTP/1.1
    Host: your-api-domain.com
    ```

### 3. Get Latest 20

- **Endpoint**: `/get_latest20/`
- **Method**: GET
- **Description**: Retrieves the latest 20 records.
- **Parameters**:
    - `channelID` (required): Channel ID
- **Example**:
    ```
    GET /get_latest20/?channelID=abcde HTTP/1.1
    Host: your-api-domain.com
    ```

### 4. Get High-Level Comments

- **Endpoint**: `/get_hlcomments/`
- **Method**: GET
- **Description**: Retrieves high-level comments for a specific video.
- **Parameters**:
    - `videoID` (required): Video ID
- **Example**:
    ```
    GET /get_hlcomments/?videoID=12345 HTTP/1.1
    Host: your-api-domain.com
    ```

### 5. Get Low-Level Comments

- **Endpoint**: `/get_llcomments/`
- **Method**: GET
- **Description**: Retrieves low-level comments for a specific video.
- **Parameters**:
    - `videoID` (required): Video ID
- **Example**:
    ```
    GET /get_llcomments/?videoID=12345 HTTP/1.1
    Host: your-api-domain.com
    ```

### 6. Perform Sentilytics

- **Endpoint**: `/perform_sentilytics/`
- **Method**: GET
- **Description**: Performs sentiment analysis on comments for a specific video.
- **Parameters**:
    - `videoID` (required): Video ID
- **Example**:
    ```
    GET /perform_sentilytics/?videoID=12345 HTTP/1.1
    Host: your-api-domain.com
    ```

Please note that the above examples are for illustrative purposes, and you should replace the values with actual data when making API requests.


