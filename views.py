import discord
import asyncio
import database
import embeds

class TierGamemodeSelect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001FAB0 Skywars", style=discord.ButtonStyle.primary, row=0, custom_id="mcpe_gm_skywars")
    async def btn_skywars(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Skywars")

    @discord.ui.button(label="\U0001F6E1\uFE0F BUHC", style=discord.ButtonStyle.primary, row=0, custom_id="mcpe_gm_buhc")
    async def btn_buhc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "BUHC")

    @discord.ui.button(label="\U0001F30B FUHC", style=discord.ButtonStyle.primary, row=0, custom_id="mcpe_gm_fuhc")
    async def btn_fuhc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "FUHC")

    @discord.ui.button(label="\U0001F44A Boxing", style=discord.ButtonStyle.primary, row=1, custom_id="mcpe_gm_boxing")
    async def btn_boxing(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Boxing")

    @discord.ui.button(label="\u26A1 Midfight", style=discord.ButtonStyle.primary, row=1, custom_id="mcpe_gm_midfight")
    async def btn_midfight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Midfight")

    @discord.ui.button(label="\U0001F4A4 Bedfight", style=discord.ButtonStyle.primary, row=1, custom_id="mcpe_gm_bedfight")
    async def btn_bedfight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._create_ticket(interaction, "Bedfight")

    async def _create_ticket(self, interaction: discord.Interaction, gamemode: str):
        await interaction.response.defer(ephemeral=True)

        cfg = database.get_guild_config(interaction.guild_id)
        if not cfg or not cfg.get('ticket_category_id'):
            await interaction.followup.send("\u274C Tier system is not configured. Ask an admin to run `/tier setup`.", ephemeral=True)
            return

        category = interaction.guild.get_channel(cfg['ticket_category_id'])
        if not category:
            await interaction.followup.send("\u274C Ticket category not found.", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if cfg.get('tier_tester_role_id'):
            tester_role = interaction.guild.get_role(cfg['tier_tester_role_id'])
            if tester_role:
                overwrites[tester_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if cfg.get('tier_staff_role_id'):
            staff_role = interaction.guild.get_role(cfg['tier_staff_role_id'])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        clean_name = f"tier-{interaction.user.name}-{gamemode.lower()}"
        clean_name = "".join(c if (c.isalnum() or c == "-") else "" for c in clean_name).lower()

        try:
            channel = await interaction.guild.create_text_channel(
                name=clean_name, category=category, overwrites=overwrites
            )
        except Exception as e:
            await interaction.followup.send(f"\u274C Failed to create ticket: {e}", ephemeral=True)
            return

        ticket_id = database.create_tier_ticket(interaction.guild_id, channel.id, interaction.user.id, gamemode)

        embed = embeds.tier_ticket_embed(interaction.user.id, gamemode)
        view = TierTicketView(ticket_id, interaction.user.id, gamemode)
        ping = f"<@{interaction.user.id}> | <@&{cfg['tier_staff_role_id']}>" if cfg.get('tier_staff_role_id') else f"<@{interaction.user.id}>"
        await channel.send(ping, embed=embed, view=view)

        await interaction.followup.send(f"\u2705 Ticket created in {channel.mention}.", ephemeral=True)


class TierTicketView(discord.ui.View):
    def __init__(self, ticket_id: int, user_id: int, gamemode: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.user_id = user_id
        self.gamemode = gamemode

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, row=0, custom_id="tier_claim", emoji="\u270B")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket = database.get_tier_ticket(interaction.channel.id)
        if not ticket or ticket['status'] != 'open':
            await interaction.response.send_message("\u274C This ticket has already been claimed or closed.", ephemeral=True)
            return

        database.claim_tier_ticket(self.ticket_id, interaction.user.id)

        embed = discord.Embed(
            title="\u270B Ticket Claimed",
            description=(
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
                f"<@{interaction.user.id}> is now handling this evaluation.\n"
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
                "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
            ),
            color=embeds.COLOR_GOLD
        )
        embed.add_field(name="Gamemode", value=f"`{self.gamemode}`", inline=True)
        embed.add_field(name="Player", value=f"<@{self.user_id}>", inline=True)
        await interaction.response.send_message(embed=embed)

        button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, row=0, custom_id="tier_close", emoji="\uD83D\uDD12")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket = database.get_tier_ticket(interaction.channel.id)
        if not ticket or ticket['status'] == 'closed':
            await interaction.response.send_message("\u274C This ticket is already closed.", ephemeral=True)
            return

        database.close_tier_ticket(self.ticket_id)
        await interaction.response.send_message("\uD83D\uDD12 Closing this ticket in 5 seconds...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except:
            pass
