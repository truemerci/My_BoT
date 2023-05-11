import os
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler


TOKEN = "5972075747:AAEF3eI76CBMHhE1Hj18pNxbH_vupKdjyO8"
filename = "expense.txt"

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
)

list_categories = ["health", "food", "clothes", "other"]


class Finance:
    def __init__(self, number: int, category: str):
        self.number = number
        self.category = category

    def __str__(self):
        if self.number >= 0:
            return f"Income: {self.number} | Category: {self.category}"
        else:
            return f"Expense: {self.number} | Category: {self.category}"


async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Command start was triggered")
    await update.message.reply_text(
        "Welcome to my Bot!\n"
        "Commands:\n"
        "List categories: /categories\n"
        "Adding expense: /add -<number> | <category>\n"
        "Adding income: /add <number> | <category>\n"
        "List expense: /list_expenses\n"
        "List income: /list_incomes\n"
        "Remove expense: /remove_expenses <expense number>\n"
        "Remove income: /remove_incomes <income number>\n"
    )


async def categories(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(', '.join(list_categories))


async def add_expense_or_income(update: Update, context: CallbackContext) -> None:
    parts = "".join(context.args).split("|")
    try:
        finances = parts[0]
        category = parts[1]
    except (ValueError, IndexError):
        logging.error("Invalid format")
        await update.message.reply_text("Your format is invalid, please correct the format to \n"
                                        "/add <number> | <category>")
        return

    if int(finances) <= 0:
        if category not in list_categories:
            await update.message.reply_text(f"No such {category} category")
            return

        expenses = Finance(int(finances), category)
        with open('expense.txt', 'a') as f:
            f.write(f'{expenses}\n')
        await update.message.reply_text(f"Your add {expenses}")

    else:
        expenses = Finance(int(finances), category)
        with open('income.txt', 'a') as f:
            f.write(f'{expenses}\n')
        await update.message.reply_text(f"Your add {expenses}")


async def list_expense(update: Update, context: CallbackContext) -> None:
    await list_data(update, context, 'expense.txt', 'expenses')


async def list_income(update: Update, context: CallbackContext) -> None:
    await list_data(update, context, 'income.txt', 'incomes')


async def list_data(update: Update, context: CallbackContext, data_file: str, data_type: str) -> None:
    with open(data_file, 'r') as f:
        if os.path.getsize(data_file) == 0:
            await update.message.reply_text(f"You dont have any {data_type}")
            return
        result = "\n".join(f"{i}. {line.strip()}" for i, line in enumerate(f, 1))
        await update.message.reply_text(result)


async def remove_expense(update: Update, context: CallbackContext) -> None:
    await remove(update, context, "expense.txt")


async def remove_income(update: Update, context: CallbackContext) -> None:
    await remove(update, context, "income.txt")


async def remove(update: Update, context: CallbackContext, data_file: str) -> None:
    with open(data_file, 'r') as f:
        lines = f.readlines()
        try:
            index_to_delete = int(context.args[0]) - 1
            await update.message.reply_text(f"{lines[index_to_delete]}successfully remove")
            del lines[index_to_delete]
        except(ValueError, IndexError):
            logging.error("Invalid index")
            await update.message.reply_text("You entered invalid index")
            return
    with open(data_file, 'w') as f:
        for line in lines:
            f.write(line)
        f.truncate()


def run():
    app = ApplicationBuilder().token(TOKEN).build()
    logging.info("Application build successfully!")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("categories", categories))
    app.add_handler(CommandHandler("add", add_expense_or_income))
    app.add_handler(CommandHandler("list_expenses", list_expense))
    app.add_handler(CommandHandler("list_incomes", list_income))
    app.add_handler(CommandHandler("remove_expenses", remove_expense))
    app.add_handler(CommandHandler("remove_incomes", remove_income))

    app.run_polling()


if __name__ == "__main__":
    run()
