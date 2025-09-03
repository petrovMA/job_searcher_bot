# job_searcher_bot

This bot will filter all incoming job offers using AI prompt

## Running the HTTP service

The project exposes an HTTP service that scrapes the [easy_qa_jobs](https://t.me/easy_qa_jobs) Telegram channel and returns job posts for a specified duration.

### Docker Compose

1. Ensure Docker and Docker Compose are installed.
2. Set the `API_TOKEN` environment variable (defaults to `secret`).
3. Build and start the service:

   ```bash
   docker-compose up --build
   ```

4. Query the service:

   ```bash
   curl -H "Authorization: Bearer secret" "http://localhost:8000/jobs?duration=3%20days"
   ```

### Local execution

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:

   ```bash
   API_TOKEN=secret uvicorn app.main:app --reload
   ```

3. Query the service as shown above.
