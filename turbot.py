import tweepy #twitter library
import typer #CLI
from dotenv import load_dotenv #for loading the .env file
import os, random, time, datetime

load_dotenv()

#twitter api credentials
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

client = tweepy.Client(BEARER_TOKEN, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

#authenticate to twitter
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

app = typer.Typer()

def load_message(filename='tweets.txt'):
    """Loads the messages from the file"""
    try:
        with open (filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        typer.secho(f"Error {filename} not found.", err=True, fg=typer.colors.RED)
        return []
    

def save_message(messages, filename='tweets.txt'):
    """Saves the messages to the file
    Args:
        filename (str, optional)
    """
    with open (filename, 'w') as f:
        for message in messages:
            f.write(f"{message}\n")
        typer.secho(f"Message saved to {filename} successfully", fg=typer.colors.GREEN)


def post_tweet(message):
    """Posts the message to twitter including a timestamp, along with handling rate limits
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_tweet = f"{message} (Posted at: {timestamp})"

    try:
        tweet = client.create_tweet(text=full_tweet)
        typer.secho(f"Tweet has been posted: {full_tweet}", fg=typer.colors.GREEN)
    except tweepy.TweepyException as e:
            typer.secho(f"An error occurred: {e}", err=True, fg=typer.colors.RED)

def run_bot(interval=3600):
    while True:
        messages = load_message()
        if messages:
            message = random.choice(messages)
            post_tweet(message)
        else:
            typer.secho("There are no tweets available to post.", err=True, fg=typer.colors.RED)
        typer.secho(f"Waiting for {interval} seconds before next tweet", fg=typer.colors.BLUE)
        time.sleep(interval)

#functions listed down below are command functions
@app.command()
def add (message: str):
    """add tweets to the list

    Args:
        message (str)
    """
    messages = load_message()
    messages.append(message)
    save_message(messages)
    typer.secho(f"Message added: {message}", fg=typer.colors.GREEN)

@app.command()
def rmv(index: int):
    """remove tweets from the list based on their index number

    Args:
        index (int)
    """
    messages = load_message()
    if 0 <= index < len(messages):
        removed_message = messages.pop(index)
        save_message(messages)
        typer.secho(f"Message removed: {removed_message}", fg=typer.colors.GREEN)
    else:
        typer.secho("The index is invalid, no message was removed", err=True, fg=typer.colors.RED)

@app.command()
def lst():
    """list messages and their indices
    """
    messages = load_message()
    for i, message in enumerate(messages):
        typer.secho(f"{i}: {message}")

@app.command()
def run():
    """runs the bot to tweet messages at a given interval
    """
    typer.secho("The bot is running... Press Ctrl+C to stop.", fg=typer.colors.BLUE)
    run_bot()

if __name__ == "__main__":
    app()


