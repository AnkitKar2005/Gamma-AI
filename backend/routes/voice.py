"""Gamma AI — Voice REST API Route."""

from fastapi import APIRouter, Depends, UploadFile, File

from auth.jwt import get_current_session

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


@router.post("/")
async def voice_endpoint(
    audio: UploadFile = File(...),
    session: dict = Depends(get_current_session),
):
    """REST fallback for voice — upload audio file, get text response.

    For real-time voice, use the WebSocket voice_data message type.
    """
    session_id = session.get("sub", "anonymous")

    try:
        audio_bytes = await audio.read()

        from services.stt import transcribe
        transcript = await transcribe(audio_bytes, audio_format=audio.filename.split(".")[-1] if audio.filename else "webm")

        from orchestrator.graph import run_orchestrator
        result = await run_orchestrator(session_id, transcript)

        return {
            "transcript": transcript,
            "response": result.get("final_response", ""),
            "intent": result.get("intent", "general"),
        }
    except Exception as e:
        return {"error": str(e), "transcript": "", "response": ""}
