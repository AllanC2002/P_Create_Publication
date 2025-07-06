# Create Publication Microservice

## Overview

This project is a backend service responsible for creating and managing publications. It allows users to post text and multimedia content, which is then stored and distributed to followers via a Redis stream. The service uses JWT for authentication.

## Folder Structure

*   **`.github/`**: Contains GitHub Actions workflows.
    *   `workflows/`: Defines CI/CD pipelines, likely for Docker image publishing (`docker-publish.yml`, `docker-publish_qa.yml`).
*   **`conections/`**: Manages connections to external data stores.
    *   `mongo.py`: Handles the connection to a MongoDB database, where publications are stored.
    *   `redis.py`: Handles the connection to a Redis instance, used for event streaming of new publications.
*   **`__pycache__/`**: Contains Python bytecode cache files. This folder is typically ignored by version control.
*   **`services/`**: Contains the business logic of the application.
    *   `functions.py`: Includes core functionalities like `create_publication` which handles the creation of new posts, validation, database interaction, and publishing events to Redis. It also includes `get_followers_list` to fetch user followers from another service.
*   **`tests/`**: Contains test scripts for the application.
    *   `route_test.py`: An integration test script that simulates a client making a request to the `/create-publication` endpoint, including authentication.
    *   `test_create_publication.py`: (File exists but content not reviewed in this plan) Likely contains unit tests for the publication creation functionality.

## Backend Design Pattern

The service appears to follow a **microservice architecture** or a **service-oriented architecture (SOA)**.
*   It's a self-contained unit focused on a specific business capability (managing publications).
*   It interacts with other services (e.g., an authentication service to validate JWTs, and a follower service via HTTP to get follower lists).
*   It uses its own database (MongoDB) and a message broker (Redis) for asynchronous communication.

## Communication Architecture

*   **Synchronous Communication (REST API):**
    *   The service exposes an HTTP POST endpoint (`/create-publication`) for creating new publications.
    *   Clients (e.g., frontend applications, other backend services) communicate with this endpoint using JSON over HTTP.
    *   It makes outbound synchronous HTTP calls to a follower service (`http://52.0.8.145:8080/followers`) to fetch data.
*   **Asynchronous Communication (Event Streaming):**
    *   Upon successful creation of a publication, an event is published to a Redis stream named `stream_user_publications`.
    *   This allows other services (e.g., a feed generation service, notification service) to consume these events and react accordingly in a decoupled manner.
*   **Authentication:**
    *   The `/create-publication` endpoint is protected and requires a JWT `Bearer` token in the `Authorization` header.

## Endpoint Instructions

### Create Publication

*   **Endpoint:** `/create-publication`
*   **Method:** `POST`
*   **Description:** Creates a new publication for the authenticated user.
*   **Headers:**
    *   `Authorization: Bearer <JWT_TOKEN>` (Required) - JWT token for user authentication.
    *   `Content-Type: application/json` (Required)
*   **Body (JSON):**
    ```json
    {
        "Text": "Your publication text content.",
        "Multimedia": {
            "image_base64": "<BASE64_ENCODED_IMAGE_STRING>",
            "content_type": "<IMAGE_CONTENT_TYPE>"
        }
    }
    ```
    *   `Text` (string, required): The textual content of the publication.
    *   `Multimedia` (object, optional): Contains multimedia data for the publication.
        *   `image_base64` (string, required if `Multimedia` is present): Base64 encoded string of the image.
        *   `content_type` (string, required if `Multimedia` is present): The MIME type of the image (e.g., `image/png`, `image/jpeg`).
*   **Success Response (201 Created):**
    ```json
    {
        "message": "Publication created",
        "publication_id": "<NEWLY_CREATED_PUBLICATION_ID>"
    }
    ```
*   **Error Responses:**
    *   **400 Bad Request:**
        *   If `Text` field is missing:
            ```json
            {
                "error": "Text field is required"
            }
            ```
        *   If `Multimedia` is present but `image_base64` or `content_type` is missing:
            ```json
            {
                "error": "Multimedia must include image_base64 and content_type"
            }
            ```
        *   If `image_base64` data is invalid:
            ```json
            {
                "error": "Invalid base64 multimedia data"
            }
            ```
    *   **401 Unauthorized:**
        *   If `Authorization` header is missing or doesn't start with `Bearer `:
            ```json
            {
                "error": "Token missing or invalid"
            }
            ```
        *   If the token contains invalid user data:
            ```json
            {
                "error": "Invalid token data"
            }
            ```
        *   If the token has expired:
            ```json
            {
                "error": "Token expired"
            }
            ```
        *   If the token is generally invalid:
            ```json
            {
                "error": "Invalid token"
            }
            ```
    *   **500 Internal Server Error:**
        *   If a database error occurs:
            ```json
            {
                "error": "Database error: <SPECIFIC_ERROR_DETAILS>"
            }
            ```
