import tweepy #twitter library
import typer #CLI
from dotenv import load_dotenv #for loading the .env file
from requests.exceptions import ConnectionError #for handling connection errors
import os, random, time, datetime

load_dotenv()

app = typer.Typer()

#twitter api credentials
def twitter_credentials():
    return tweepy.Client(
        bearer_token=os.getenv('BEARER_TOKEN'),
        consumer_key=os.getenv('API_KEY'),
        consumer_secret=os.getenv('API_SECRET'),
        access_token=os.getenv('ACCESS_TOKEN'),
        access_token_secret=os.getenv('ACCESS_SECRET')
    )

client = twitter_credentials()

app = typer.Typer()

def file_operation (filename = 'tweets.txt', mode = 'r', messages=None):
    """Loading and Saving messages to a file by performing read and write operations
    """
    try:
        with open (filename, mode) as f:
            if mode == 'r':
                return [line.strip() for line in f if line.strip()]
            elif mode == 'w':
                for message in messages:
                    f.write(f"{message}\n")
                typer.secho(f"Message has been saved to {filename} successfully", fg=typer.colors.GREEN)
    except FileNotFoundError:
        typer.secho (f"Error: {filename} not found", err=True, fg=typer.colors.RED)
        return[]

def post_tweet(message, max_retries=3):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_tweet = f"{message} (Posted at: {timestamp})"
    
    for attempt in range(max_retries):
        try:
            global client
            client = twitter_credentials()  # Reconnect before each attempt
            client.create_tweet(text=full_tweet)
            typer.secho(f"Tweet has been posted: {full_tweet}", fg=typer.colors.GREEN)
            return
        except (tweepy.TweepyException, ConnectionError) as e:
            if attempt < max_retries - 1:
                typer.secho(f"Error occurred: {e}. Retrying in 5 seconds...", fg=typer.colors.YELLOW)
                time.sleep(5)
            else:
                typer.secho(f"Failed to post tweet after {max_retries} attempts: {e}", err=True, fg=typer.colors.RED)

def run_bot(interval=3600):
    try:
        while True:
            messages = file_operation()
            if messages:
                message = random.choice(messages)
                post_tweet(message)
            else:
                typer.secho("No tweets available to post.", err=True, fg=typer.colors.RED)
            
            # Wait for the interval, but periodically check if we're still connected
            start_time = time.time()
            while time.time() - start_time < interval:
                time.sleep(min(300, interval))  # Check every 5 minutes or at the end of the interval
                try:
                    global client
                    client = twitter_credentials()  # Attempt to reconnect
                    client.get_me()  # Simple API call to check connection
                except Exception as e:
                    typer.secho(f"Connection check failed: {e}. Will retry on next tweet.", fg=typer.colors.YELLOW)
                
            typer.secho(f"Waiting completed. Preparing to post next tweet.", fg=typer.colors.BLUE)
    except KeyboardInterrupt:
        typer.secho("The bot has stopped running.", fg=typer.colors.RED)

@app.command()    
def add (message: str):
    """add tweets to the list

    Args:
        message (str)
    """
    messages = file_operation()
    messages.append(message)
    file_operation(mode='w', messages=messages)
    typer.secho(f"Message added: {message}", fg=typer.colors.GREEN)

@app.command()
def rmv(index: int):
    """remove tweets from the list based on their index number

    Args:
        index (int)
    """
    messages = file_operation()
    if 0 <= index < len(messages):
        removed_message = messages.pop(index)
        file_operation(mode='w', messages=messages)
        typer.secho(f"Message removed: {removed_message}", fg=typer.colors.GREEN)
    else:
        typer.secho("The index is invalid, no message was removed", err=True, fg=typer.colors.RED)

@app.command()
def lst():
    """list messages and their indices
    """
    for i, message in enumerate(file_operation()):
        typer.secho(f"{i}: {message}", fg=typer.colors.BLUE)

@app.command()
def edit(index: int, new_message: str):
    """edit messages based on their index number
    """
    messages = file_operation()
    if 0 <= index < len(messages):
        old_message = messages[index]
        messages[index] = new_message
        file_operation(mode='w', messages=messages)
        typer.secho(f"Message edited: {old_message} -> {new_message}", fg=typer.colors.GREEN)
    else:
        typer.secho("The index is invalid, no message was edited", err=True, fg=typer.colors.RED)

@app.command()
def run():
    """runs the bot to tweet messages at a given interval
    """
    typer.secho("The bot is running... Press Ctrl+C to stop.", fg=typer.colors.BLUE)
    run_bot()

@app.command()
def main():
    """this is the main program that asks the user for command prompts
    """
    typer.secho("Welcome to the Twitter Bot!", fg=typer.colors.BLUE)
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
            index = typer.prompt ("Enter the index of the tweet to edit", type=int)
            new_message = typer.prompt ("Enter the new tweet")
            edit(index, new_message)
        elif command == 'quit':
            typer.secho("Exiting the bot.", fg=typer.colors.YELLOW)
            break
        else:
            typer.secho("Invalid command. Please try again.", err=True, fg=typer.colors.RED)

if __name__ == "__main__":
    app()


