import discord
from discord import app_commands
import database
import embeds

class WelcomeGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="welcome", description="Welcome system commands")

    @app_commands.command(name="setup", description="Set the welcome message channel.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="Channel for welcome messages")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)

        cfg = database.get_guild_config(interaction.guild_id) or {}
        cfg['welcome_channel_id'] = channel.id
        database.save_guild_config(interaction.guild_id, cfg)

        embed = discord.Embed(
            title="\u2705 Welcome System Configured",
            description=(
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
                "New members will now be welcomed automatically.\n"
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                f"\n\n\uD83D\uDCCD **Channel:** {channel.mention}"
            ),
            color=embeds.COLOR_GREEN
        )
        embed.set_footer(text="MCPE ASIA \u2022 Welcome System")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="test", description="Send a test welcome message.")
    @app_commands.checks.has_permissions(administrator=True)
    async def test(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        cfg = database.get_guild_config(interaction.guild_id)
        if not cfg or not cfg.get('welcome_channel_id'):
            await interaction.followup.send("\u274C Welcome system not configured. Use `/welcome setup` first.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(cfg['welcome_channel_id'])
        if not channel:
            await interaction.followup.send("\u274C Welcome channel not found.", ephemeral=True)
            return

        embed = embeds.welcome_embed(interaction.user, interaction.guild.member_count)
        await channel.send(embed=embed)
        await interaction.followup.send(f"\u2705 Test welcome sent to {channel.mention}.", ephemeral=True)


async def send_welcome(member: discord.Member):
    cfg = database.get_guild_config(member.guild.id)
    if not cfg or not cfg.get('welcome_channel_id'):
        return

    channel = member.guild.get_channel(cfg['welcome_channel_id'])
    if not channel:
        return

    embed = embeds.welcome_embed(member, member.guild.member_count)
    try:
        await channel.send(embed=embed)
    except:
        pass
