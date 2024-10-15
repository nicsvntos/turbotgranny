import tweepy,typer,os,random,datetime,time
from dotenv import load_dotenv

load_dotenv()
app = typer.Typer()

def twitter_credentials():
    return tweepy.Client(
        bearer_token=os.getenv('BEARER_TOKEN'),
        consumer_key=os.getenv('API_KEY'),
        consumer_secret=os.getenv('API_SECRET'),
        access_token=os.getenv('ACCESS_TOKEN'),
        access_token_secret=os.getenv('ACCESS_SECRET')
    )

client = twitter_credentials()

def file_operation(filename='tweets.txt', mode='r', messages=None):
    try:
        with open(filename, mode) as f:
            if mode == 'r':
                return [line.strip() for line in f if line.strip()]
            elif mode == 'w':
                for message in messages:
                    f.write(f"{message}\n")
                typer.secho(f"Message has been saved to {filename} successfully", fg=typer.colors.GREEN)
    except FileNotFoundError:
        typer.secho(f"Error: {filename} not found", err=True, fg=typer.colors.RED)
        return []

def post_tweet(max_retries=3, retry_delay=15*60):  # 15 minutes delay
    messages = file_operation()
    if not messages:
        typer.secho("No tweets available to post.", fg=typer.colors.RED)
        return

    message = random.choice(messages)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_tweet = f"{message} (Posted at: {timestamp})"

    for attempt in range(max_retries):
        try:
            global client
            client = twitter_credentials()  # Reconnect before each attempt
            client.create_tweet(text=full_tweet)
            typer.secho(f"Tweet has been posted: {full_tweet}", fg=typer.colors.GREEN)
            return
        except tweepy.TooManyRequests as e:
            if attempt < max_retries - 1:
                typer.secho(f"Rate limit hit. Waiting for {retry_delay/60} minutes before retrying...", fg=typer.colors.YELLOW)
                time.sleep(retry_delay)
            else:
                typer.secho(f"Failed to post tweet after {max_retries} attempts due to rate limiting.", fg=typer.colors.RED)
        except tweepy.TweepyException as e:
            typer.secho(f"Failed to post tweet: {e}", fg=typer.colors.RED)
            if attempt < max_retries - 1:
                typer.secho(f"Retrying in {retry_delay/60} minutes...", fg=typer.colors.YELLOW)
                time.sleep(retry_delay)
            else:
                typer.secho(f"Failed to post tweet after {max_retries} attempts.", fg=typer.colors.RED)

@app.command()    
def add(message: str):
    """Add a tweet to the list"""
    messages = file_operation()
    messages.append(message)
    file_operation(mode='w', messages=messages)
    typer.secho(f"Message added: {message}", fg=typer.colors.GREEN)

@app.command()
def rmv(index: int):
    """Remove a tweet from the list based on its index number"""
    messages = file_operation()
    if 0 <= index < len(messages):
        removed_message = messages.pop(index)
        file_operation(mode='w', messages=messages)
        typer.secho(f"Message removed: {removed_message}", fg=typer.colors.GREEN)
    else:
        typer.secho("The index is invalid, no message was removed", fg=typer.colors.RED)

@app.command()
def lst():
    """List messages and their indices"""
    for i, message in enumerate(file_operation()):
        typer.secho(f"{i}: {message}", fg=typer.colors.BLUE)

@app.command()
def edit(index: int, new_message: str):
    """Edit a message based on its index number"""
    messages = file_operation()
    if 0 <= index < len(messages):
        old_message = messages[index]
        messages[index] = new_message
        file_operation(mode='w', messages=messages)
        typer.secho(f"Message edited: {old_message} -> {new_message}", fg=typer.colors.GREEN)
    else:
        typer.secho("The index is invalid, no message was edited", fg=typer.colors.RED)

@app.command()
def tweet():
    """Post a single tweet"""
    post_tweet()

if __name__ == "__main__":
    app()
