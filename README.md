# InternetWhisper: Conversational AI Chatbot with Internet Access

## Project Description

Based in You.com and Google's Bard, this project is a conversational generative artificial intelligence chatbot that can access the internet. It is designed to provide real-time information and engage in conversations with users. To enhance its performance, the chatbot utilizes a Redis vector database (Redis Vector DB cache) to store previously retrieved information, reducing the need to query the internet for the same data repeatedly. It also leverages the Google Search API for website querying.


## Getting Started

Follow these steps to run the chatbot locally on your machine:

1. **Set Up Environment Variables**:

    - Create a `.env` file by copying the provided `.env.example`. This file should contain the following environment variables:
        - `HEADER_ACCEPT_ENCODING`: Set it to "gzip".
        - `HEADER_USER_AGENT`: Use a user agent string, e.g., "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 (gzip)".
        - `GOOGLE_API_HOST`: Set the Google API host to "https://www.googleapis.com/customsearch/v1?".
        - `GOOGLE_FIELDS`: Define the fields you want to retrieve from Google. Example: "items(title, displayLink, link, snippet,pagemap/cse_thumbnail)".
        - `GOOGLE_API_KEY`: Obtain a Google API key from [Google Custom Search](https://developers.google.com/custom-search/v1/overview).
        - `GOOGLE_CX`: You can get your Custom Search Engine (CX) ID from the same Google Custom Search page.
        - `OPENAI_API_KEY`: Obtain an API key from [OpenAI](https://openai.com/blog/openai-api).

2. **Build and Run the Application**:

    - Open your terminal and navigate to the project directory.
    - Run the following commands to build and start the application using Docker Compose:

    ```bash
    docker-compose build
    docker-compose up
    ```

3. **Choose Your Scraper Class**:

    The project includes two scraper classes:

    - `ScraperLocal`: Uses aiohttp for web scraping (default).
    - `ScraperRemote`: Utilizes Playwright in a separate replicated container for more complex JavaScript rendering.

    To switch between scraper classes, modify the `orchestrator/main.py` file and uncomment the appropriate scraper and lb-scraper services in the `docker-compose.yml`.

4. **Select Your Embeddings Class**:

    Two embeddings classes are available:

    - `OpenAIEmbeddings`: The default option, using OpenAI's embeddings.
    - `RemoteEmbeddings`: Utilizes the "multi-qa-MiniLM-L6-cos-v1" model in a separate container. Please note that this is CPU/GPU intensive and may slow down the application without adequate resources.

    To use a specific embeddings class, edit the `orchestrator/main.py` file and uncomment the embeddings service in the `docker-compose.yml`.

5. **Access the Chatbot**:

    After running the application, open your web browser and navigate to [http://localhost:8501/](http://localhost:8501/) to interact with the chatbot.

## Notes

- This project offers flexibility in choosing between different scraper and embeddings classes to suit your requirements.
- Be aware that selecting the `ScraperRemote` or `RemoteEmbeddings` classes may increase resource consumption and affect the application's performance.

Feel free to explore and modify this conversational AI chatbot for your specific use case. Enjoy chatting with your new AI companion!
