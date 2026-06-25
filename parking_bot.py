import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ── Конфигурация ──────────────────────────────────────────────────────────────
BOT_TOKEN = "8982540662:AAG9aoodMapaqoI9GgAUs_2H4ykoDpq501g"
ADMIN_ID = 223112207
SITE_URL = "https://sevilla-parking.github.io/sevilla-parking/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Тексты разделов ───────────────────────────────────────────────────────────
TEXTS = {
    "main": (
        "👋 Привет! Это сервис шеринга машиномест в *Испанских кварталах 2*.\n\n"
        "Соседи сдают и находят парковку напрямую — без посредников, "
        "без регистрации, бесплатно.\n\n"
        "👇 Выберите раздел:"
    ),

    "how": (
        "📋 *Как пользоваться сервисом*\n\n"
        "Сервис — это доска объявлений для соседей.\n\n"
        "• Уезжаете на несколько дней? Сдайте своё место соседу\n"
        "• Нужна парковка для гостей? Оставьте запрос\n"
        "• Сервис автоматически находит совпадения по датам\n\n"
        "Всё анонимно — телефон и номер квартиры не нужны.\n"
        "Расчёты напрямую между соседями — сервис платежи не проводит.\n\n"
        f"👉 Открыть сервис: {SITE_URL}"
    ),

    "offer": (
        "🚗 *Как сдать машиноместо*\n\n"
        "1. Откройте сервис и перейдите на вкладку *«Сдают»*\n"
        "2. Нажмите кнопку *«+ Сдать место»*\n"
        "3. Укажите даты — с какого по какое число место свободно\n"
        "4. Укажите цену за сутки (необязательно)\n"
        "5. Выберите секцию бегунком от 1 до 11\n"
        "6. Нажмите *«Опубликовать»*\n"
        "7. Сохраните код — он понадобится чтобы зайти в карточку\n\n"
        "⚠️ Указывайте только секцию, без номера места — "
        "точный номер называйте арендатору лично при встрече.\n\n"
        f"👉 {SITE_URL}"
    ),

    "request": (
        "🔍 *Как найти машиноместо*\n\n"
        "1. Откройте сервис и перейдите на вкладку *«Ищут»*\n"
        "2. Нажмите *«+ Оставить запрос»*\n"
        "3. Укажите даты — когда нужна парковка\n"
        "4. Выберите причину из списка\n"
        "5. Нажмите *«Опубликовать»* и сохраните код\n\n"
        "После публикации:\n"
        "• Сервис автоматически покажет совпадения с теми кто сдаёт\n"
        "• Нажмите *«Откликнуться»* на подходящую карточку\n"
        "• Укажите имя и как с вами связаться\n"
        "• Автор карточки увидит ваш контакт и напишет вам\n\n"
        f"👉 {SITE_URL}"
    ),

    "matches": (
        "✨ *Вкладка «Совпадения»*\n\n"
        "Это умная функция сервиса — она автоматически находит "
        "пары «сдают + ищут» с пересекающимися датами.\n\n"
        "Например:\n"
        "• Сосед сдаёт место с 5 по 10 июля\n"
        "• Вы ищете место с 6 по 8 июля\n"
        "• Сервис сам покажет это совпадение на вкладке\n\n"
        "Откликнуться можно прямо оттуда — не нужно искать карточки вручную.\n\n"
        f"👉 {SITE_URL}"
    ),

    "code": (
        "🔑 *Потеряли код карточки?*\n\n"
        "Код — это ваш личный доступ к карточке. "
        "Без него нельзя посмотреть отклики или закрыть карточку.\n\n"
        "*Что делать:*\n\n"
        "1. Откройте сервис\n"
        "2. Прокрутите вниз до формы *«Есть идея улучшения?»*\n"
        "3. Напишите: «Потерял код, мои даты: ...»\n"
        "4. Организатор найдёт вашу карточку и поможет\n\n"
        "Или напишите прямо сюда — нажмите кнопку «Задать вопрос» ниже.\n\n"
        "💡 *Совет на будущее:* после публикации карточки "
        "используйте кнопку ⎙ чтобы отправить код себе в Telegram."
    ),

    "safety": (
        "🛡 *Безопасность*\n\n"
        "*Деньги:*\n"
        "• Не переводите деньги заранее\n"
        "• Сначала договоритесь о встрече и убедитесь что место реальное\n"
        "• Все расчёты напрямую между соседями — сервис платежи не проводит\n\n"
        "*Личные данные:*\n"
        "• Не указывайте телефон и номер квартиры в карточке\n"
        "• Доска видна всем у кого есть ссылка\n"
        "• Контакты из откликов видны только автору карточки\n\n"
        "*Номер места:*\n"
        "• Указывайте только секцию, без номера места\n"
        "• Точный номер называйте арендатору лично при встрече\n\n"
        "Все соседи — жители одного дома. "
        "Доверие строится на репутации внутри сообщества."
    ),
}

# ── Клавиатуры ────────────────────────────────────────────────────────────────
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Как пользоваться", callback_data="how")],
        [InlineKeyboardButton("🚗 Сдать место", callback_data="offer"),
         InlineKeyboardButton("🔍 Найти место", callback_data="request")],
        [InlineKeyboardButton("✨ Совпадения", callback_data="matches")],
        [InlineKeyboardButton("🔑 Потерял код", callback_data="code"),
         InlineKeyboardButton("🛡 Безопасность", callback_data="safety")],
        [InlineKeyboardButton("💬 Задать вопрос", callback_data="ask")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("← Назад в меню", callback_data="main")]
    ])

def ask_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("← Назад в меню", callback_data="main")]
    ])

# ── Обработчики ───────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TEXTS["main"],
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main":
        await query.edit_message_text(
            TEXTS["main"],
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
    elif data == "ask":
        await query.edit_message_text(
            "💬 *Задать вопрос организатору*\n\n"
            "Напишите ваш вопрос следующим сообщением — "
            "организатор получит его и ответит в ближайшее время.",
            parse_mode="Markdown",
            reply_markup=ask_keyboard()
        )
        context.user_data["waiting_question"] = True
    elif data in TEXTS:
        await query.edit_message_text(
            TEXTS[data],
            parse_mode="Markdown",
            reply_markup=back_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_name = user.first_name or "Пользователь"
    text = update.message.text

    # Если пользователь нажал «Задать вопрос» и пишет вопрос
    if context.user_data.get("waiting_question"):
        context.user_data["waiting_question"] = False

        # Пересылаем организатору
        try:
            await context.bot.send_message(
                ADMIN_ID,
                f"❓ Вопрос от {user_name} (@{user.username or 'нет username'}, "
                f"ID: {user.id}):\n\n«{text}»"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение администратору: {e}")

        await update.message.reply_text(
            "✅ Вопрос отправлен организатору!\n\n"
            "Ответ придёт в этот чат в ближайшее время.",
            reply_markup=main_keyboard()
        )
        return

    # Любое другое сообщение — показываем меню
    await update.message.reply_text(
        TEXTS["main"],
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ── Запуск ────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
