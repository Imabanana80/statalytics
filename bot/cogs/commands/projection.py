import os
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from ui import SelectView
from render.renderprojection import renderprojection
from functions import (username_autocompletion,
                       session_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       get_smart_session,
                       authenticate_user,
                       skin_session)


class Projection(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Projected stats
    @app_commands.command(name = "prestige", description = "View the projected stats of a player")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', prestige='The prestige you want to view', session='The session you want to use as a benchmark (defaults to 1)')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def projected_stats(self, interaction: discord.Interaction, prestige: int, username: str=None, session: int=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        # Bot responses Logic
        refined = name.replace('_', r'\_')
        if session is None: session = 100
        session_data = await get_smart_session(interaction, session, refined, uuid)
        if not session_data: return
        if session == 100: session = session_data[0]

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)

        hypixel_data = get_hypixel_data(uuid)
        
        try:
            current_star = renderprojection(name, uuid, session, mode="Overall", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        except ZeroDivisionError:
            content = f"You can use `/bedwars` if you want current stats...\nUnless maybe an error occured? In which case please report this to the developers!"
            await interaction.edit_original_response(content=content)
            return
        
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')

        content = ":warning: THE LEVEL YOU ENTERED IS LOWER THAN THE CURRENT STAR! :warning:" if current_star > prestige else None
        await interaction.edit_original_response(content=content, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        renderprojection(name, uuid, session, mode="Solos", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        renderprojection(name, uuid, session, mode="Doubles", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        renderprojection(name, uuid, session, mode="Threes", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        renderprojection(name, uuid, session, mode="Fours", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        renderprojection(name, uuid, session, mode="4v4", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)

        update_command_stats(interaction.user.id, 'projection')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Projection(client))
