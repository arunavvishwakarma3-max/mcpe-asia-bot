import discord

COLOR_PURPLE = 0x9B59B6
COLOR_BLUE = 0x3498DB
COLOR_GREEN = 0x2ECC71
COLOR_GOLD = 0xFFD700
COLOR_TEAL = 0x1ABC9C

GAMEMODE_EMOJIS = {
    "Skywars": "\U0001FAB0",
    "BUHC": "\U0001F6E1\uFE0F",
    "FUHC": "\U0001F30B",
    "Boxing": "\U0001F44A",
    "Midfight": "\u26A1",
    "Bedfight": "\U0001F4A4",
}

GAMEMODE_LABELS = {
    "Skywars": "Skywars",
    "BUHC": "BUHC",
    "FUHC": "FUHC",
    "Boxing": "Boxing",
    "Midfight": "Midfight",
    "Bedfight": "Bedfight",
}

def tier_hub_embed():
    lines = "\n".join(
        f"{GAMEMODE_EMOJIS[gm]} \u2014 **{label}**"
        for gm, label in GAMEMODE_LABELS.items()
    )
    embed = discord.Embed(
        title="\uD83C\uDFAA Tier Evaluation Portal",
        description=(
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            "Welcome to the official tier testing system.\n"
            "Select a gamemode below to begin your evaluation.\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
        ),
        color=COLOR_PURPLE
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.add_field(
        name="\uD83C\uDFAE Available Gamemodes",
        value=f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
               f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
               f"{lines}\n"
               f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
               f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501",
        inline=False
    )
    embed.add_field(
        name="\uD83D\uDCDD Guidelines",
        value=(
            "\u2022 A stable internet connection is required.\n"
            "\u2022 Tier decisions are final and binding.\n"
            "\u2022 Respect staff and testers at all times.\n"
            "\u2022 Do not create multiple tickets."
        ),
        inline=False
    )
    embed.set_footer(text="MCPE ASIA \u2022 Tier System")
    return embed

def tier_ticket_embed(user_id: int, gamemode: str):
    emoji = GAMEMODE_EMOJIS.get(gamemode, "\uD83C\uDFAE")
    embed = discord.Embed(
        title="\uD83C\uDF9F\uFE0F New Tier Ticket",
        description=(
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"A player has requested a **{gamemode}** evaluation.\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
        ),
        color=COLOR_BLUE
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.add_field(name="Player", value=f"<@{user_id}>", inline=True)
    embed.add_field(name="Gamemode", value=f"{emoji} {gamemode}", inline=True)
    embed.add_field(name="Status", value="```css\n[ Pending ]\n```", inline=True)
    embed.add_field(
        name="Actions",
        value=(
            "\u2022 **Staff** \u2014 Click `\u270B Claim` to handle this request\n"
            "\u2022 **Tester** \u2014 Use `/tier result` after evaluation\n"
            "\u2022 **Player** \u2014 Please wait for a staff member"
        ),
        inline=False
    )
    embed.set_footer(text="MCPE ASIA \u2022 Tier Tickets")
    return embed

def tier_result_embed(result: dict):
    embed = discord.Embed(
        title="\u2705 Tier Test Complete",
        description=(
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"**{result['ign']}** has been officially tiered.\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
        ),
        color=COLOR_GREEN
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.add_field(name="Player", value=f"<@{result['user_id']}>", inline=True)
    embed.add_field(name="IGN", value=f"`{result['ign']}`", inline=True)
    embed.add_field(name="Previous Tier", value=f"```\n{result['previous_tier']}\n```", inline=True)
    embed.add_field(name="New Tier", value=f"```diff\n+ {result['new_tier']}\n```", inline=True)
    embed.add_field(name="Notes", value=f"```{result['note'] or 'None'}```", inline=False)
    embed.add_field(name="Evaluated By", value=f"<@{result['tester_id']}>", inline=True)
    embed.set_footer(text="MCPE ASIA \u2022 Tier Results")
    return embed

def welcome_embed(member: discord.Member, member_count: int):
    embed = discord.Embed(
        title="\uD83D\uDC4B Welcome to the Server!",
        description=(
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"Welcome to **{member.guild.name}**, {member.mention}!\n"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
        ),
        color=COLOR_TEAL
    )
    embed.set_image(url=member.display_avatar.url)
    embed.add_field(
        name="\uD83D\uDCD6 Getting Started",
        value=(
            "\u2022 Read the server rules\n"
            "\u2022 Visit `/tier` to get ranked\n"
            "\u2022 Enjoy your stay!"
        ),
        inline=False
    )
    embed.add_field(
        name="\uD83D\uDCC5 Member Information",
        value=f"\u2022 **User:** {member.mention}\n\u2022 **Joined:** <t:{int(member.joined_at.timestamp())}:R>\n\u2022 **Member #:** `{member_count}`",
        inline=False
    )
    embed.set_footer(text=f"MCPE ASIA \u2022 Member #{member_count}")
    return embed
