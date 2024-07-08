from playwright.sync_api import sync_playwright
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import re
import requests
import os


def handle_text_message(update: Update, context: CallbackContext):
    text = update.message.text
    link_match = re.search(r'(https?://[^\s]+)', text)

    if link_match:
        link = link_match.group(0)
        update.message.reply_text("Collecting the video...")
        download_and_send_video(link, update.message.chat_id, update, context)
    else:
        update.message.reply_text("This message does not contain a link.")

def download_and_send_video(link, chat_id, update: Update, context: CallbackContext):

    with sync_playwright() as p:
        try:
            browser = p.firefox.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Open The Page
            page.goto("https://publer.io/tools/media-downloader", timeout=60000)

            page.press('input[name="url"]', 'Enter')
            page.fill('input[name="url"]', link)
            page.press('input[name="url"]', 'Enter')

            # Click the Button
            page.click('button[type="submit"]')

            page.wait_for_load_state("load")

            # Wait for video to be ready
            page.wait_for_selector("video")

            # Get video element and source URL
            video_element = page.query_selector("video")
            video_source = video_element.get_attribute("src")

            if video_source:
                update.message.reply_text("Sending the video...")
                try:
                    BOT_TOKEN = os.getenv("BOT_TOKEN")
                    telegram_bot_token = BOT_TOKEN
                    bot = Bot(token=telegram_bot_token)
                    response = requests.get(video_source, stream=True)
                    if response.status_code == 200:
                        bot.send_video(chat_id=update.effective_chat.id, video=response.raw)
                    else:
                        raise Exception(f"Failed to download video. Status code: {response.status_code}")

                except Exception as e:
                    update.message.reply_text(f'Error sending video link: {str(e)}')

            else:
                raise Exception("Video source not found in the HTML.")

        except Exception as e:
            update.message.reply_text(f'Error: {str(e)}')

        finally:
            browser.close()

def main():
    # Write Your Bot Token
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(token=BOT_TOKEN, use_context=True) 
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))

    # Start The Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()