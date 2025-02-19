import discord
from discord.ext import commands
import requests
from urllib.parse import quote
import json
import os

class ReverseImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monitor_channel_id = None
        self.result_channel_id = None
        
        if not os.path.exists('log.json'):
            self.log_ids(None, None, None)
        
        try:
            with open('log.json', 'r') as f:
                data = json.load(f)
                self.monitor_channel_id = data.get('monitor_channel_id')
                self.result_channel_id = data.get('result_channel_id')
                print(f"Loaded channel IDs from log.json: Monitor={self.monitor_channel_id}, Result={self.result_channel_id}")
        except Exception as e:
            print(f"Error loading log.json: {e}")

    @discord.app_commands.command(name="setup", description="yur")
    @discord.app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction, monitor_channel: discord.TextChannel, result_channel: discord.TextChannel):
        self.monitor_channel_id = monitor_channel.id
        self.result_channel_id = result_channel.id
        self.log_ids(interaction.guild.id, monitor_channel.id, result_channel.id)
        await interaction.response.send_message(
            f'Setup complete! Monitoring images in {monitor_channel.mention} and sending results to {result_channel.mention}.'
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.monitor_channel_id and message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith('image/'):
                    await self.process_image(attachment.url, message)

    async def process_image(self, image_url, message):
        google_lens_url = f"https://lens.google.com/uploadbyurl?url={quote(image_url)}"
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        
        result_channel = self.bot.get_channel(self.result_channel_id)
        if result_channel:
            embed = discord.Embed(
                title="🚨 POTENTIAL CATFISH 🚨",
                description=f"**ATTENTION:** An image requiring verification has been detected.\n\n"
                           f"🔍 [Click here to reverse search]({google_lens_url})\n"
                           f"📱 [Go to original message]({message_link})\n\n"
                           f"⚠️ **Why this alert?**\n"
                           f"• Image verification helps prevent catfishing\n"
                           f"• Protects community members from scams\n"
                           f"• Ensures authentic interactions\n\n"
                           f"ℹ️ **Note:** Currently, all images are flagged for verification until an API is implemented. "
                           f"However, it's still important to check each image for community safety.",
                color=0xFF0000
            )
            embed.set_image(url=image_url)
            embed.add_field(
                name="📌 Source Information",
                value=f"• Posted by: {message.author.mention}\n"
                      f"• Channel: {message.channel.mention}\n"
                      f"• Time: <t:{int(message.created_at.timestamp())}:R>",
                inline=False
            )
            embed.set_footer(text="🛡️ We're reporting this as we have detected an issue. | Stay safe online!")
            view = VerificationView(original_message=message)
            await result_channel.send("Check for verification.", embed=embed, view=view)

    def log_ids(self, server_id, monitor_channel_id, result_channel_id):
        log_data = {
            "server_id": server_id,
            "monitor_channel_id": monitor_channel_id,
            "result_channel_id": result_channel_id
        }
        with open('log.json', 'w') as log_file:
            json.dump(log_data, log_file, indent=4)

class VerificationView(discord.ui.View):
    def __init__(self, original_message=None):
        super().__init__(timeout=None)
        self.original_message = original_message

    @discord.ui.button(style=discord.ButtonStyle.danger, label="Catfish", custom_id="catfish_button")
    async def catfish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ Marked as a Catfish. Original message has been deleted.", ephemeral=True)
        if self.original_message:
            try:
                await self.original_message.delete()
            except:
                await interaction.followup.send("Could not delete the original message.", ephemeral=True)
        self.disable_all_buttons()
        await interaction.message.edit(content="🚫 **Image has been confirmed as a Catfish and removed.**", view=self)

    @discord.ui.button(style=discord.ButtonStyle.danger, label="Clear", custom_id="clear_button")
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Image has been cleared!", ephemeral=True)
        embed = interaction.message.embeds[0]
        embed.title = "✅ VERIFIED CLEAR ✅"
        embed.color = discord.Color.green()
        self.disable_all_buttons()
        await interaction.message.edit(content="Image has been verified as safe.", embed=embed, view=self)

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True

def setup(bot):
    bot.add_cog(ReverseImage(bot))