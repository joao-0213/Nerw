from discord.ext import commands
from typing import Optional
from copy import deepcopy
import bot
import discord

class Help(commands.Cog, name="Ajuda"):
    def __init__(self, client: commands.Bot):
        self.prefix = bot.get_prefix()
        self.client = client

    def get_command_help(self, ctx, command):
        if command is None:
            raise ValueError

        if isinstance(ctx.me, discord.ClientUser):
            color = discord.Color.from_rgb(230, 0, 0)
        else:
            color = ctx.me.color

        aliases_copy = deepcopy(command.aliases)
        embed = discord.Embed(title=command.qualified_name,
                              description=command.usage,
                              color=color)

        alal = "|".join(aliases_copy)

        embed.add_field(name="Descrição", value=command.help if command.help is not None else "Nenhuma ajuda disponível")
        embed.add_field(name="Apelidos", value=alal if alal != "" else "Nenhum", inline=False)
        embed.add_field(name="Argumentação", value=f"`{command.qualified_name} {command.signature}`", inline=True)
        return embed

    def get_subcommand_help(self, ctx, command: commands.Group):
        embed = self.get_command_help(ctx, command)
        cmds = command.commands
        scheme = []

        for cmd in cmds:
            scheme.append(f"`,{command.qualified_name} {cmd.name}`")
        embed.add_field(name="Subcomandos", value="\n".join(scheme))

        return embed

    def get_hidden_commands(self):
        return list(filter(lambda command : command.enabled, self.client.commands))

    @commands.command(name="helpall")
    async def _help(self, ctx, *, cmd: Optional[str]):
        if isinstance(ctx.me, discord.ClientUser):
            color = discord.Color.from_rgb(230, 0, 0)
        else:
            color = ctx.me.color
        permissions = discord.Permissions(administrator=True)
        url = discord.utils.oauth_url(self.client.user.id, permissions)
        eb = discord.Embed(color=color)
        eb.set_author(name="Me convide para o seu servidor!", url=url)

        filt = filter(lambda command: not command.hidden, self.client.commands)
        eb.description = " | ".join(map(lambda command: f"`{command.name}`", filt))

    @commands.command(name="help")
    async def _help(self, ctx, *, cmd: Optional[str]):
        """Mostra essa mensagem."""

        if cmd is None:
            permissions = discord.Permissions(administrator=True)
            url = discord.utils.oauth_url(self.client.user.id, permissions)
            if bot.is_canary():
                eb = discord.Embed(color=0x04c312)
            else:
                eb = discord.Embed(color=0xed0467)
            eb.description = f"Prefixo no servidor: `{self.prefix}`"
            eb.set_author(name="Clique aqui para me adicionar ao seu servidor!", url=url, icon_url= self.client.user.avatar_url)
            eb.add_field(name="**Diversão:**", value="enviar | chatbot | selfmute | banrandom | snipe | kickrandom | textão | oibot", inline=False)
            eb.add_field(name="**Música:**", value="play | pause | leave | resume | queue | playdownload ",
                            inline=False)
            eb.add_field(name="**Utilidades:**",
                            value="shazam | ban | nick | botinfo | domin | kick | mover_mensagem | ping | tempo | invite",
                            inline=False)
            eb.add_field(name="**Imagens:**", value=" sus | marry | mememan | xvidros", inline=False)
            eb.add_field(name="**Xadrez:**", value="xadrez_iniciar | xadrez_rank | xadrez | xadrez_espectar\n⠀⠀⠀⠀⠀⠀⠀",
                            inline=False)
            eb.set_footer(text=f"Use {self.prefix}help <comando> para mais informações.")
            appinfo = await self.client.application_info()
            if ctx.author.id in list(map(lambda user : user.id, appinfo.team.members)):
                filt = filter(lambda command: command.hidden, self.client.commands)
                cmds = list(map(lambda command: f"`{command.name}`", filt))
                all_commands = " | ".join(cmds)

                hidden_embed = discord.Embed(title=":detective:", description=all_commands)
                await ctx.author.send(embed=hidden_embed)

            await ctx.reply(embed=eb)
        else:
            try:
                command = self.client.get_command(cmd)
                if isinstance(command, commands.Group):
                    hlp = self.get_subcommand_help(ctx, command)
                elif isinstance(command, commands.Command):
                    hlp = self.get_command_help(ctx, command)
            except ValueError:
                await ctx.reply(f"Não existe nenhum comando com o nome **{cmd}**.")
                return
            else:
                try:
                    await ctx.reply(embed=hlp)
                except UnboundLocalError:
                    return await ctx.reply(f"Não existe nenhum comando com o nome **{cmd}**.")

def setup(client):
    client.add_cog(Help(client))