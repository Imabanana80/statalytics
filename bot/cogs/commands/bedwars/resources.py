import os

import discord
from discord import app_commands
from discord.ext import commands

from render.resources import render_resources
from helper import (
    fetch_player_info,
    username_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    send_generic_renders,
    loading_message
)


class Resources(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(name="resources", description="View the resource stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def resources(self, interaction: discord.Interaction, username: str=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        await interaction.followup.send(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        hypixel_data = await get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "save_dir": interaction.id
        }

        await send_generic_renders(interaction, render_resources, kwargs)
        update_command_stats(interaction.user.id, 'resources')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Resources(client))
