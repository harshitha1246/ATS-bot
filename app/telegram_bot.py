from hashlib import sha256
from io import BytesIO
import asyncio
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.analysis.engine import analyze_documents
from app.chat.response_formatter import format_results
from app.config import MAX_UPLOAD_MB
from app.documents.classifier import ClassificationError, classify_document_type, classify_documents
from app.documents.text_extractor import DocumentExtractionError, extract_text

load_dotenv()


def _reset(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data["resumes"] = []
    context.user_data["fingerprints"] = set()


def _fingerprint(text: str) -> str:
    return sha256(text.strip().lower().encode("utf-8")).hexdigest()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _reset(context)
    await update.message.reply_text(
        "Send one JD and at least one resume as files. I will guide you after each upload. "
        "Use /clear to start over."
    )


async def receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    filename = document.file_name or "uploaded_file"
    pending = context.user_data.get("pending_document")
    if pending:
        await update.message.reply_text("Please choose whether the previous file is the JD or a resume before uploading another file.")
        return
    if document.file_size and document.file_size > MAX_UPLOAD_MB * 1024 * 1024:
        await update.message.reply_text(f"{filename} is too large. The limit is {MAX_UPLOAD_MB} MB.")
        return
    try:
        telegram_file = await context.bot.get_file(document.file_id)
        content = BytesIO()
        await telegram_file.download_to_memory(content)
        text = extract_text(filename, content.getvalue())
    except DocumentExtractionError as exc:
        await update.message.reply_text(f"I could not read {filename}: {exc}")
        return
    except Exception:
        await update.message.reply_text(f"I could not download {filename}. Please try again.")
        return

    fingerprint = _fingerprint(text)
    fingerprints = context.user_data.setdefault("fingerprints", set())
    if fingerprint in fingerprints or (pending and fingerprint == pending[2]):
        await update.message.reply_text(f"I already received {filename}. Please send a different file.")
        return

    kind = classify_document_type(text)
    if not context.user_data.get("jd") and not context.user_data.get("resumes"):
        context.user_data["pending_document"] = (filename, text, fingerprint)
        detected = "job description" if kind == "jd" else "resume" if kind == "resume" else "document"
        await update.message.reply_text(
            f"This looks like a {detected}. Please confirm what it is:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Use as JD", callback_data="mark_jd")],
                [InlineKeyboardButton("Use as resume", callback_data="mark_resume")],
            ]),
        )
        return
    if kind == "unknown":
        context.user_data["pending_document"] = (filename, text, fingerprint)
        await update.message.reply_text(
            f"I cannot confidently identify {filename}. Is it the job description or a resume?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("This is the JD", callback_data="mark_jd")],
                [InlineKeyboardButton("This is a resume", callback_data="mark_resume")],
            ]),
        )
        return

    if kind == "jd":
        if context.user_data.get("jd"):
            await update.message.reply_text("I already have a JD. Please upload resumes only, or use /clear for another JD.")
            return
        context.user_data["jd"] = (filename, text)
        fingerprints.add(fingerprint)
        await _prompt_next(update, context, f"Added {filename} as the JD.")
        return

    if not context.user_data.get("jd"):
        context.user_data.setdefault("resumes", []).append((filename, text))
        fingerprints.add(fingerprint)
        await update.message.reply_text(f"Added {filename} as a resume. Now upload the JD.")
        return

    context.user_data.setdefault("resumes", []).append((filename, text))
    fingerprints.add(fingerprint)
    await _prompt_next(update, context, f"Added {filename} as a resume.")


async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action = query.data
    if action in {"mark_jd", "mark_resume"}:
        pending = context.user_data.pop("pending_document", None)
        if not pending:
            await query.edit_message_text("That upload has expired. Please send the file again.")
            return
        filename, text, fingerprint = pending
        fingerprints = context.user_data.setdefault("fingerprints", set())
        if fingerprint in fingerprints:
            await query.edit_message_text("I already received that document. Please send a different file.")
            return
        if action == "mark_jd":
            if context.user_data.get("jd"):
                await query.edit_message_text("I already have a JD. Use /clear before adding another one.")
                return
            context.user_data["jd"] = (filename, text)
            message = f"Added {filename} as the JD."
        else:
            context.user_data.setdefault("resumes", []).append((filename, text))
            message = f"Added {filename} as a resume."
        fingerprints.add(fingerprint)
        await query.edit_message_text(message)
        await _prompt_next(update, context)
        return

    if action == "manage_files":
        await _show_file_manager(query, context)
        return

    if action == "remove_jd":
        jd = context.user_data.pop("jd", None)
        if jd:
            context.user_data.setdefault("fingerprints", set()).discard(_fingerprint(jd[1]))
        await query.edit_message_text("Removed the JD. Upload a new JD to continue.")
        return

    if action.startswith("remove_resume_"):
        try:
            index = int(action.rsplit("_", 1)[1])
            resumes = context.user_data.get("resumes", [])
            removed = resumes.pop(index)
            context.user_data.setdefault("fingerprints", set()).discard(_fingerprint(removed[1]))
            await query.edit_message_text(f"Removed {removed[0]}.")
            await _prompt_next(update, context)
        except (ValueError, IndexError):
            await query.edit_message_text("That file is no longer available. Please use /files to see the current uploads.")
        return

    if action == "analyze_now":
        await analyze(update, context)
    elif action == "add_resume":
        await query.edit_message_text("Okay. Upload another resume, or use /analyze when ready.")


async def _prompt_next(update: Update, context: ContextTypes.DEFAULT_TYPE, prefix: str = "") -> None:
    jd = context.user_data.get("jd")
    resumes = context.user_data.get("resumes", [])
    if not jd:
        text = f"{prefix} Now upload the JD." if prefix else "Please upload the JD."
        await update.effective_message.reply_text(text)
    elif not resumes:
        text = f"{prefix} Now upload at least one resume." if prefix else "Now upload at least one resume."
        await update.effective_message.reply_text(text)
    else:
        await update.effective_message.reply_text(
            f"{prefix} I have 1 JD and {len(resumes)} resume(s). What would you like to do?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Analyze now", callback_data="analyze_now")],
                [InlineKeyboardButton("Add another resume", callback_data="add_resume")],
                [InlineKeyboardButton("Remove a file", callback_data="manage_files")],
            ]),
        )


async def _show_file_manager(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = []
    if context.user_data.get("jd"):
        buttons.append([InlineKeyboardButton("Remove JD", callback_data="remove_jd")])
    for index, (filename, _) in enumerate(context.user_data.get("resumes", [])):
        buttons.append([InlineKeyboardButton(f"Remove resume: {filename}", callback_data=f"remove_resume_{index}")])
    if not buttons:
        await query.edit_message_text("There are no uploaded files. Send a JD or resume to begin.")
        return
    buttons.append([InlineKeyboardButton("Keep files", callback_data="add_resume")])
    await query.edit_message_text("Choose the file you want to remove:", reply_markup=InlineKeyboardMarkup(buttons))


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    jd = context.user_data.get("jd")
    resumes = context.user_data.get("resumes", [])
    if not jd:
        await update.effective_message.reply_text("Please upload one JD first.")
        return
    if not resumes:
        await update.effective_message.reply_text("Please upload at least one resume first.")
        return
    try:
        documents = [jd, *resumes]
        classified = classify_documents(documents)
        analyses = analyze_documents(classified.jd[1], classified.resumes)
        await _send_results(update, classified.jd[0], format_results(analyses))
        await update.effective_message.reply_text("Analysis complete. Use /clear for a new JD and new resumes.")
    except ClassificationError as exc:
        await update.effective_message.reply_text(str(exc))


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _reset(context)
    await update.message.reply_text("Cleared. Send one JD and one or more resumes to begin again.")


async def files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("jd") and not context.user_data.get("resumes"):
        await update.message.reply_text("No files uploaded yet.")
        return
    await update.message.reply_text("Choose a file to remove:", reply_markup=InlineKeyboardMarkup(_file_buttons(context)))


def _file_buttons(context: ContextTypes.DEFAULT_TYPE) -> list[list[InlineKeyboardButton]]:
    buttons = []
    if context.user_data.get("jd"):
        buttons.append([InlineKeyboardButton("Remove JD", callback_data="remove_jd")])
    for index, (filename, _) in enumerate(context.user_data.get("resumes", [])):
        buttons.append([InlineKeyboardButton(f"Remove resume: {filename}", callback_data=f"remove_resume_{index}")])
    return buttons


async def text_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Please upload the JD or resume as a PDF, DOCX, or TXT file. Use /analyze when ready or /clear to restart.")


async def unsupported_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Please send the document as a PDF, DOCX, or TXT file, not as a photo or video.")


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
            "WHY THESE GAPS: " + (" | ".join(item["gap_explanations"]) or "None identified"),
            "SCORE BREAKDOWN: " + (", ".join(f"{name}={value}" for name, value in item["score_breakdown"].items()) or "Unavailable"),
            "COURSES: " + (" | ".join(f"{course['title']} ({course['url']})" for course in item["course_links"]) or "None recommended"),
        ])
    message = "\n".join(lines)
    for start in range(0, len(message), 3800):
        await update.effective_message.reply_text(message[start : start + 3800])


def build_application() -> Application:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in .env before starting the Telegram bot.")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(CommandHandler("files", files))
    application.add_handler(CallbackQueryHandler(handle_choice))
    application.add_handler(MessageHandler(filters.Document.ALL, receive_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_help))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.AUDIO, unsupported_media))
    return application


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    build_application().run_polling()
