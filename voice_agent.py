from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from google.cloud import texttospeech
import io
import os

app = FastAPI()
client = texttospeech.TextToSpeechClient()

@app.post("/speak")
async def synthesize(request: Request):
    body = await request.json()
    text_input = body.get("text", "")

    streaming_config = texttospeech.StreamingSynthesizeConfig(
        voice=texttospeech.VoiceSelectionParams(
            name="en-US-Chirp3-HD-Charon",
            language_code="en-US",
        )
    )

    config_request = texttospeech.StreamingSynthesizeRequest(
        streaming_config=streaming_config
    )

    def request_generator():
        yield config_request
        yield texttospeech.StreamingSynthesizeRequest(
            input=texttospeech.StreamingSynthesisInput(text=text_input)
        )

    audio_stream = io.BytesIO()
    for response in client.streaming_synthesize(request_generator()):
        audio_stream.write(response.audio_content)

    audio_stream.seek(0)
    return StreamingResponse(audio_stream, media_type="audio/mpeg")
