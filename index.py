import discord
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
import time
import os
import json
from datetime import datetime
from transcribe import get_transcription_results
from summarize.summarize_openai import summarize_text
import asyncio 
# Load environment variables
load_dotenv()

# Initialize bot
intents = discord.Intents.default()
intents.members = True  # Enable member intent
intents.voice_states = True  # Enable voice state intent
intents.message_content = True  # Required for reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

# Load the Opus library
try:
    discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')  # Path to Opus
    print("Opus library loaded successfully.")
except discord.opus.OpusNotLoaded:
    print("Failed to load the Opus library. Please ensure it is installed correctly.")

# Global variables
connections = {}

@bot.command()
async def record(ctx):
    # Ensure ctx.author is a Member object
    if not isinstance(ctx.author, discord.Member):
        await ctx.send("⚠️ This command can only be used in a server!")
        return

    # Check if the user is in a voice channel
    voice = ctx.author.voice
    if not voice:
        await ctx.send("⚠️ You aren't in a voice channel!")
        return

    # Join the user's voice channel
    vc = await voice.channel.connect()
    connections[ctx.guild.id] = vc

    # Start recording and save to a file
    vc.start_recording(
        discord.sinks.WaveSink(),  # Recording in WAV format
        once_done,
        ctx.channel,
    )
    await ctx.send("🔴 Listening and recording this conversation.")
    
async def notify_users(users, message):
    for user in users:
        try:
            # Send a DM to the user
            await user.send('```'+message+'```')
            print(f"Sent DM to {user.display_name} ({user.name}#{user.discriminator})")
        except Exception as e:
            print(f"Failed to send DM to {user.display_name}: {e}")
            
async def process_recorded_audio(file_path):
        result = get_transcription_results(file_path)
        summarized_output = summarize_text(result)
                # Write the summarized output to a file
        summarized_file_path = os.path.join(os.getcwd(), "summarized_output", "summarized_output"+str(int(time.time()))+".txt")
        os.makedirs(os.path.dirname(summarized_file_path), exist_ok=True)  # Ensure the directory exists
        with open(summarized_file_path, "w", encoding="utf-8") as summarized_file:
            summarized_file.write(summarized_output)
        print("Summarized output saved to:", summarized_file_path)

# Helper function to handle file writing (offloaded to a thread)
def write_to_file(file_path, content):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

async def process_recorded_audio_thread(file_path,users):
    try:
        # Offload the transcription and summarization to a thread pool
        transcription_result = await asyncio.to_thread(get_transcription_results, file_path)
        summarized_output = await asyncio.to_thread(summarize_text, transcription_result)

        # Offload file writing to a thread
        summarized_file_path = os.path.join("summarized_output", "summarized_output.txt")
        await asyncio.to_thread(os.makedirs, os.path.dirname(summarized_file_path), exist_ok=True)
        await asyncio.to_thread(write_to_file, summarized_file_path, summarized_output)
        await notify_users(users, summarized_output)

        print(f"Summarized output saved to {summarized_file_path}")
    except Exception as e:
        print(f"Error processing recorded audio: {e}")
    
async def once_done(sink: discord.sinks.WaveSink, channel: discord.TextChannel, *args):
    recorded_users = []
    user_objects = [] 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.join("recordings", channel.name+"_"+timestamp)  # Directory for channel
    os.makedirs(base_dir, exist_ok=True)  # Ensure the channel-specific directory exists

    info_data = {
        "channel_name": channel.name,
        "total_users": len(sink.audio_data),
        "users": [],
    }

    try:
        for user_id, audio in sink.audio_data.items():
            user = await channel.guild.fetch_member(user_id)  # Fetch the user object
            user_objects.append(user)
            username = user.display_name  # Get the user's display name
            full_tag = f"{user.name}#{user.discriminator}"  # Full tag (username#discriminator)

            file_name = f"recording_{username}_{timestamp}.wav"
            file_path = os.path.join(base_dir, file_name)

            # Save the audio file
            with open(file_path, "wb") as f:
                f.write(audio.file.read())
            
            file_size = os.path.getsize(file_path) / 1024  # File size in KB
            print(f"Saved recording: {file_path} ({file_size:.2f} KB)")

            recorded_users.append(f"{username} ({full_tag})")
            info_data["users"].append({
                "user_name": username,
                "user_tag": full_tag,
                "file_name": file_name,
                "file_path": file_path,
            })

        # Save info.json in the channel directory
        info_file_path = os.path.join(base_dir, "info.json")
        with open(info_file_path, "w", encoding="utf-8") as info_file:
            json.dump(info_data, info_file, indent=4)
        
        print(f"Saved metadata to {info_file_path}")
        # print(f"Saved summarized output to {summarized_file_path}")
        asyncio.create_task(process_recorded_audio_thread(info_file_path,user_objects))
        # notify_users(user_objects, summarized_output)
        
        # Disconnect the voice client
        await sink.vc.disconnect()
        await channel.send(
            f"🎙️ Recording finished for: {', '.join(recorded_users)}. "
            f"Audio files and metadata have been saved in the `{base_dir}` directory."
        )
    except Exception as e:
        # Log the error and notify the channel
        error_message = f"An error occurred while processing the recordings: {str(e)}"
        print(error_message)
        await channel.send(f"⚠️ {error_message}")

@bot.command()
async def stop_recording(ctx):
    if ctx.guild.id in connections:
        vc = connections.pop(ctx.guild.id)
        vc.stop_recording()
        await ctx.send("⏹️ Stopped recording.")
    else:
        await ctx.send("🚫 Not recording in this server.")


# Run the bot (use environment variable for token)
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
