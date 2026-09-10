# Resume Matchroom

Resume Matchroom is a small AI-ready chatbot application that compares one job description with one or more resumes using ATS-style scoring.

## What it does

- Accepts PDF, DOCX, and TXT documents.
- Identifies the JD using document content, with filename fallback for ambiguous files.
- Parses the JD once and reuses it for every resume.
- Reports ATS score, matched skills, missing skills, JD alignment, prioritized gaps, and course recommendations.
- Explains why each important gap matters, shows the score contribution by factor, and links targeted learning resources.
- Ranks multiple resumes against the same JD.
- Skips a failed resume without stopping the rest of the batch.

## Architecture

`app/documents` handles validation, extraction, and classification. `app/analysis` contains the independent analysis engine. `app/chat` exposes the engine through a FastAPI upload route and formats JSON for the browser chat interface. The engine does not depend on the web layer.

## ATS score

The score is deterministic and visible in `app/analysis/scorer.py`:

```text
Required skill match       40%
Preferred skill match      15%
Experience match           15%
Education match            10%
Responsibility alignment   15%
Keyword/concept relevance   5%
```

Skills are normalized through aliases and counted once, so repeated keywords do not inflate a score.

## AI boundary

The current baseline deliberately works without an API key. Deterministic parsing, matching, scoring, ranking, validation, and error handling are local and inexpensive. An LLM adapter can be added later for semantic requirement extraction, alignment explanations, and recommendations without changing the engine contract.

## Run locally

On Windows, use the `py` launcher if `python` is not on PATH:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> and upload `sample_data/sample_jd.txt` plus one or both sample resumes.

## Telegram bot

Telegram is the external chat-platform adapter. In Telegram, open `@BotFather`, run `/newbot`, and copy the generated token into a local `.env` file:

```text
TELEGRAM_BOT_TOKEN=your-token-here
```

Never commit `.env` or share the token. Install dependencies and start the bot with:

```powershell
py -m pip install -r requirements.txt
py run_telegram.py
```

Open the bot in Telegram, send one JD and one or more resume files, then send `/analyze`. Use `/clear` to reset the current chat. The Telegram adapter uses the same document extraction, classification, scoring, ranking, and recommendation engine as the browser interface.

### Telegram edge cases

The guided Telegram flow handles these cases explicitly:

- No JD: asks the user to upload one.
- No resume: asks the user to upload at least one.
- Resume before JD: stores it and asks for the JD.
- Uncertain document type: shows buttons to mark it as JD or resume.
- Two JDs: rejects the second JD and keeps the current session.
- Unrelated document: rejects it instead of analyzing it as a resume.
- Duplicate document: detects the same extracted content even if the filename changes.
- Duplicate uncertain document: does not replace the pending clarification.
- Multiple resumes: offers `Analyze now` or `Add another resume`.
- Wrong file type, empty file, corrupted file, or oversized file: returns a readable error.
- Uploaded photo, video, or audio: asks for PDF, DOCX, or TXT instead.
- Accidental text message: explains the expected file workflow.
- Incorrect removal button after the list changed: returns a safe retry message.
- Removing files: `/files` or `Remove a file` removes the JD or any selected resume and updates the session.
- New analysis: `/clear` resets the chat-specific state.

## Test

```powershell
py -m pytest -q
```

The tests cover extraction, invalid files, classification, skill matching, recommendations, and multi-resume ranking. Manual testing should also include PDF/DOCX uploads, an empty file, a corrupted file, a missing JD, and an ambiguous pair of documents.

## Limitations and next steps

The baseline parser uses lightweight rules and a curated skill vocabulary. Scanned PDFs need OCR, and production use would need stronger semantic extraction, privacy controls, authentication, rate limits, and a real chat-platform adapter. Those additions are intentionally deferred so the core remains explainable for an interview.
