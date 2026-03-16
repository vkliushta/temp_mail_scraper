# temp_mail_scraper

## Setup instruction

- create .env file using .env.example
- run docker compose command:

```bash
docker compose up
```

## Usage example

```python
import requests

r = requests.get("http://localhost:5000/api/email")
print(r.json())

r = requests.get("http://localhost:5000/api/inbox")
print(r.json())

r = requests.get("http://localhost:5000/api/email/<email_id>")
print(r.json())

r = requests.post("http://localhost:5000/api/email/refresh")
print(r.json())
```

## Limitations

During development, the Tempail website frequently triggered Google reCAPTCHA challenges.
Because the CAPTCHA also appeared when using a normal browser session, it was not possible to fully test the scraping workflow end-to-end.

The scraping logic and selectors were implemented based on manual inspection of the page structure and partial interactive testing, but full automated E2E verification could not be completed due to this limitation.

## Service Architecture

### 1. Flask API

The API layer is implemented using Flask and exposes endpoints for interacting with the temporary email service.

Endpoints:

* **GET /api/email**
  Returns the current temporary email address.

* **GET /api/inbox**
  Returns a list of received emails (sender, subject, timestamp, id).

* **GET /api/email/<id>**
  Returns the full content of a specific email.

* **POST /api/email/refresh**
  Generates a new temporary email address and waits until the operation completes.

The Flask application is responsible only for request handling and delegating long-running operations to background workers.

---

### 2. Background Processing (Celery)

Long-running and asynchronous tasks are handled using Celery.

Celery is responsible for:

* running the inbox watcher
* triggering email refresh
* coordinating scraping tasks

In theory, Using Celery prevents blocking the API while waiting for external web interactions(not the case for /email/refresh endpoint for now).

---

### 3. Web Scraping Layer (Playwright)

Playwright is used to automate a browser session and interact with the Tempail website.

Responsibilities:

* open the Tempail inbox page
* retrieve the generated temporary email address
* monitor the inbox for new emails
* open individual email pages
* extract sender, subject, and body content

Only **one browser session** is used to reduce resource consumption and avoid triggering anti-bot protections.

Inbox monitoring is implemented using **periodic polling of the DOM** rather than MutationObserver.
This approach was chosen because the Tempail page updates dynamically and polling is more reliable and easier to maintain.

---

### 4. Database (PostgreSQL)

PostgreSQL stores:

* temporary email addresses
* retrieved email metadata
* full email content

Data is modeled with two tables:

* **EmailAddress** – stores generated temporary addresses
* **Email** – stores email messages associated with an address

Alembic is used for database migrations.

---

## Docker Architecture

The system runs using Docker Compose with the following services:

* **app** – Flask API server
* **celery** – Celery worker executing background tasks
* **redis** - Redis as Celery message broker
* **db** – PostgreSQL database

This separation ensures that API requests, background tasks, and database operations run independently.

---

## Key Design Decisions

### Single Playwright Session

Only one browser instance is used for scraping.

---

### Background Email Watcher

A long-running watcher process continuously checks the inbox for new emails and stores them in the database.
This allows the API to return email data instantly without waiting for scraping operations.

---

### Polling Instead of DOM Observers

The inbox is monitored by periodically checking the DOM for new email rows.

Reasons for this approach:

* simpler implementation
* more stable with dynamically updated pages
* avoids race conditions with injected JavaScript
* easier recovery if the page reloads

---

## High-Level Flow

1. The watcher opens the Tempail inbox page.
2. The generated temporary email address is extracted.
3. The watcher periodically checks the inbox for new emails.
4. When a new email appears:

   * the email page is opened
   * the email body is extracted
   * the email is stored in the database
5. The API reads email data directly from the database.
