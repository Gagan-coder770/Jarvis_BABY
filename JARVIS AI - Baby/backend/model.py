import cohere
from dotenv import dotenv_values
from rich import print
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache

# Load environment
env_vars = dotenv_values(".env")
co = cohere.Client(api_key=env_vars["CohereAPIKey"])

# Define the preamble for classifying queries
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write an application and open it in notepad'.  
*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'general ( query )' if the query can be answered by a conversational AI model and does not require real-time data.  
  Examples:
  - 'who was Albert Einstein?' → 'general who was Albert Einstein?'
  - 'how can I study more effectively?' → 'general how can I study more effectively?'
  - 'what is Python programming language?' → 'general what is Python programming language?'
  - 'who is the CEO of Google?' → 'general who is the CEO of Google?'
  - 'what is climate change?' → 'general what is climate change?'
  - 'who is he?' (if the query lacks context) → 'general who is he?'
  - 'what’s the time?' → 'general what’s the time?'

-> Respond with 'realtime ( query )' if the query requires **up-to-date** or **real-time** information.  
  Examples:
  - 'who is the current US president?' → 'realtime who is the current US president?'
  - 'what is the latest iPhone model?' → 'realtime what is the latest iPhone model?'
  - 'tell me about Facebook’s recent update.' → 'realtime tell me about Facebook’s recent update.'
  - 'who is the top scorer in today’s football match?' → 'realtime who is the top scorer in today’s football match?'
  - 'what is today’s news?' → 'realtime what is today’s news?'
  - 'who won the last F1 race?' → 'realtime who won the last F1 race?'

-> Respond with 'open (application name or website name)' if the query asks to open any application.  
  Examples:
  - 'open Facebook' → 'open Facebook'
  - 'open Telegram and YouTube' → 'open Telegram, open YouTube'

-> Respond with 'close (application name)' if the query asks to close any application.  
  Examples:
  - 'close Notepad' → 'close Notepad'
  - 'close Chrome and Spotify' → 'close Chrome, close Spotify'

-> Respond with 'play (song name)' if the query asks to play a song.  
  Examples:
  - 'play Let Her Go by Passenger' → 'play Let Her Go by Passenger'
  - 'play Afsanay by Young Stunners' → 'play Afsanay by Young Stunners'

-> Respond with 'generate image (image prompt)' if the query requests an image generation.  
  Examples:
  - 'generate image of a lion' → 'generate image of a lion'
  - 'generate image of a futuristic city' → 'generate image of a futuristic city'

-> Respond with 'reminder (datetime with message)' if the query requests a reminder.  
  Examples:
  - 'set a reminder for my meeting at 9:00 PM on 25th June' → 'reminder 9:00 PM 25th June meeting'

-> Respond with 'system (task name)' if the query asks to adjust system settings.  
  Examples:
  - 'mute volume' → 'system mute volume'
  - 'increase brightness' → 'system increase brightness'

-> Respond with 'content (topic)' if the query asks to generate any type of content.  
  Examples:
  - 'write an email about job application' → 'content job application email'
  - 'write a Python script for web scraping' → 'content Python script for web scraping'

-> Respond with 'google search (topic)' if the query asks to search something on Google.  
  Examples:
  - 'search AI trends on Google' → 'google search AI trends'
  - 'find the best laptops for coding' → 'google search best laptops for coding'

-> Respond with 'youtube search (topic)' if the query asks to search something on YouTube.  
  Examples:
  - 'find tutorials for Python Django framework' → 'youtube search Python Django framework'
  - 'search for latest movie trailers' → 'youtube search latest movie trailers'

*** If the query asks for multiple actions, respond accordingly. ***  
  Examples:
  - 'open Facebook and close Telegram' → 'open Facebook, close Telegram'
  - 'set a reminder and play a song' → 'reminder (time and message), play (song name)'

*** If you can't decide the kind of query, or if the task is not listed above, respond with 'general (query)'. ***  
"""

# Retry logic for API calls
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def classify_query(query: str) -> str:
    """
    Classifies the query as a general query, automation query, or real-time query.
    """
    try:
        # Use Cohere Chat API instead of generate
        response = co.chat(
            model='command-r-plus',
            message=f"{preamble}\nQuery: {query}\nCategory:",
            temperature=0.3,  # Lower temperature for more deterministic output
        )
        raw = response.text.strip()
        return raw.split("\n")[0]  # Take the first line only
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        return "error"

# Caching layer
class QueryClassifier:
    @lru_cache(maxsize=1000)
    def classify(self, query: str) -> str:
        return classify_query(query)

# Main loop
if __name__ == "__main__":
    classifier = QueryClassifier()
    print("[green]Welcome![/green]")
    while True:
        user_input = input("Enter query: ").strip().lower()
        if user_input in {"exit", "quit", "bye"}:
            break
        print(f"Classification: {classifier.classify(user_input)}")

# Function to classify the query
def classify_query(query: str) -> str:
    """
    Classifies the query as a general query, automation query, or realtime query.
    """
    try:
        # Use Cohere Chat API instead of generate
        response = co.chat(
            model='command-r-plus',
            message=f"{preamble}\nQuery: {query}\nCategory:",
            temperature=0.7,  # Control the creativity of the response
        )
        return response.text.strip()

    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        return "Error: Unable to classify the query."

# Main script
if __name__ == "__main__":
    print("[bold green]Welcome to the Genius AI Query Classifier![/bold green]")
    while True:
        user_input = input("\n[bold yellow]Enter your query:[/bold yellow] ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("[bold cyan]Goodbye![/bold cyan] Thanks for using the Genius AI.")
            break

        classification = classify_query(user_input)
        print(f"[bold blue]Classification:[/bold blue] {classification}")

class FirstLayerDMM:
    def __init__(self):
        self.cache = {}  # Store previous queries to save API calls

    def __call__(self, query):
        if query in self.cache:
            return self.cache[query]
        
        classification = classify_query(query)
        self.cache[query] = classification  # Store result
        return classification
