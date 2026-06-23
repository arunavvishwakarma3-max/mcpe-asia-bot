import discord

COLOR_GOLD = 0xFFD700
COLOR_ACCENT = 0x7B2FBE
COLOR_GREEN = 0x00FF88
COLOR_INFO = 0x4FC3F7

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
        f"\u2022 **{label}**"
        for label in GAMEMODE_LABELS.values()
    )
    embed = discord.Embed(
        title="\uD83C\uDFAA **TIER EVALUATION**",
        description=(
            f"Click a button below to request a tier test.\n"
            f"You'll be asked for your **IGN** & **available time**."
        ),
        color=COLOR_GOLD
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.add_field(
        name="\uD83C\uDFAE Gamemodes",
        value=lines,
        inline=True
    )
    embed.add_field(
        name="\uD83D\uDCDD Rules",
        value=(
            f"\u2022 Stable internet required\n"
            f"\u2022 Tier decisions are final\n"
            f"\u2022 Respect staff"
        ),
        inline=True
    )
    embed.set_footer(text="MCPE ASIA \u2022 Click to begin")
    return embed

def tier_ticket_embed(user_id: int, gamemode: str, ign: str, time: str):
    embed = discord.Embed(
        title="\uD83C\uDF9F\uFE0F **TIER TICKET**",
        description=(
            f"<@{user_id}> requested a **{gamemode}** evaluation.\n"
            f"Status: \u23F3 **Pending**"
        ),
        color=COLOR_ACCENT
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.add_field(name="\uD83D\uDCDD IGN", value=f"**{ign}**", inline=True)
    embed.add_field(name="\uD83D\uDD52 Time", value=f"**{time}**", inline=True)
    embed.add_field(
        name="\u2699\uFE0F",
        value=(
            f"\u270B **Claim** \u2014 handle the request\n"
            f"\uD83D\uDCDD **Result** \u2014 submit evaluation\n"
            f"\uD83D\uDD12 **Close** \u2014 delete ticket"
        ),
        inline=False
    )
    embed.set_footer(text=f"MCPE ASIA \u2022 {gamemode}")
    return embed

def tier_claim_embed(user_id: int, gamemode: str, ign: str, time: str, claimed_by: int):
    embed = discord.Embed(
        title="\u270B **TICKET CLAIMED**",
        description=(
            f"<@{claimed_by}> is handling **{gamemode}** for <@{user_id}>."
        ),
        color=COLOR_GOLD
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.add_field(name="\uD83D\uDCDD IGN", value=f"**{ign}**", inline=True)
    embed.add_field(name="\uD83D\uDD52 Time", value=f"**{time}**", inline=True)
    embed.set_footer(text="MCPE ASIA \u2022 Evaluation In Progress")
    return embed

def tier_result_embed(result: dict):
    embed = discord.Embed(
        title="\u2705 **TIER COMPLETE**",
        description=(
            f"**{result['ign']}** evaluated by <@{result['tester_id']}>."
        ),
        color=COLOR_GREEN
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.add_field(name="\uD83D\uDC64 Player", value=f"<@{result['user_id']}>", inline=True)
    embed.add_field(name="\u2B07 Previous", value=f"**{result['previous_tier']}**", inline=True)
    embed.add_field(name="\u2B06 New Tier", value=f"**{result['new_tier']}**", inline=True)
    embed.add_field(name="\uD83D\uDCDD Notes", value=result['note'] or "None", inline=False)
    embed.set_footer(text="MCPE ASIA \u2022 Results")
    return embed

def tier_history_embed(results: list):
    embed = discord.Embed(
        title="\uD83D\uDCDC **TIER HISTORY**",
        color=COLOR_INFO
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    for r in results:
        embed.add_field(
            name=f"**{r['ign']}** {r['previous_tier']} \u2192 {r['new_tier']}",
            value=f"<@{r['user_id']}> \u2022 by <@{r['tester_id']}>",
            inline=False
        )
    embed.set_footer(text="MCPE ASIA \u2022 Recent results")
    return embed

def tier_role_embed(tier_name: str, role_name: str):
    embed = discord.Embed(
        title="\uD83C\uDFC6 **ROLE MAPPED**",
        description=f"**{tier_name}** \u2192 {role_name}",
        color=COLOR_GREEN
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    return embed

def tier_roles_list_embed(mapping: dict):
    lines = "\n".join(f"\u2022 **{t}** \u2192 <@&{r}>" for t, r in mapping.items())
    embed = discord.Embed(
        title="\uD83C\uDFC6 **ROLE MAPPINGS**",
        description=lines,
        color=COLOR_GOLD
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    return embed

def tiersetup_success_embed(tier_channel, results_channel, ticket_category, staff_role, tester_role):
    text = (
        f"\uD83D\uDCCD {tier_channel.mention} - Lobby\n"
        f"\uD83D\uDCCD {results_channel.mention} - Results\n"
        f"\uD83D\uDCCD {ticket_category.mention} - Tickets\n"
        f"\uD83D\uDC64 {staff_role.mention} - Staff\n"
    )
    if tester_role:
        text += f"\uD83D\uDC64 {tester_role.mention} - Testers"
    embed = discord.Embed(
        title="\u2705 **SYSTEM READY**",
        description=text,
        color=COLOR_GREEN
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.set_footer(text="MCPE ASIA \u2022 Tier System Active")
    return embed

def tier_remove_embed():
    embed = discord.Embed(
        title="\uD83D\uDDD1\uFE0F **SYSTEM REMOVED**",
        description="The tier hub panel has been deleted. You can re-run `/tier setup` anytime.",
        color=COLOR_INFO
    )
    embed.set_thumbnail(url="https://i.imgur.com/g8o468o.png")
    embed.set_footer(text="MCPE ASIA \u2022 Tier System Removed")
    return embed
