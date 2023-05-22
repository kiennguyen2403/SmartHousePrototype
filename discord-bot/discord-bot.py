from voicecommand import *
import threading
import os

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from GPTWrapper import ask

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
##########################
class RecordingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        language_code = "en-US"  # a BCP-47 language tag
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            listen_print_loop(responses)

###############

@bot.hybrid_command(help='Join the voice server')
async def join(ctx):
    
    channel = ctx.author.voice.channel
    voice_client = await channel.connect()
    recordingThread = RecordingThread()
    recordingThread.start()
    await ctx.send(f'Joined {channel}')

@bot.hybrid_command(help='Leave the voice server')
async def leave(ctx):
    await ctx.voice_client.disconnect()



@bot.hybrid_command()
async def ping(ctx):
    await ctx.send('pong')


@bot.hybrid_command(help='Show the current temperature and humidity')
async def get_temperture_humidity(ctx):
    data = await fetch_temperature_humidity()
    result = ask("Notifying the user about the fetching temperature and humidity",
                 f'**Temperature**: {data["temperature"]} C\n**Humidity**: {data["humidity"]} %')
    await ctx.send(result)


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
    result = ask("Notifying the user about the status of the lighting",
                 f'**Light**: {state}')
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
    result = ask("Notifying the user about the status of the fan and heater",
                 f'**Fan**: {fan_state}\n**Heater**: {heater_state}')
    await ctx.send(result)


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
