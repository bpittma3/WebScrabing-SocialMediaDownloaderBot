from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import os
import requests
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import re

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
    options = Options()
    options.headless = True  # Run in headless mode

    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://publer.io/tools/media-downloader")

        url_input = driver.find_element_by_name("url")
        url_input.send_keys(link)
        url_input.send_keys(Keys.RETURN)

        driver.implicitly_wait(10)

        video_element = driver.find_element_by_tag_name("video")
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
        driver.quit()

def main():
    BOT_TOKEN = os.getenv("7921364353:AAEfny8GCC0S-OGl2SeLto7w3AtDjg6DnDQ")
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
