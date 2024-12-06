from telethon import TelegramClient, events

# Remember to use your own values from my.telegram.org!
api_id = 1025907
api_hash = '452b0359b988148995f22ff0f4229750'
proxy_port = 1081
client = TelegramClient('anon', api_id, api_hash,
                        proxy=("socks5", '127.0.0.1', proxy_port))


@client.on(events.NewMessage)
async def my_event_handler(event):
    sender = await event.get_sender()
    chat_id = event.chat_id

    if chat_id == -4619464166:
        print(event.raw_text)
        print()
        print()
        print(sender.first_name)
        print(sender.last_name)
        if 'hello' in event.raw_text:
            await event.respond('hi!')

client.start()
client.run_until_disconnected()
