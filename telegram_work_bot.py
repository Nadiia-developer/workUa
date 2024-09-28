import logging
import emoji
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from resume_parser import get_all_resumes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

JOB_POSITION, SKILLS, KEYWORDS, SUMMARY = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Python Developer"]]

    await update.message.reply_text(
        "<b>Welcome to the Work Bot!\n"
        "Let's get some details about the candidate you're finding.\n"
        "Who is your candidate?</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )

    return JOB_POSITION


async def job_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data["job_position"] = update.message.text
    position = {"Python Developer": emoji.emojize("\U0001F40D")}
    logger.info("Position type of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        f"<b>You selected {update.message.text} {position[update.message.text]} candidate.\n"
        f"Would you like to fill in keywords for your candidate?</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    keyboard = [
        [InlineKeyboardButton("Fill", callback_data="Fill")],
        [InlineKeyboardButton("Skip", callback_data="Skip")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "<b>Choose an option:</b>", parse_mode="HTML", reply_markup=reply_markup
    )

    return SKILLS


async def skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    decision = query.data

    if decision == "Fill":
        await query.edit_message_text(
            text="<b>Please type keywords (e.g., python):</b>", parse_mode="HTML"
        )
        return KEYWORDS
    else:
        await query.edit_message_text(
            text="<b>Keywords step skipped.</b>", parse_mode="HTML"
        )
        context.user_data["keywords"] = "Not provided"
        return await summary(update, context)


async def keywords(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["keywords"] = update.message.text
    await update.message.reply_text("<b>Keywords noted.</b>", parse_mode="HTML")
    return await summary(update, context)


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selections = context.user_data
    summary_text = (
        f"<b>Here's what you told me about your candidate:\n</b>"
        f"<b>Job Position:</b> {selections.get('job_position')}\n"
        f"<b>Keywords:</b> {selections.get('keywords')}\n"
    )
    logging.info(f"Summary text: {summary_text}")
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id, text=summary_text, parse_mode="HTML"
    )

    resumes = await fetch_resumes(update, context)
    for resume in resumes:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"<b>Title:</b>{resume.title}\n"
            f"<b>Name:</b>{resume.name}\n"
            f"<b>Years:</b>{resume.years}\n"
            f"<b>Location:</b>{resume.location}\n"
            f"<b>Skills:</b>{','.join(resume.skills)}\n",
            parse_mode="HTML",
        )

    return ConversationHandler.END


async def fetch_resumes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> list:
    service = Service("path/to/chromedriver")
    chrome_options = Options()

    driver = webdriver.Chrome(service=service, options=chrome_options)
    resumes = get_all_resumes(driver)
    for resume in resumes:
        print(resume)

    return resumes


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bye! Hope to talk to you again soon.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    application = (
        Application.builder()
        .token("YOUR_BOT_TOKEN")
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            JOB_POSITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, job_position)
            ],
            SKILLS: [CallbackQueryHandler(skills)],
            KEYWORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, keywords)],
            SUMMARY: [MessageHandler(filters.ALL, summary)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == "__main__":
    main()
