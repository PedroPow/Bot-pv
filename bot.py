from discord.ext import commands
from discord.ui import View, Button, Select, Modal, TextInput
from discord import Embed
import asyncio
import os
import aiohttp
import io
import discord

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

CARGO_OFICIAL = 1449985109116715008
CANAL_COMUNICACAO = 1479197215854559385

# ============================
# TOKEN
# ============================
TOKEN = os.getenv("TOKEN")  # coloque TOKEN no .env


class PainelComunicacao(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="📡 Enviar Comunicado",
        style=discord.ButtonStyle.gray,
        custom_id="botao_comunicado"
    )
    async def enviar(self, interaction: discord.Interaction, button: discord.ui.Button):

        if CARGO_OFICIAL not in [cargo.id for cargo in interaction.user.roles]:

            await interaction.response.send_message(
                "❌ Apenas oficiais podem usar este sistema.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Selecione os policiais:",
            view=SelecionarPolicial(),
            ephemeral=True
        )


class SelecionarPolicial(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SelectPolicial())


class SelectPolicial(discord.ui.UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="🔎 Buscar policiais...",
            min_values=1,
            max_values=10
        )

    async def callback(self, interaction: discord.Interaction):

        policiais = self.values

        await interaction.response.send_modal(
            ModalComunicado(policiais)
        )


class ModalComunicado(discord.ui.Modal, title="Comunicado Interno SSP"):

    mensagem = discord.ui.TextInput(
        label="Mensagem",
        style=discord.TextStyle.paragraph
    )

    def __init__(self, policiais):
        super().__init__()
        self.policiais = policiais

    async def on_submit(self, interaction: discord.Interaction):

        enviados = 0

        for policial in self.policiais:

            embed = discord.Embed(
                title="**Comunicação Interna - SSP**\n\n",
                description=self.mensagem.value,
                color=discord.Color.dark_gray()
            )

            embed.set_image(
                url="https://cdn.discordapp.com/attachments/1444735189765849320/1474956398235353108/Logo_SSP.png?ex=69aae4f0&is=69a99370&hm=1a549690277ae1bb157c4d21b1faace1ec5adbb1d05696a5d76423b0154b012e&"
            )

            embed.set_footer(text="Batalhão Rota Virtual® Todos direitos reservados.")

            try:
                await policial.send(embed=embed)
                enviados += 1
            except:
                pass

        await interaction.response.send_message(
            f"✅ Comunicado enviado para {enviados} policiais.",
            ephemeral=True
        )


@bot.event
async def on_ready():

    print("BOT ONLINE")

    bot.add_view(PainelComunicacao())

    canal = bot.get_channel(CANAL_COMUNICACAO)

    if canal is None:
        print("❌ Canal não encontrado.")
        return

    embed = discord.Embed(
        title="Central de Comunicação - SSP",
        description="Sistema utilizado pelos oficiais para envio de comunicados internos.\n\n"
        "Neste canal você poderá enviar mensagens para os Policiais pelo nosso Sistema do SSP\n\n"
        "Qualquer duvida, tira-las no <#1475647625289142544>\n\n"
        "_Dignidade Acima de Tudo_",
        color=discord.Color.blue()
    )

    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1444735189765849320/1474956398235353108/Logo_SSP.png?ex=69aae4f0&is=69a99370&hm=1a549690277ae1bb157c4d21b1faace1ec5adbb1d05696a5d76423b0154b012e&"
    )

    embed.set_footer(text="Batalhão Rota Virtual® Todos direitos reservados.")

    painel_encontrado = None

    async for mensagem in canal.history(limit=50):

        if mensagem.author == bot.user and mensagem.components:

            painel_encontrado = mensagem
            break

    if painel_encontrado:

        await painel_encontrado.edit(embed=embed, view=PainelComunicacao())
        print("🔄 Painel atualizado.")

    else:

        await canal.send(embed=embed, view=PainelComunicacao())
        print("✅ Painel criado.")

    print(f"Bot conectado como {bot.user}")


# ============================
# RUN
# ============================
if not TOKEN:
    print("ERRO: TOKEN não definido.")
else:
    bot.run(TOKEN)