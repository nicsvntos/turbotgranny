import tweepy #twitter library
import tweepy.errors
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
    try:
        while True:
            messages = load_message()
            if messages:
                message = random.choice(messages)
                post_tweet(message)
            else:
                typer.secho("There are no tweets available to post.", err=True, fg=typer.colors.RED)
            typer.secho(f"Waiting for {interval} seconds before next tweet", fg=typer.colors.BLUE)
            time.sleep(interval)
    except KeyboardInterrupt:
        typer.secho("The bot has stopped running", fg=typer.colors.RED)
    

#test rate limit
@app.command()
def test():
    """test function to hit the rate limit
    """
    count = 0
    start_time = time.time()
    try:
        while True:
            message = f"Test tweet {count}"
            post_tweet(message)
            count += 1
            time.sleep(10)
    except tweepy.errors.TooManyRequests as e:
        elapsed_time = time.time() - start_time
        typer.secho(f"Rate limit hit after {count} tweets in {elapsed_time:.2f} seconds", fg=typer.colors.YELLOW)
        typer.secho(f"Error message: {str(e)}", fg=typer.colors.RED)

def add (message: str):
    """add tweets to the list

    Args:
        message (str)
    """
    messages = load_message()
    messages.append(message)
    save_message(messages)
    typer.secho(f"Message added: {message}", fg=typer.colors.GREEN)


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


def lst():
    """list messages and their indices
    """
    messages = load_message()
    for i, message in enumerate(messages):
        typer.secho(f"{i}: {message}")

def edit(index: int, new_message: str):
    """edit messages based on their index number
    """
    messages = load_message()
    if 0 <= index < len(messages):
        old_message = messages[index]
        messages[index] = new_message
        save_message(messages)
        typer.secho(f"Message edited: {old_message} -> {new_message}", fg=typer.colors.GREEN)
    else:
        typer.secho("The index is invalid, no message was edited", err=True, fg=typer.colors.RED)


def run():
    """runs the bot to tweet messages at a given interval
    """
    typer.secho("The bot is running... Press Ctrl+C to stop.", fg=typer.colors.BLUE)
    run_bot()


def main():
    """this is the main program that asks the user for command prompts
    """
    typer.secho("Welcome to the Twitter Bot!", fg=typer.colors.GREEN)
    typer.secho("Available commands: add, rmv, lst, edit, run, quit", fg=typer.colors.BLUE)
    while True:
        command = typer.prompt ("Enter a command")
        
        if command == 'add':
            message = typer.prompt ("Enter a tweet")
            add(message)
        elif command == 'rmv':
            index = typer.prompt ("Enter the index of the tweet to remove", type=int)
            rmv(index)
        elif command == 'lst':
            lst()
        elif command == 'run':
            run()
        elif command == 'edit':
            index = typer.prompt ("Enter the index of the tweet to edit:", type=int)
            new_message = typer.prompt ("Enter the new tweet")
            edit(index, new_message)
        elif command == 'test':
            test()
        elif command == 'quit':
            typer.secho("Exiting the bot.", fg=typer.colors.YELLOW)
            break
        else:
            typer.secho("Invalid command. Please try again.", err=True, fg=typer.colors.RED)

if __name__ == "__main__":
    main()


