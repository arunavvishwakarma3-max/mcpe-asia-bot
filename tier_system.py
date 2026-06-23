import discord
from discord import app_commands
import database
import embeds
import views

def is_tier_staff():
    async def predicate(interaction: discord.Interaction):
        cfg = database.get_guild_config(interaction.guild_id)
        if not cfg:
            return False
        if interaction.user.guild_permissions.administrator:
            return True
        roles = interaction.user.roles
        if cfg.get('tier_staff_role_id') and interaction.guild.get_role(cfg['tier_staff_role_id']) in roles:
            return True
        if cfg.get('tier_tester_role_id') and interaction.guild.get_role(cfg['tier_tester_role_id']) in roles:
            return True
        return False
    return app_commands.check(predicate)

class TierGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="tier", description="Tier test system commands")

    @app_commands.command(name="setup", description="Configure the tier testing system.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        tier_channel="Channel for the tier lobby panel",
        results_channel="Channel for publishing tier results",
        ticket_category="Category for tier ticket channels",
        staff_role="Role that can manage tier tickets",
        tester_role="Role for tier testers (optional)"
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        tier_channel: discord.TextChannel,
        results_channel: discord.TextChannel,
        ticket_category: discord.CategoryChannel,
        staff_role: discord.Role,
        tester_role: discord.Role = None
    ):
        await interaction.response.defer(ephemeral=True)

        data = {
            "tier_channel_id": tier_channel.id,
            "tier_results_channel_id": results_channel.id,
            "ticket_category_id": ticket_category.id,
            "tier_staff_role_id": staff_role.id,
        }
        if tester_role:
            data["tier_tester_role_id"] = tester_role.id

        cfg = database.get_guild_config(interaction.guild_id)
        old_channel_id = cfg.get('tier_channel_id') if cfg else None
        old_msg_id = cfg.get('tier_message_id') if cfg else None
        if old_channel_id and old_msg_id:
            old_channel = interaction.guild.get_channel(old_channel_id)
            if old_channel:
                try:
                    old_msg = await old_channel.fetch_message(old_msg_id)
                    await old_msg.delete()
                except:
                    pass

        embed = embeds.tier_hub_embed()
        view = views.TierGamemodeSelect()
        msg = await tier_channel.send(embed=embed, view=view)
        bot_ref = interaction.client
        if hasattr(bot_ref, 'add_view') and callable(bot_ref.add_view):
            bot_ref.add_view(view, message_id=msg.id)

        data["tier_message_id"] = msg.id
        database.save_guild_config(interaction.guild_id, data)

        success = embeds.tiersetup_success_embed(
            tier_channel, results_channel, ticket_category, staff_role, tester_role
        )
        await interaction.followup.send(embed=success, ephemeral=True)

    @setup.error
    async def setup_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("\u274C You need Manage Server permission to use this command.", ephemeral=True)

    @app_commands.command(name="remove", description="Delete the tier hub panel from its channel.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        cfg = database.get_guild_config(interaction.guild_id)
        if not cfg or not cfg.get('tier_channel_id'):
            await interaction.followup.send("\u274C No tier system is configured.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(cfg['tier_channel_id'])
        msg_id = cfg.get('tier_message_id')

        if channel and msg_id:
            try:
                msg = await channel.fetch_message(msg_id)
                await msg.delete()
                deleted = True
            except:
                pass

        database.save_guild_config(interaction.guild_id, {
            "tier_channel_id": None,
            "tier_results_channel_id": None,
            "ticket_category_id": None,
            "tier_staff_role_id": None,
            "tier_tester_role_id": None,
            "tier_message_id": None,
        })

        embed = embeds.tier_remove_embed()
        await interaction.followup.send(embed=embed, ephemeral=True)

    @remove.error
    async def remove_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("\u274C You need Manage Server permission to use this command.", ephemeral=True)

    @app_commands.command(name="result", description="Submit a tier evaluation result.")
    @is_tier_staff()
    @app_commands.describe(
        player="The player who was evaluated",
        ign="The player's in-game name",
        previous_tier="Tier before evaluation",
        new_tier="Tier after evaluation",
        note="Optional notes"
    )
    async def result(
        self,
        interaction: discord.Interaction,
        player: discord.Member,
        ign: str,
        previous_tier: str,
        new_tier: str,
        note: str = None
    ):
        await interaction.response.defer(ephemeral=True)

        database.save_tier_result(
            guild_id=interaction.guild_id,
            user_id=player.id,
            ign=ign,
            previous_tier=previous_tier,
            new_tier=new_tier,
            note=note or "No notes provided.",
            tester_id=interaction.user.id
        )

        tier_mapping = database.get_tier_role_mapping(interaction.guild_id)
        role_updates = []
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
            "user_id": player.id,
            "ign": ign,
            "previous_tier": previous_tier,
            "new_tier": new_tier,
            "note": note or "No notes provided.",
            "tester_id": interaction.user.id
        }
        embed = embeds.tier_result_embed(result_data)

        cfg = database.get_guild_config(interaction.guild_id)
        if cfg and cfg.get('tier_results_channel_id'):
            chan = interaction.guild.get_channel(cfg['tier_results_channel_id'])
            if chan:
                await chan.send(embed=embed)

        role_msg = f"\n\uD83C\uDFC6 Roles: {', '.join(role_updates)}" if role_updates else ""
        await interaction.followup.send(f"\u2705 Result recorded for **{player.display_name}**.{role_msg}", ephemeral=True)

    @result.error
    async def result_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("\u274C You do not have permission to use this command.", ephemeral=True)

    @app_commands.command(name="history", description="View recent tier evaluation results.")
    async def history(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        results = database.get_tier_results(interaction.guild_id, limit=10)
        if not results:
            await interaction.followup.send("\uD83D\uDCED No tier results recorded yet.", ephemeral=True)
            return

        embed = embeds.tier_history_embed(results)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="setrole", description="Map a tier name to a role (auto-assigned on evaluation).")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        tier_name="The tier name (e.g. LT3, Iron, Gold)",
        role="The role to assign when this tier is earned"
    )
    async def setrole(self, interaction: discord.Interaction, tier_name: str, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        database.set_tier_role(interaction.guild_id, tier_name, role.id)
        embed = embeds.tier_role_embed(tier_name, role.mention)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @setrole.error
    async def setrole_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("\u274C You need Manage Server permission to use this command.", ephemeral=True)

    @app_commands.command(name="unsetrole", description="Remove a tier-to-role mapping.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(tier_name="The tier name to unmap")
    async def unsetrole(self, interaction: discord.Interaction, tier_name: str):
        await interaction.response.defer(ephemeral=True)
        database.remove_tier_role(interaction.guild_id, tier_name)
        await interaction.followup.send(f"\u2705 Role mapping removed for **{tier_name}**.", ephemeral=True)

    @unsetrole.error
    async def unsetrole_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("\u274C You need Manage Server permission to use this command.", ephemeral=True)

    @app_commands.command(name="roles", description="List all tier-to-role mappings.")
    async def list_roles(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        mapping = database.get_tier_role_mapping(interaction.guild_id)
        if not mapping:
            await interaction.followup.send("\uD83D\uDCED No tier role mappings configured. Use `/tier setrole` to add some.", ephemeral=True)
            return

        embed = embeds.tier_roles_list_embed(mapping)
        await interaction.followup.send(embed=embed, ephemeral=True)
