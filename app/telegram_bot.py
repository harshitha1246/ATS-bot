from io import BytesIO
import asyncio
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.analysis.engine import analyze_documents
from app.chat.response_formatter import format_results
from app.documents.classifier import ClassificationError, classify_documents
from app.documents.text_extractor import DocumentExtractionError, extract_text

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["documents"] = []
    await update.message.reply_text(
        "Send me one job description and one or more resumes as files. "
        "When finished, send /analyze. Use /clear to start over."
    )


async def receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    filename = document.file_name or "uploaded_file"
    try:
        telegram_file = await context.bot.get_file(document.file_id)
        content = BytesIO()
        await telegram_file.download_to_memory(content)
        text = extract_text(filename, content.getvalue())
        context.user_data.setdefault("documents", []).append((filename, text))
        count = len(context.user_data["documents"])
        await update.message.reply_text(f"Added {filename}. I have {count} document(s). Send /analyze when ready.")
    except DocumentExtractionError as exc:
        await update.message.reply_text(f"I could not read {filename}: {exc}")


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    documents = context.user_data.get("documents", [])
    if len(documents) < 2:
        await update.message.reply_text("Please upload one JD and at least one resume first.")
        return
    try:
        classified = classify_documents(documents)
        analyses = analyze_documents(classified.jd[1], classified.resumes)
        await _send_results(update, classified.jd[0], format_results(analyses))
    except ClassificationError as exc:
        await update.message.reply_text(str(exc))


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["documents"] = []
    await update.message.reply_text("Cleared. Send a JD and resume files to begin again.")


async def _send_results(update: Update, jd_name: str, result: dict) -> None:
    lines = [f"JD identified: {jd_name}", "", "RANKING"]
    for item in result["ranking"]:
        lines.append(f"{item['rank']}. {item['resume']} - {item['score']}/100 ({item['alignment']})")
    for item in result["analyses"]:
        lines.extend([
            "", f"RESUME ANALYSIS: {item['resume_name']}",
            f"ATS SCORE: {item['score']}/100",
            f"JD ALIGNMENT: {item['alignment_rating']} - {item['alignment_percentage']}%",
            "MATCHED: " + (", ".join(item["matched_skills"]) or "None identified"),
            "MISSING: " + (", ".join(item["missing_skills"]) or "None identified"),
            "IMPORTANT GAPS: " + (", ".join(item["important_gaps"]) or "None identified"),
            "COURSES: " + (", ".join(item["course_recommendations"]) or "None recommended"),
        ])
    message = "\n".join(lines)
    for start in range(0, len(message), 3800):
        await update.message.reply_text(message[start : start + 3800])


def build_application() -> Application:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env before starting the Telegram bot.")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.Document.ALL, receive_document))
    return application


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    build_application().run_polling()