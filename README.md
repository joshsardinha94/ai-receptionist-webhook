# AI Receptionist Webhook — Alex

A production-deployed voice AI receptionist built on Vapi, Claude Haiku, and Flask.

## What it does
- Answers inbound phone calls automatically via Vapi
- Collects caller name, callback number, reason for call, and best callback time
- Sends a formatted email summary with full transcript after every call
- Scores each call on a 1-10 performance scale using structured outputs

## Stack
- **Voice AI:** Vapi (STT via Deepgram, TTS, LLM orchestration)
- **LLM:** Claude Haiku 4.5 (Anthropic)
- **Backend:** Python / Flask
- **Deployment:** Render
- **Email:** SendGrid

## Live Demo
Call Alex right now: **1 (845) 603-8413**

## Architecture
Vapi handles the full call → structured outputs extract caller data → 
end-of-call webhook fires to Flask server → formatted summary email delivered instantly.
