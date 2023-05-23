import os
import logging
import datetime

from datetime import date
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
    def __init__(self, number: int, category: str, date_time: date = None):
        self.number = number
        self.category = category
        self.datetime = date_time

    def __str__(self):
        if self.number >= 0:
            return f"Income: {self.number}, Category: {self.category}, Date: {self.datetime}"
        else:
            return f"Expense: {self.number}, Category: {self.category}, Date: {self.datetime}"


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
        "Statistic expense: /statistic_expense <category>, <day, week, month, or year>\n"
        "Statistic income: /statistic_income <category>, <day, week, month, or year>\n"
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
        expenses = Finance(int(finances), category, date.today())
        with open('expense.txt', 'a') as f:
            f.write(f'{expenses}\n')
        await update.message.reply_text(f"Your add {expenses}")

    else:
        expenses = Finance(int(finances), category, date.today())
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


async def statistic_expense(update: Update, context: CallbackContext) -> None:
    await statistic(update, context, "expense.txt")


async def statistic_income(update: Update, context: CallbackContext) -> None:
    await statistic(update, context, "income.txt")


async def statistic(update: Update, context: CallbackContext, data_file: str) -> None:
    user_input = "".join(context.args).split(",")

    category = user_input[0]
    period = user_input[1]

    if period not in ["day", "week", "month", "year"]:
        await update.message.reply_text("The period specified is incorrect. Select: day, week, month or year")
        return

    total_expenses = 0

    with open(data_file, 'r') as f:
        lines = f.readlines()

        today = datetime.date.today()

        for line in lines:
            fields = line.strip().split(',')
            item_category = fields[1].split(': ')[1]
            amount = int(fields[0].split(': ')[1])

            if item_category != category:
                continue

            data = fields[2].split(': ')[1]
            datetime_obj = datetime.datetime.strptime(data, "%Y-%m-%d").date()

            if period == "day":
                if datetime_obj == today:
                    total_expenses += amount
            elif period == "week":
                start_of_week = today - datetime.timedelta(days=today.weekday())
                end_of_week = start_of_week + datetime.timedelta(days=6)
                if start_of_week <= datetime_obj <= end_of_week:
                    total_expenses += amount
            elif period == "month":
                if datetime_obj.year == today.year and datetime_obj.month == today.month:
                    total_expenses += amount
            elif period == "year":
                if datetime_obj.year == today.year:
                    total_expenses += amount

    if total_expenses == 0:
        await update.message.reply_text(f"No expenses found for the category {category} during {period}")
    else:
        await update.message.reply_text(f"Total expenses for {period} and category {category}: {total_expenses}")


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
    app.add_handler(CommandHandler("statistic_expenses", statistic_expense))
    app.add_handler(CommandHandler("statistic_incomes", statistic_income))
    app.run_polling()


if __name__ == "__main__":
    run()
