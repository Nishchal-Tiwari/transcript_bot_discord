import discord
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
import os
import json
import asyncio
from kombu import Connection, Exchange, Queue

# Load environment variables
load_dotenv()
# The code to rewrite
redis_url = "redis://localhost:6379/0"

exchange = Exchange("example_exchange", type="direct")
queue = Queue("example_queue", exchange, routing_key="example_key")
# Initialize bot
intents = discord.Intents.default()
intents.members = True  # Enable member intent
intents.voice_states = True  # Enable voice state intent
intents.message_content = True  # Required for reading message content
bot = commands.AutoShardedBot(command_prefix="!", intents=intents)

# Load the Opus library
try:
    discord.opus.load_opus(os.getenv('OPUS_PATH'))  # Path to Opus library
    print("Opus library loaded successfully.")
except discord.opus.OpusNotLoaded:
    print("Failed to load the Opus library. Ensure it is installed correctly.")

# Global variables
connections = {}

def send_for_processing(filePath):
    with Connection(redis_url) as conn:
        producer = conn.Producer(serializer="json")
        producer.publish(
            {"message": filePath},
            exchange=exchange,
            routing_key="example_key",
            declare=[queue]
        )

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name}#{bot.user.discriminator}')
    print(f'Total Guilds: {len(bot.guilds)}')

@bot.command()
async def join(ctx):
    """Command to join a voice channel and start recording."""
    if not isinstance(ctx.author, discord.Member):
        await ctx.send("⚠️ This command can only be used in a server!")
        return

    # Check if the user is in a voice channel
    voice = ctx.author.voice
    if not voice:
        await ctx.send("⚠️ You aren't in a voice channel!")
        return

    # Join the user's voice channel
    try:
        vc = await voice.channel.connect()
        connections[ctx.guild.id] = vc

        # Start recording
        vc.start_recording(
            discord.sinks.WaveSink(),  # Recording in WAV format
            once_done,
            ctx.channel,
        )
        await ctx.send("🔴 Listening and recording this conversation.")
    except discord.ClientException as e:
        await ctx.send(f"⚠️ Could not join the voice channel: {str(e)}")
    except Exception as e:
        await ctx.send(f"⚠️ An unexpected error occurred: {str(e)}")

async def once_done(sink: discord.sinks.WaveSink, channel: discord.TextChannel, *args):
    """Callback for processing recordings after completion."""
    recorded_users = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.join("recordings", f"{channel.name}_{timestamp}")  # Directory for the channel
    os.makedirs(base_dir, exist_ok=True)  # Ensure directory exists

    info_data = {
        "channel_name": channel.name,
        "total_users": len(sink.audio_data),
        "users": [],
        "timestamp": timestamp,
        "guild_id": channel.guild.id,
        "guild_name": channel.guild.name,
        "text_channel_id": channel.id,
        "text_channel_name": channel.name
    }

    try:
        for user_id, audio in sink.audio_data.items():
            user = await channel.guild.fetch_member(user_id)  # Fetch user object
            username = user.display_name
            full_tag = f"{user.name}#{user.discriminator}"

            file_name = f"recording_{username}_{timestamp}.wav"
            file_path = os.path.join(base_dir, file_name)

            # Save audio file
            with open(file_path, "wb") as f:
                f.write(audio.file.read())

            file_size = os.path.getsize(file_path) / 1024  # File size in KB
            print(f"Saved recording: {file_path} ({file_size:.2f} KB)")

            recorded_users.append(f"{username} ({full_tag})")
            info_data["users"].append({
                "user_id": user.id,
                "user_name": username,
                "user_tag": full_tag,
                "file_name": file_name,
                "file_path": file_path,
                "file_size_kb": file_size
            })

        # Save metadata as JSON
        info_file_path = os.path.join(base_dir, "info.json")
        with open(info_file_path, "w", encoding="utf-8") as info_file:
            json.dump(info_data, info_file, indent=4)
        send_for_processing(info_file_path)
        print(f"Saved metadata to {info_file_path}")
        await channel.send(
            f"🎙️ Recording finished for: {', '.join(recorded_users)}. Files saved in `{base_dir}`."
        )

    except Exception as e:
        error_message = f"An error occurred while processing the recordings: {str(e)}"
        print(error_message)
        await channel.send(f"⚠️ {error_message}")
    finally:
        try:
            # Ensure all data is flushed and disconnected
            for audio in sink.audio_data.values():
                audio.file.close()  # Close all audio file streams
            sink.audio_data.clear()  # Clear audio data to prevent memory issues

            if sink.vc and sink.vc.is_connected():
                await sink.vc.disconnect()
        except Exception as final_err:
            print(f"Error during cleanup: {final_err}")

@bot.command()
async def stop(ctx):
    """Command to stop recording."""
    if ctx.guild.id in connections:
        vc = connections.pop(ctx.guild.id)
        try:
            vc.stop_recording()
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred while stopping the recording: {str(e)}")
        await ctx.send("⏹️ Stopped recording.")
    else:
        await ctx.send("🚫 Not recording in this server.")

# Graceful shutdown handler
@bot.event
async def on_disconnect():
    for vc in connections.values():
        if vc.is_connected():
            try:
                await vc.disconnect()
            except Exception as disconnect_err:
                print(f"Error during disconnect: {disconnect_err}")
    connections.clear()

# Run the bot
try:
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
except Exception as e:
    print(f"Failed to start bot: {e}")
