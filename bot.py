import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'🎉 Welcome to the server, {member.mention}!')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f'🧹 Cleared {amount} messages', delete_after=3)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'👢 {member.mention} was kicked.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'🔨 {member.mention} was banned.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned_users = await ctx.guild.bans()
    name, discriminator = member_name.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (name, discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'✅ Unbanned {user.mention}')
            return
    await ctx.send('❌ User not found.')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'🔇 {member.mention} has been muted.')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(muted_role)
    await ctx.send(f'🔊 {member.mention} has been unmuted.')

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, seconds: int, *, reason=None):
    duration = datetime.timedelta(seconds=seconds)
    await member.timeout(duration, reason=reason)
    await ctx.send(f'⏱️ {member.mention} has been timed out for {seconds} seconds.')

@bot.command()
async def help(ctx):
    help_text = """**🛠️ Admin Bot Commands**
`!clear [amount]` - Clear recent messages.
`!kick @user` - Kick a user.
`!ban @user` - Ban a user.
`!unban name#1234` - Unban a user.
`!mute @user` - Mute a user.
`!unmute @user` - Unmute a user.
`!timeout @user seconds` - Timeout a user.
`!help` - Show this help message."""
    await ctx.send(help_text)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('⛔ You do not have permission to use this command.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('⚠️ Missing argument. Please check your command.')
    else:
        await ctx.send('🚨 An error occurred.')
        raise error

bot.run(TOKEN)
