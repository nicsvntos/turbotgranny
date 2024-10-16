import tweepy, typer, os, random, time, datetime, requests
from dotenv import load_dotenv

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

def file_operation (filename = 'tweets.txt', mode = 'r', messages=None):
    """loading and saving messages to a file"""
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

def check_internet():
    """checking internet connection"""
    try:
        requests.get("https://api.twitter.com", timeout=5)
        return True
    except requests.RequestException:
        return False
    
def post_tweet(message, max_attempts=3):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_tweet = f"{message} (Posted at: {timestamp})"
    for attempt in range(max_attempts):
        if not check_internet():
            typer.secho("No internet connection. Retrying in 30 seconds...", fg=typer.colors.YELLOW)
            time.sleep(30)
            if attempt == max_attempts - 1:
                typer.secho(f"Failed to connect to the internet after {max_attempts} attempts", fg=typer.colors.RED)
            continue
        try:
            global client
            client = twitter_credentials()  # Attempt to reconnect
            client.create_tweet(text=full_tweet)
            typer.secho(f"Tweet has been posted: {full_tweet}", fg=typer.colors.GREEN)
            return
        except (tweepy.TweepyException) as e:
            if attempt < max_attempts - 1:
                typer.secho(f"Error occurred: {e}. Retrying in 5 seconds...", fg=typer.colors.YELLOW)
                time.sleep(5)
            else:
                typer.secho(f"Failed to post tweet after {max_attempts} attempts: {e}", err=True, fg=typer.colors.RED)
    typer.secho ("Failed to post tweet due to errors/connection issues. Press Ctrl+C to exit.", err=True, fg=typer.colors.RED)

def run_bot(interval=3600):
    """handling rate limits and tweet selection"""
    try:
        while True:
            messages = file_operation()
            if messages:
                message = random.choice(messages)
                post_tweet(message)
            else:
                typer.secho("No tweets available to post.", err=True, fg=typer.colors.RED)
                
            # Wait for the interval, only check connection once
            time.sleep(interval)
            try:
                global client
                client = twitter_credentials()  # Attempt to reconnect
                client.get_me()  # Simple API call to check connection
            except tweepy.TooManyRequests as e:
                typer.secho(f"Rate limit hit: {e}. Pausing for 15 minutes.", fg=typer.colors.YELLOW)
                time.sleep(15*60) 
            except tweepy.TweepyException as e:
                typer.secho(f"Connection check failed: {e}.", fg=typer.colors.YELLOW)

            typer.secho(f"Preparing to post next tweet.", fg=typer.colors.BLUE)
    except KeyboardInterrupt:
        typer.secho("The bot has stopped running.", fg=typer.colors.RED)

@app.command()    
def add (message: str):
    """add tweets to the list"""
    messages = file_operation()
    messages.append(message)
    file_operation(mode='w', messages=messages)
    typer.secho(f"Message added: {message}", fg=typer.colors.GREEN)

@app.command()
def rmv(index: int):
    """remove tweets from the list based on their index number"""
    messages = file_operation()
    if 0 <= index < len(messages):
        removed_message = messages.pop(index)
        file_operation(mode='w', messages=messages)
        typer.secho(f"Message removed: {removed_message}", fg=typer.colors.GREEN)
    else:
        typer.secho("The index is invalid, no message was removed", err=True, fg=typer.colors.RED)

@app.command()
def lst():
    """list messages and their indices"""
    for i, message in enumerate(file_operation()):
        typer.secho(f"{i}: {message}", fg=typer.colors.BLUE)

@app.command()
def edit(index: int, new_message: str):
    """edit messages based on their index number"""
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
    """run the bot to post tweets"""
    typer.secho("Bot running... Press Ctrl+C to stop/exit.", fg=typer.colors.BLUE)
    run_bot()


@app.command()
def main():
    """Main program loop"""
    typer.secho("Welcome to the Twitter Bot!", fg=typer.colors.BLUE)
    typer.secho("Commands: add, rmv, lst, edit, run, quit", fg=typer.colors.BLUE)
    while True:
        command = typer.prompt("Enter a command").lower()
        if command == 'add':
            add(typer.prompt("Enter tweet"))
        elif command == 'rmv':
            rmv(typer.prompt("Enter index to remove", type=int))
        elif command == 'lst':
            lst()
        elif command == 'edit':
            edit(typer.prompt("Enter index to edit", type=int), typer.prompt("Enter new tweet"))
        elif command == 'run':
            run()
        elif command == 'quit':
            typer.secho("Exiting bot.", fg=typer.colors.YELLOW)
            break
        else:
            typer.secho("Invalid command.", err=True, fg=typer.colors.RED)

if __name__ == "__main__":
    app()