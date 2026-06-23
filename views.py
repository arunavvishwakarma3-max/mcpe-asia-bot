import discord
import asyncio
import database
import embeds

class TierInfoModal(discord.ui.Modal, title="Tier Evaluation Details"):
    def __init__(self, gamemode: str):
        super().__init__()
        self.gamemode = gamemode

        self.ign = discord.ui.TextInput(
            label="In-Game Name (IGN)",
            placeholder="e.g. xXPlayer123Xx",
            min_length=2,
            max_length=32,
            required=True
        )
        self.time = discord.ui.TextInput(
            label="Available Time",
            placeholder="e.g. 8 PM - 10 PM IST / Anytime",
            min_length=2,
            max_length=64,
            required=True
        )
        self.add_item(self.ign)
        self.add_item(self.time)

    async def on_submit(self, interaction: discord.Interaction):
        ign = self.ign.value.strip()
        time = self.time.value.strip()

        cfg = database.get_guild_config(interaction.guild_id)
        if not cfg or not cfg.get('ticket_category_id'):
            await interaction.response.send_message(
                "\u274C Tier system is not configured. Ask an admin to run `/tier setup`.",
                ephemeral=True
            )
            return

        category = interaction.guild.get_channel(cfg['ticket_category_id'])
        if not category:
            await interaction.response.send_message("\u274C Ticket category not found.", ephemeral=True)
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

        clean_name = f"tier-{interaction.user.name}-{self.gamemode.lower()}"
        clean_name = "".join(c if (c.isalnum() or c == "-") else "" for c in clean_name).lower()

        await interaction.response.defer(ephemeral=True)

        try:
            channel = await interaction.guild.create_text_channel(
                name=clean_name, category=category, overwrites=overwrites
            )
        except Exception as e:
            await interaction.followup.send(f"\u274C Failed to create ticket: {e}", ephemeral=True)
            return

        ticket_id = database.create_tier_ticket(
            interaction.guild_id, channel.id, interaction.user.id,
            self.gamemode, ign, time
        )

        embed = embeds.tier_ticket_embed(interaction.user.id, self.gamemode, ign, time)
        view = TierTicketView(ticket_id, interaction.user.id, self.gamemode, ign, time)
        ping = (
            f"<@{interaction.user.id}> | <@&{cfg['tier_staff_role_id']}>"
            if cfg.get('tier_staff_role_id')
            else f"<@{interaction.user.id}>"
        )
        await channel.send(ping, embed=embed, view=view)

        await interaction.followup.send(
            f"\u2705 Ticket created in {channel.mention} for **{self.gamemode}**.",
            ephemeral=True
        )


class TierResultModal(discord.ui.Modal, title="Submit Tier Result"):
    def __init__(self, player_id: int, ign: str):
        super().__init__()
        self.player_id = player_id

        self.ign_input = discord.ui.TextInput(
            label="IGN",
            default=ign,
            required=True,
            max_length=32
        )
        self.previous_tier = discord.ui.TextInput(
            label="Previous Tier",
            placeholder="e.g. Unranked, Iron, Gold",
            required=True,
            max_length=32
        )
        self.new_tier = discord.ui.TextInput(
            label="New Tier",
            placeholder="e.g. Iron, Gold, Diamond",
            required=True,
            max_length=32
        )
        self.notes = discord.ui.TextInput(
            label="Notes (optional)",
            placeholder="Any notes about the evaluation",
            required=False,
            max_length=200
        )
        self.add_item(self.ign_input)
        self.add_item(self.previous_tier)
        self.add_item(self.new_tier)
        self.add_item(self.notes)

    async def on_submit(self, interaction: discord.Interaction):
        ign = self.ign_input.value.strip()
        previous_tier = self.previous_tier.value.strip()
        new_tier = self.new_tier.value.strip()
        notes = self.notes.value.strip() or "No notes provided."

        database.save_tier_result(
            guild_id=interaction.guild_id,
            user_id=self.player_id,
            ign=ign,
            previous_tier=previous_tier,
            new_tier=new_tier,
            note=notes,
            tester_id=interaction.user.id
        )

        tier_mapping = database.get_tier_role_mapping(interaction.guild_id)
        player = interaction.guild.get_member(self.player_id)
        role_updates = []
        if player:
            if new_tier in tier_mapping:
                new_role = interaction.guild.get_role(tier_mapping[new_tier])
                if new_role:
                    try:
                        await player.add_roles(new_role, reason=f"Tier evaluation: {previous_tier} \u2192 {new_tier}")
                        role_updates.append(f"+ {new_role.name}")
                    except:
                        role_updates.append(f"\u274C Could not assign {new_role.name}")
            if previous_tier in tier_mapping and previous_tier != new_tier:
                old_role = interaction.guild.get_role(tier_mapping[previous_tier])
                if old_role and old_role in player.roles:
                    try:
                        await player.remove_roles(old_role, reason=f"Tier updated: {previous_tier} \u2192 {new_tier}")
                        role_updates.append(f"- {old_role.name}")
                    except:
                        pass

        result_data = {
            "user_id": self.player_id,
            "ign": ign,
            "previous_tier": previous_tier,
            "new_tier": new_tier,
            "note": notes,
            "tester_id": interaction.user.id
        }
        embed = embeds.tier_result_embed(result_data)

        cfg = database.get_guild_config(interaction.guild_id)
        if cfg and cfg.get('tier_results_channel_id'):
            chan = interaction.guild.get_channel(cfg['tier_results_channel_id'])
            if chan:
                await chan.send(embed=embed)

        await interaction.response.send_message(
            f"\u2705 Result recorded for **{ign}** ({previous_tier} \u2192 {new_tier})."
            f"{' Roles: ' + ', '.join(role_updates) if role_updates else ''}",
            ephemeral=False
        )


class TierGamemodeSelect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001FAB0 Skywars", style=discord.ButtonStyle.primary, row=0, custom_id="mcpe_gm_skywars")
    async def btn_skywars(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TierInfoModal("Skywars"))

    @discord.ui.button(label="\U0001F6E1\uFE0F BUHC", style=discord.ButtonStyle.primary, row=0, custom_id="mcpe_gm_buhc")
    async def btn_buhc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TierInfoModal("BUHC"))

    @discord.ui.button(label="\U0001F30B FUHC", style=discord.ButtonStyle.primary, row=0, custom_id="mcpe_gm_fuhc")
    async def btn_fuhc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TierInfoModal("FUHC"))

    @discord.ui.button(label="\U0001F44A Boxing", style=discord.ButtonStyle.primary, row=1, custom_id="mcpe_gm_boxing")
    async def btn_boxing(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TierInfoModal("Boxing"))

    @discord.ui.button(label="\u26A1 Midfight", style=discord.ButtonStyle.primary, row=1, custom_id="mcpe_gm_midfight")
    async def btn_midfight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TierInfoModal("Midfight"))

    @discord.ui.button(label="\U0001F4A4 Bedfight", style=discord.ButtonStyle.primary, row=1, custom_id="mcpe_gm_bedfight")
    async def btn_bedfight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TierInfoModal("Bedfight"))


class TierTicketView(discord.ui.View):
    def __init__(self, ticket_id: int, user_id: int, gamemode: str, ign: str, time: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.user_id = user_id
        self.gamemode = gamemode
        self.ign = ign
        self.time = time

    def _is_tester(self, interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        cfg = database.get_guild_config(interaction.guild_id)
        if not cfg:
            return False
        tester_role_id = cfg.get('tier_tester_role_id')
        if tester_role_id and interaction.guild.get_role(tester_role_id) in interaction.user.roles:
            return True
        return False

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, row=0, custom_id="tier_claim", emoji="\u270B")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False)

        ticket = database.get_tier_ticket(interaction.channel.id)
        if not ticket or ticket['status'] != 'open':
            await interaction.followup.send(
                "\u274C This ticket has already been claimed or closed.",
                ephemeral=True
            )
            return

        database.claim_tier_ticket(self.ticket_id, interaction.user.id)

        embed = embeds.tier_claim_embed(
            self.user_id, self.gamemode,
            self.ign, self.time, interaction.user.id
        )
        button.disabled = True
        await interaction.edit_original_response(view=self)
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Result", style=discord.ButtonStyle.success, row=0, custom_id="tier_result_btn", emoji="\uD83D\uDCDD")
    async def result_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self._is_tester(interaction):
            await interaction.response.send_message(
                "\u274C You don't have permission to submit results.",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(TierResultModal(self.user_id, self.ign))

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, row=0, custom_id="tier_close", emoji="\uD83D\uDD12")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False)

        ticket = database.get_tier_ticket(interaction.channel.id)
        if not ticket or ticket['status'] == 'closed':
            await interaction.followup.send(
                "\u274C This ticket is already closed.",
                ephemeral=True
            )
            return

        database.close_tier_ticket(self.ticket_id)
        await interaction.followup.send("\uD83D\uDD12 Closing this ticket in 5 seconds...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except:
            pass
