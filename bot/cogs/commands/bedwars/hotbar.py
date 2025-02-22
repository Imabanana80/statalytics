import discord
from discord import app_commands
from discord.ext import commands

from render.hotbar import render_hotbar
from helper import (
    fetch_player_info,
    username_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    loading_message
)


class Hotbar(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(name="hotbar", description="View the hotbar preferences of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def hotbar(self, interaction: discord.Interaction,username: str=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        hypixel_data = await get_hypixel_data(uuid)
        rendered = render_hotbar(name, uuid, hypixel_data)
        await interaction.edit_original_response(
            content=None, attachments=[discord.File(rendered, filename="hotbar.png")])

        update_command_stats(interaction.user.id, 'hotbar')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Hotbar(client))
