from discord.ext import commands, tasks
from typing import Optional
from PIL import Image, ImageDraw

import discord
import asyncio
import random
import io


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.messages = {}
        self.messages_task.start()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.messages[message.channel.id] = message

    @tasks.loop(minutes=2)
    async def messages_task(self):
        try:
            keyview = list(self.messages.keys())
            key = keyview[len(keyview) - 1]

            del self.messages[key]
        except (IndexError, KeyError):
            pass

    @commands.command
    async def snipe(self, ctx, channel: Optional[discord.TextChannel]):
        if channel is None:
            channel = ctx.channel
        try:
            msg = self.messages[ctx.channel.id]
        except KeyError:
            await ctx.reply("Nada para snipar!")
            return

        embed = discord.Embed(description=msg.content, color=msg.author.color)
        embed.set_author(name=msg.author, icon_url=msg.author.avatar_url)

        await ctx.reply(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def chatbot(self, ctx, *, texto: str):
        async with ctx.channel.typing():
            if not hasattr(self.client, "chat_thread") or not self.client.chat_thread.available:
                await ctx.reply("O comando `chatbot` não pôde ser executado por que"
                                    "o chatter está indisponível ou não está ativado.")
                return

            resposta = self.client.chat_thread.generate_response(texto)
            await ctx.channel.send(f"{ctx.author.mention} " + str(resposta.text))
            self.client.last_statements[ctx.author.id] = texto

    @commands.command(name="banrandom", aliases=["banc"])
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def randomban(self, ctx):
        """Bane alguém aleatóriamente"""

        client = self.client

        msg = await ctx.send("Fique atento de que o bot vai **realmente banir alguém**...\nPronto?")
        await msg.add_reaction("👎")
        await msg.add_reaction("👍")

        try:
            def react(reaction, user):
                return reaction.emoji in ["👍", "👎"] and user.id == ctx.author.id and reaction.message.id == msg.id
            reaction, user = await client.wait_for("reaction_add", check=react, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("comando cancelado.")
        else:
            if reaction.emoji == "👎":
                await ctx.send("comando cancelado.")
                return
            invite = random.choice(await ctx.guild.invites())

            memb = random.choice(list(filter(lambda member : member.top_role < ctx.me.top_role, ctx.guild.members)))
            await ctx.send(f"Eu escolhi {memb} pra ser banido :smiling_imp:...")

            await memb.send(f"Oi, você foi banido do `{ctx.guild.name}`, pelo comando banrandom, "
                        "daqui a 5 segundos, tente entrar no servidor usando esse convite: {invite.url}")

            await memb.ban(reason=f"Banido devido ao comando ,banrandom executado por {ctx.author}")

            await ctx.send(f"{ctx.author.mention} ele foi banido.")

            await asyncio.sleep(5)
            await ctx.guild.unban(memb, reason="Tinha sido banido pelo ,banrandom")

    def get_colors(self, image, colors=10, resize=150):
        if isinstance(image, bytes):
            image = io.BytesIO(image)
        image = Image.open(image)

        image = image.copy()
        image.thumbnail((resize, resize))

        palt = image.convert("P", palette=Image.ADAPTIVE, colors=colors)
        palette = palt.getpalette()
        color_counts = sorted(palt.getcolors(), reverse=True)
        colors = []

        for c in range(len(colors) + 1):
            palette_index = color_counts[c][1]
            dominant_color = palette[palette_index*3:palette_index*3+3]

            colors.append(tuple(dominant_color))

        return colors

    def save_palette(self, colors, swatchsize=20, outfile="palette.png"):
        num_colors = len(colors)
        palette = Image.new('RGB', (swatchsize*num_colors, swatchsize))
        draw = ImageDraw.Draw(palette)

        posx = 0
        for color in colors:
            draw.rectangle([posx, 0, posx+swatchsize, swatchsize], fill=color) 
            posx = posx + swatchsize

        del draw
        palette.save(outfile, "PNG")

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.member)
    async def domin(self, ctx, member: Optional[discord.Member]):
        avatar = (member or ctx.author).avatar_url

        colors = self.get_colors(await avatar.read())
        self.save_palette(colors)

        with open("palette.png", "rb") as fp:
            file = discord.File(fp, "palette.png")

        await ctx.reply(file=file)


    @commands.command(name="kickrandom", aliases=["kickr"])
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kickrandom(self, ctx):
        """Bane alguém aleatóriamente"""

        client = self.client

        msg = await ctx.send("Fique atento de que o bot vai **realmente expulsar alguém**...\nPronto?")
        await msg.add_reaction("👎")
        await msg.add_reaction("👍")

        try:
            def react(reaction, user):
                return reaction.emoji in ["👍", "👎"] and user.id == ctx.author.id and reaction.message.id == msg.id
            reaction, user = await client.wait_for("reaction_add", check=react, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("comando cancelado.")
        else:
            if reaction.emoji == "👎":
                await ctx.send("comando cancelado.")
                return
            invite = random.choice(await ctx.guild.invites())

            memb = random.choice(list(filter(lambda member : member.top_role < ctx.me.top_role, ctx.guild.members)))
            await ctx.send(f"Eu escolhi {memb} pra ser expulso :smiling_imp:...")

            await memb.send(f"Oi, você foi banido do `{ctx.guild.name}`, pelo comando kick, tente entrar no servidor usando esse convite: {invite.url}")
            await memb.kick(reason=f"expulso devido ao comando ,banrandom executado por {ctx.author}")
            await ctx.send(f"{ctx.author.mention} ele foi expulso.")

    @commands.command(aliases=["textao"])
    @commands.cooldown(1, 120.0, commands.BucketType.guild)
    async def textão(self, ctx):
        """Faz um textão do tamanho do pinto do João."""
        with ctx.typing():
            await asyncio.sleep(120)
        await ctx.channel.send("lacrei manas")
        await ctx.message.delete()

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def oibot(self, ctx):
        """Tá carente? Usa esse comando!"""
        await ctx.channel.send('Oieeeeee {}!'.format(ctx.message.author.name))

    @commands.command()
    @commands.cooldown(1, 10.0, commands.BucketType.member)
    async def enviar(self, ctx, user: discord.Member, *, msg: str):
        """Envia uma mensagem para a dm da pessoa mencionada.
        é necessário de que a DM dela esteja aberta."""
        try:
            files = [await att.to_file() for att in ctx.message.attachments]
            await user.send(msg, files=files)
            await user.send(embed=discord.Embed(title="Responda seu amigo (ou inimigo) anônimo!",
                                            description="Para responder use `,responder <mensagem>`",
                                            color=0xff0000))
            await ctx.message.delete()

        except discord.HTTPException:
            await ctx.reply("A mensagem não pôde ser enviada. Talvez o usuário esteja com a DM bloqueada.", delete_after=10)

        def check(message):
            msgcon = message.content.startswith(",responder")
            return message.author.id == user.id and message.guild is None and msgcon

        guild = self.client.get_guild(790744527450800139)
        channel = guild.get_channel(790744527941009480)

        enviar_embed = discord.Embed(title=",enviar usado.", description=ctx.message.content,
                            color=discord.Color.red())
        enviar_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await channel.send(embed=enviar_embed)


        try:
            message = await self.client.wait_for("message",
                                            check=check,
                                            timeout=300.0)
        except asyncio.TimeoutError:
            await user.send("Oh não! VocÊ demorou muito para responder. :sad:")
            pass
        else:
            con = " ".join(message.content.split(" ")[1:])

            embed = discord.Embed(
                title=f"E ele respondeu!",
                color=discord.Color.red(),
                description=con,
            )
            await message.add_reaction("👍")
            embed.set_author(name=str(user), icon_url=message.author.avatar_url)
            files = None
            if message.attachments:
                files = [await att.to_file() for att in message.attachments]

            await ctx.author.send(embed=embed, files=files)

def setup(client):
    client.add_cog(Misc(client))
    client.add_cog(Fun(client))
