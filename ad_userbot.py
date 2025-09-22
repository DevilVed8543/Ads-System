import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetDialogsRequest

# Replace with your credentials
api_id = 20251473
api_hash = 'ba6f9341005e1c9f09499e6323e3ff2e'
phone = '+919965826551'

# Channel and message
source_channel_username = '@forwarder69'  # e.g., 'mychannel'
message_id_to_copy = 2  # Message ID you want to copy (not forward)

# Auto-reply message
auto_reply_text = "Message at @DevilVed"

client = TelegramClient(phone, api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def auto_reply_handler(event):
    if event.is_private and not event.out:
        try:
            await event.respond(auto_reply_text)
            print(f"Auto-replied to {event.sender_id}")
        except Exception as e:
            print(f"Auto-reply failed: {e}")

async def copy_message_loop():
    await client.start(phone)

    # Get the source channel
    try:
        source_channel = await client.get_entity(source_channel_username)
    except Exception as e:
        print(f"Error getting source channel: {e}")
        return

    # Fetch the original message
    try:
        message = await client.get_messages(source_channel, ids=message_id_to_copy)
        if not message:
            print("Message not found!")
            return
    except Exception as e:
        print(f"Error fetching message: {e}")
        return

    while True:
        try:
            # Get your groups
            result = await client(GetDialogsRequest(
                offset_date=None,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=200,
                hash=0
            ))

            groups = [chat for chat in result.chats if getattr(chat, 'megagroup', False)]
            print(f"[COPYING] Sending to {len(groups)} groups...")

            for group in groups:
                try:
                    if message.text:
                        await client.send_message(group, message.text)
                        print(f"[SENT] to {group.title}")
                    elif message.media:
                        await client.send_file(group, file=message.media, caption=message.text or "")
                        print(f"[SENT FILE] to {group.title}")
                    else:
                        print(f"[SKIPPED] No supported content in message ID {message_id_to_copy}")
                except Exception as e:
                    print(f"[ERROR] Sending to {group.title}: {e}")

            print("[WAITING] Sleeping 30 minutes...")
            await asyncio.sleep(1800)

        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            await asyncio.sleep(60)

async def main():
    await asyncio.gather(
        copy_message_loop(),
    )

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
