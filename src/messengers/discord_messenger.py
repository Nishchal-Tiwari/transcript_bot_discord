import discord
# Discord bot setup
class DiscordDM:
    def __init__(self, token):
        self.token = token
        self.client = discord.Client(intents=discord.Intents.default())
        self.loop = asyncio.get_event_loop()

        # Start the bot connection
        self.loop.create_task(self.client.start(self.token))
        self.loop.run_until_complete(self.wait_until_ready())

    async def wait_until_ready(self):
        await self.client.wait_until_ready()
        print(f"Discord bot logged in as {self.client.user}")

    async def send_dm(self, user_id, message_content):
        try:
            user = await self.client.fetch_user(user_id)
            await user.send(message_content)
            print(f"DM sent to {user.name}")
        except Exception as e:
            print(f"Failed to send DM: {e}")
            traceback.print_exc()

    def send_message(self, user_id, message_content):
        """Wrapper for sending a DM from the worker."""
        self.loop.run_until_complete(self.send_dm(user_id, message_content))