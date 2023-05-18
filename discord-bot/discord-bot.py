import os

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))
API_URL = os.getenv('API_URL')
INDOOR_ENV_DEVICE = os.getenv('INDOOR_ENV')
LIGHTING_DEVICE = os.getenv('LIGHTING')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
CHANNEL_ID = int(str(os.getenv('CHANNEL_ID')))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

bearer_token = ''


@bot.hybrid_command()
async def ping(ctx):
    await ctx.send('pong')


@bot.hybrid_command(help='Show the current temperature and humidity')
async def get_temperture_humidity(ctx):
    data = await fetch_temperature_humidity()
    await ctx.send(f'**Temperature**: {data["temperature"]} C\n**Humidity**: {data["humidity"]} %')


async def fetch_temperature_humidity():
    keys = '%2C'.join(['temperature', 'humidity'])
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{API_URL}/api/plugins/telemetry/DEVICE/{INDOOR_ENV_DEVICE}/values/timeseries?keys={keys}&useStrictDataTypes=true',
            headers={'X-Authorization': f'Bearer {bearer_token}'}
        ) as response:
            data = await response.json()
            return {
                'temperature': data['temperature'][0]["value"],
                'humidity': data['humidity'][0]["value"]
            }


@bot.hybrid_command(help='Show the current lighting status')
async def get_lighting_status(ctx):
    data = await fetch_lighting_status()
    state = 'ON' if data == 1 else 'OFF'
    await ctx.send(f'**Light**: {state}')


async def fetch_lighting_status():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{API_URL}/api/plugins/telemetry/DEVICE/{LIGHTING_DEVICE}/values/timeseries?keys=light&useStrictDataTypes=true',
            headers={'X-Authorization': f'Bearer {bearer_token}'}
        ) as response:
            data = await response.json()
            return data['light'][0]["value"]


@bot.hybrid_command(help='Show the current fan and heater status')
async def get_fan_heater_status(ctx):
    data = await fetch_fan_heater_status()
    fan_state = 'ON' if data['fan'] else 'OFF'
    heater_state = 'ON' if data['heater'] else 'OFF'
    await ctx.send(f'**Fan**: {fan_state}\n**Heater**: {heater_state}')


async def fetch_fan_heater_status():
    keys = '%2C'.join(['fan', 'heater'])
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{API_URL}/api/plugins/telemetry/DEVICE/{INDOOR_ENV_DEVICE}/values/timeseries?keys={keys}&useStrictDataTypes=true',
            headers={'X-Authorization': f'Bearer {bearer_token}'}
        ) as response:
            data = await response.json()
            return {
                'fan': data['fan'][0]["value"],
                'heater': data['heater'][0]["value"]
            }


@tasks.loop(minutes=5)
async def update_data():
    channel = bot.get_channel(CHANNEL_ID)
    temp_humid_data = await fetch_temperature_humidity()
    lighting_data = await fetch_lighting_status()
    fan_heater_data = await fetch_fan_heater_status()
    light_state = 'ON' if lighting_data == 1 else 'OFF'
    fan_state = 'ON' if fan_heater_data['fan'] else 'OFF'
    heater_state = 'ON' if fan_heater_data['heater'] else 'OFF'
    await channel.send(f'**Temperature**: {temp_humid_data["temperature"]} C\n**Humidity**: {temp_humid_data["humidity"]} %\n**Light**: {light_state}\n**Fan**: {fan_state}\n**Heater**: {heater_state}') # type: ignore


async def login():
    global bearer_token
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{API_URL}/api/auth/login',
            json={'username': USERNAME, 'password': PASSWORD}
        ) as response:
            data = await response.json()
            bearer_token = data['token']


@bot.event
async def on_ready():
    await login()
    await bot.tree.sync()
    print('Bot is ready')
    await update_data.start()


if __name__ == '__main__':
    bot.run(TOKEN)
