from telebot import types

from src.telegram.callbacks import (
    increment_value_from_callback_data,
    parse_increment_callback_data,
)
from src.telegram import bot
from src.utils.telebot import Keyboard, KeyboardFactory


@bot.callback_query_handler(func=lambda call: call.data.startswith("increment:"))
def handle_increment_callback(call: types.CallbackQuery):
    """
    Handles the callback for the incrementing button.
    Increments the value and updates the message with the new button.
    """
    try:
        # 1. Get the new callback data string (e.g., "increment:1")
        new_callback_data = increment_value_from_callback_data(call.data)

        # 2. Parse the integer value from the new data to update the button text
        new_value = parse_increment_callback_data(new_callback_data)

        # 3. Create the updated button
        updated_button = Keyboard(
            text=f"Value: {new_value}", callback_data=new_callback_data
        )
        updated_keyboard_markup = KeyboardFactory.from_keyboard([updated_button])

        # 4. Edit the original message with the new button
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Value has been updated:",
            reply_markup=updated_keyboard_markup,
        )

        # Answer the callback query to remove the "loading" state on the user's end
        bot.answer_callback_query(call.id, text=f"Value is now {new_value}")

    except Exception as e:
        print(f"Error in handle_increment_callback: {e}")
        bot.answer_callback_query(
            call.id, text="An error occurred while updating the value."
        )
