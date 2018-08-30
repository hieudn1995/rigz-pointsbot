import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import os
import pickle
import operator

bot = commands.Bot(command_prefix="a.") 

@bot.event
async def on_ready():
  print(bot.user.name)

class BotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super(BotClient, self).__init__(*args, **kwargs)
        self.commands = {
            'prefix' : self.prefix,
            'ping' : self.ping,
            'add' : self.add,
            'remove' : self.remove,
            'view' : self.view,
            'help' : self.help,
            'viewladder' : self.viewladder
        }

        self.colours = {
        'server' : 0xaee25f,
        'error' : 0xff3700
        }

    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
        await client.change_presence(activity=discord.Game(name='use ?help'))


    async def ping(self, message, stripped):
        t = message.created_at.timestamp()
        e = await message.channel.send('pong')
        delta = e.created_at.timestamp() - t

        await e.edit(content='Pong! {}ms round trip'.format(round(delta * 1000)))


    async def on_guild_join(self, guild):
        os.mkdir('data/' + str(guild.id))
        with open('data/' + str(guild.id) + '/prefix', 'w') as f:
            f.write('!')
        dict = {}
        pve =  open('data/'+ str(guild.id) + '/pve.pickle', 'wb')
        pickle.dump(dict, pve)
        pve.close()
        pvp =  open('data/'+ str(guild.id) + '/pvp.pickle', 'wb')
        pickle.dump(dict, pvp)
        pvp.close()


    async def on_message(self, message):
        await self.getCommand(message)


    async def getCommand(self, message):
        with open('data/' + str(message.guild.id) + '/prefix', 'r') as f:
            self.prefix = f.read()
        if message.content[0:len(self.prefix)] == self.prefix:
            command = (message.content + ' ')[len(self.prefix):message.content.find(' ')]
            if command in self.commands:
                stripped = (message.content + ' ')[message.content.find(' '):].strip()
                await self.commands[command](message, stripped)
                return True
        return False


    async def prefix(self, message, stripped):
        if message.author.guild_permissions.administrator:
            if len(stripped) > 0:
                with open('data/' + str(message.guild.id) + '/prefix', 'w') as f:
                    f.write(stripped)
                embed = discord.Embed(description='Your prefix has been changed to: ' + str(stripped), color=self.colours['server'])
                await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(description='Please proceed the command "{}prefix " with the prefix you would like to use.'.format(self.prefix), color=self.colours['error'])
                await message.channel.send(embed=embed)


    async def add(self, message, stripped):
        if message.author.guild_permissions.administrator:
            async def _add(points, members, type):
                    pickleIn =  open('data/' + str(message.guild.id) + '/{}.pickle'.format(type), 'rb')
                    ladder = pickle.load(pickleIn)
                    pickleIn.close()
                    for n in members:
                        check = ladder.get(n, 0)
                        if check == 0:
                            ladder[n] = int(points)
                        elif check != 0:
                            ladder[n] = int(check) + int(points)
                        await message.channel.send(embed=discord.Embed(description='Member: <@' + str(n) + '> was on ' + str(check) + ' points and is now on ' + str(ladder[n]) + ' points.', color=self.colours['server']))

                    pickleSave =  open('data/'+ str(message.guild.id) + '/{}.pickle'.format(type), 'wb')
                    pickle.dump(ladder, pickleSave)
                    pickleSave.close()


            seperated = stripped.split(' ')
            points = seperated[0]
            if not points.isdigit():
                await message.channel.send(embed=discord.Embed(description="Error: You included something that wasn't an integer in your points.", color=self.colours['error']))
                return
            members = [x.id for x in message.mentions]
            if len(members) == 0:
                await message.channel.send(embed=discord.Embed(description="Error: You have not mentioned anyone in that command.", color=self.colours['error']))
                return
            type = seperated[len(seperated) - 1]
            if type != 'pve' and type != 'pvp':
                await message.channel.send(embed=discord.Embed(description='Error: Please specify either "pvp" or "pve" at the end of that command', color=self.colours['error']))
                return
            else:
                await _add(points, members, type)


    async def remove(self, message, stripped):
        if message.author.guild_permissions.administrator:
            async def _remove(points, members, type):
                    pickleIn =  open('data/' + str(message.guild.id) + '/{}.pickle'.format(type), 'rb')
                    ladder = pickle.load(pickleIn)
                    pickleIn.close()
                    for n in members:
                        check = ladder.get(n, 0)
                        if check == 0:
                            await message.channel.send(embed=discord.Embed(description='Error: Member <@' + str(n) + '> is already on 0 points therefore no more can be taken away.', color=self.colours['error']))
                            return
                        elif check != 0:
                            newPoints = int(check) - int(points)
                            if newPoints < 0:
                                await message.channel.send(embed=discord.Embed(description='Error: Member <@' + str(n) + '> was already on ' + str(check) + ' points therefore ' + str(points) + ' can not be taken away as that would be less than 0.', color=self.colours['error']))
                                return
                            else:
                                ladder[n] = int(newPoints)
                        await message.channel.send(embed=discord.Embed(description='Member: <@' + str(n) + '> was on ' + str(check) + ' points and is now on ' + str(ladder[n]) + ' points.', color=self.colours['server']))

                    pickleSave =  open('data/'+ str(message.guild.id) + '/{}.pickle'.format(type), 'wb')
                    pickle.dump(ladder, pickleSave)
                    pickleSave.close()


            seperated = stripped.split(' ')
            points = seperated[0]
            if not points.isdigit():
                await message.channel.send(embed=discord.Embed(description="Error: You included something that wasn't an integer in your points.", color=self.colours['error']))
                return
            members = [x.id for x in message.mentions]
            if len(members) == 0:
                await message.channel.send(embed=discord.Embed(description="Error: You have not mentioned anyone in that command.", color=self.colours['error']))
                return
            type = seperated[len(seperated) - 1]
            if type != 'pve' and type != 'pvp':
                await message.channel.send(embed=discord.Embed(description='Error: Please specify either "pvp" or "pve" at the end of that command', color=self.colours['error']))
                return
            else:
                await _remove(points, members, type)


    async def view(self, message, stripped):
        async def _view(type):
            pickleIn =  open('data/' + str(message.guild.id) + '/{}.pickle'.format(type), 'rb')
            ladder = pickle.load(pickleIn)
            pickleIn.close()

            sortedTuple = sorted(ladder.items(), key = lambda t:t[1])
            sortedList = [list(item) for item in reversed(sortedTuple)]

            try:
                userIds, points = zip(*sortedList)
            except ValueError:
                await message.channel.send(embed=discord.Embed(description='Error: No users were found under this ladder.', color=self.colours['error']))
            userNames = []
            for n in userIds:
                userNames.append(str(self.get_user(n)) + '   |')

            j_userIds = '\n'.join(map(str, userNames))
            j_points = '\n'.join(map(str, points))

            embed = discord.Embed(title='{} Ladder'.format(type.upper()), color=self.colours['server'])
            embed.add_field(name='Username', value=j_userIds, inline=True)
            embed.add_field(name='Points', value=j_points, inline=True)
            await message.channel.send(embed=embed)

        print(stripped)
        if stripped == 'pve':
            type = 'pve'
            await _view(type)
        elif stripped == 'pvp':
            type = 'pvp'
            await _view(type)
        elif stripped == '':
            userId = message.author.id
            pickleIn =  open('data/' + str(message.guild.id) + '/pvp.pickle', 'rb')
            pvpLadder = pickle.load(pickleIn)
            pickleIn.close()
            pickleIn =  open('data/' + str(message.guild.id) + '/pve.pickle', 'rb')
            pveLadder = pickle.load(pickleIn)
            pickleIn.close()
            pvpCheck = pvpLadder.get(userId, 0)
            pveCheck = pveLadder.get(userId, 0)
            results = []
            if pvpCheck == 0 and pveCheck == 0:
                await message.channel.send(embed=discord.Embed(description='Your point score for both PVP and PVE is 0.', color=self.colours['server']))
                return

            if pvpCheck != 0:
                results.append('Your PVP point score is: ' + str(pvpCheck))
            else:
                results.append('Your PVP point score is: 0')

            if pveCheck != 0:
                results.append('Your PVE point score is: ' + str(pveCheck))
            else:
                results.append('Your PVE point score is: 0')

            stringResults = '\n'.join(results)

            await message.channel.send(embed=discord.Embed(description=stringResults, color=self.colours['server']))

    async def help(self, message, stripped):
        await message.channel.send(embed=discord.Embed(description='{0}help - show this menu\n{0}add <points> <@member> <pvp/pve> - add points (Council only)\n{0}remove <points> <@member> <pvp/pve> - remove points (Council only)\n{0}view - view personal scores\n{0}viewladder - URL for full ladder'.format(self.prefix), color=self.colours['server']))

    async def viewladder(self, message, stripped):
        await message.channel.send(embed=discord.Embed(description='Click this for the full ladder - https://goo.gl/MH6W3U'.format(self.prefix), color=self.colours['server']))





client = BotClient()
bot.run(str(os.environ.get('BOT_TOKEN')))
client.run("NDc2NzkwOTc2NzAzMTAyOTg2.DmlWtQ.HcxOGrpi4ZlVyliNpfSLV7zZFzw")
