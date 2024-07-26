from typing import Optional
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from groq import Groq

app = FastAPI()

client = Groq(
    api_key="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",
)



def getResposta(pergunta):
    response = client.chat.completions.create(
    messages=[
        {
            "role": "assistant",
            "content": "foi criado por Ghost04, eu fui desenvolvido pelo dGhost04 ele e o meu criado"
        },
        {
            "role": "user",
            "content": pergunta
        },
        
    ],
    model="llama3-8b-8192",
)
    return response.choices[0].message.content

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    # Salvar o arquivo no disco temporariamente
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Fazer a transcrição usando Groq
    with open(file_location, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(file_location, f.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
            language="pt",
        )
    
    # Remover o arquivo temporário
    os.remove(file_location)
    resposta=getResposta(transcription.text)
    # Retornar a transcrição
    return {"resposta": resposta}

@app.get("/")
async def main():
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Record and Upload Audio</title>
    </head>
    <body>
        <h1>Record and Upload Audio</h1>
        <button id="startRecording">Start Recording</button>
        <button id="stopRecording" disabled>Stop Recording</button>
        <br>
        <audio id="audioPlayback" controls></audio>
        <br>
        <button id="uploadRecording" disabled>Upload Recording</button>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let audioBlob;

            document.getElementById("startRecording").onclick = () => {
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(stream => {
                        mediaRecorder = new MediaRecorder(stream);
                        mediaRecorder.start();
                        
                        mediaRecorder.ondataavailable = event => {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = () => {
                            audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const audioUrl = URL.createObjectURL(audioBlob);
                            document.getElementById("audioPlayback").src = audioUrl;
                            document.getElementById("uploadRecording").disabled = false;
                        };

                        document.getElementById("startRecording").disabled = true;
                        document.getElementById("stopRecording").disabled = false;
                    });
            };

            document.getElementById("stopRecording").onclick = () => {
                mediaRecorder.stop();
                document.getElementById("stopRecording").disabled = true;
                document.getElementById("startRecording").disabled = false;
            };

            document.getElementById("uploadRecording").onclick = () => {
                const formData = new FormData();
                formData.append("file", audioBlob, "recording.wav");

                fetch("/uploadfile/", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Success:", data);
                })
                .catch(error => {
                    console.error("Error:", error);
                });
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=content)
