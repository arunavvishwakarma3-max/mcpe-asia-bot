import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import database
import embeds
import views
import tier_system
import welcome_system

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

class MCPEAsiaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.tree.add_command(tier_system.TierGroup())
        self.tree.add_command(welcome_system.WelcomeGroup())

        help_cmd = app_commands.Command(
            name="help",
            description="Show all available commands",
            callback=self.help_callback,
        )
        self.tree.add_command(help_cmd)

    async def on_ready(self):
        database.init_db()
        print(f"Logged in as {self.user.name} ({self.user.id})")

        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash commands.")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        self.add_view(views.TierGamemodeSelect())
        print("Persistent views restored.")

    async def on_member_join(self, member: discord.Member):
        await welcome_system.send_welcome(member)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if self.user in message.mentions:
            embed = discord.Embed(
                title="\uD83D\uDC4B Need Help?",
                description=(
                    "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                    "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
                    f"Hi {message.author.mention}! Here are my commands:\n"
                    "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                    "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                ),
                color=0x9B59B6
            )
            embed.add_field(
                name="\uD83D\uDCCC Commands",
                value=(
                    "\u2022 `/tier setup` \u2014 Configure the tier system\n"
                    "\u2022 `/tier result` \u2014 Record a tier evaluation\n"
                    "\u2022 `/tier history` \u2014 View past results\n"
                    "\u2022 `/tier setrole` \u2014 Map a tier to a role\n"
                    "\u2022 `/tier roles` \u2014 View tier role mappings\n"
                    "\u2022 `/welcome setup` \u2014 Set welcome channel\n"
                    "\u2022 `/welcome test` \u2014 Test welcome message\n"
                    "\u2022 `/help` \u2014 Show this menu"
                ),
                inline=False
            )
            embed.set_footer(text="MCPE ASIA \u2022 Need anything else?")
            await message.channel.send(embed=embed)

    async def help_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="\uD83D\uDCD6 MCPE ASIA Commands",
            description=(
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            ),
            color=embeds.COLOR_GOLD
        )
        embed.add_field(
            name="\uD83C\uDFAA Tier System",
            value=(
                "`/tier setup` \u2014 Configure the tier system\n"
                "`/tier result` \u2014 Record a tier evaluation\n"
                "`/tier history` \u2014 View recent results\n"
                "`/tier setrole` \u2014 Map tier name to a role\n"
                "`/tier unsetrole` \u2014 Remove a tier-role mapping\n"
                "`/tier roles` \u2014 View all tier-role mappings"
            ),
            inline=False
        )
        embed.add_field(
            name="\uD83D\uDC4B Welcome System",
            value=(
                "`/welcome setup` \u2014 Set welcome channel\n"
                "`/welcome test` \u2014 Send a test welcome"
            ),
            inline=False
        )
        embed.set_footer(text="MCPE ASIA \u2022 Built for MCPE")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"MCPE ASIA Bot is alive!")

    def log_message(self, format, *args):
        pass

bot = MCPEAsiaBot()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    health_thread = threading.Thread(target=server.serve_forever)
    health_thread.start()
    print(f"Health server running on port {port}")

    if TOKEN and TOKEN != "your_discord_token_here":
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"Bot failed: {e}")
    else:
        print("DISCORD_TOKEN not set. Add it in Render dashboard and redeploy.")

    health_thread.join()
