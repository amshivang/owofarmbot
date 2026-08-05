import time
from discord.ext import commands

class FarmCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def start(self, ctx):
        if self.bot.is_farming:
            return await ctx.send("Already farming! Use .stop first.")
        
        self.bot.target_channels = [ctx.channel]
        self.bot.current_channel_index = 0
        self.bot.is_farming = True
        self.bot.start_session()
        self.bot.farm_task = self.bot.loop.create_task(self.bot._farm_runner())
        
        await ctx.send(f"Farming started! Duration: ~2 hours.")

    @commands.command()
    async def owo(self, ctx, *channel_ids: str):
        if self.bot.is_farming:
            return await ctx.send("Already farming! Use .stop first.")
        
        if not channel_ids:
            return await ctx.send("Provide at least one channel ID: .owo <id> [id...]")
            
        channels = []
        for cid in channel_ids:
            ch = self.bot.get_channel(int(cid))
            if not ch: return await ctx.send(f"Invalid channel ID: {cid}")
            channels.append(ch)
            
        self.bot.target_channels = channels
        self.bot.current_channel_index = 0
        self.bot.is_farming = True
        self.bot.start_session()
        self.bot.farm_task = self.bot.loop.create_task(self.bot._farm_runner())
        
        await ctx.send(f"Farming started across {len(channels)} channels!")

    @commands.command()
    async def stop(self, ctx):
        if self.bot.is_farming:
            self.bot.is_farming = False
            if self.bot.farm_task: 
                self.bot.farm_task.cancel()
            await ctx.send("Farming stopped.")
        else:
            await ctx.send("Not currently farming.")

    @commands.command()
    async def resume(self, ctx):
        if self.bot.is_farming:
            return await ctx.send("Already farming.")
        
        self.bot.is_farming = True
        if self.bot.on_break or self.bot.on_rest:
            self.bot.on_break = False
            self.bot.on_rest = False
            self.bot.start_session() # reset session timers
            await ctx.send("Resumed from break/rest!")
        else:
            if not self.bot.target_channels:
                self.bot.target_channels = [ctx.channel]
            self.bot.start_session()
            await ctx.send("Resumed farming!")
            
        self.bot.farm_task = self.bot.loop.create_task(self.bot._farm_runner())

    @commands.command()
    async def status(self, ctx):
        if self.bot.is_farming:
            elapsed = int(time.time() - self.bot.start_time)
            rem = int(max(0, self.bot.session_end_time - time.time()))
            await ctx.send(f"**Running** | Uptime: {elapsed//3600}h {(elapsed%3600)//60}m | Next break in: {rem//3600}h {(rem%3600)//60}m")
        elif self.bot.on_break:
            rem = int(max(0, self.bot.break_end_time - time.time()))
            await ctx.send(f"**On Break** | Ends in: {rem//3600}h {(rem%3600)//60}m")
        elif self.bot.on_rest:
            rem = int(max(0, self.bot.rest_end_time - time.time()))
            await ctx.send(f"**On Rest** | Ends in: {rem//3600}h {(rem%3600)//60}m")
        else:
            await ctx.send("**Stopped**.")

async def setup(bot):
    await bot.add_cog(FarmCommands(bot))
