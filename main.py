from typing import Optional
from fastapi import FastAPI, File, UploadFile,Form
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from PIL import Image
import io
from typing import Optional

genai.configure(api_key="AIzaSyBtmW-jLX6FX8gcmwZrEGks19v5BNTqtt8")

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
from groq import Groq
from treino import *


app = FastAPI()

client = Groq(
    api_key="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",
)


historico_gina = []
historico_dina = []
historico_junior = []
historico_gina.append({"role": "assistent", "content": treino_gina})
historico_dina.append({"role": "assistent", "content": treino_dina})
historico_junior.append({"role": "assistent", "content": treino_junior})
def getResposta(pergunta,modelo):
    response = client.chat.completions.create(
    messages=[
        {
            "role": "assistant",
            "content": modelo
        },
        {
            "role": "user",
            "content": pergunta
        },
        
    ],
    model="llama3-8b-8192",
)
    return response.choices[0].message.content


@app.get('/chat/')
def home_img():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Upload de Imagem</title>
</head>
<body>
    <h1>Upload de Imagem</h1>
    <form action="/uploadimage/" enctype="multipart/form-data" method="post">
        <input type="file" name="file">
      <input type="text" name="text">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
""")

async def transcribe_audio(file):
    # Ler o conteúdo do arquivo
    contents = await file.read()

    # Salvar o conteúdo em um BytesIO buffer
    audio_buffer = io.BytesIO(contents)
    audio_buffer.name = file.filename  # Definir o nome do arquivo para manter a extensão

    # Fazer a transcrição usando Groq
    transcription = client.audio.transcriptions.create(
        file=(audio_buffer.name, audio_buffer.read()),
        model="whisper-large-v3",
        response_format="verbose_json",
        language="pt",
    )
    return transcription

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
    historico_gina.append({"role": "user", "content": transcription.text})
    resposta=getResposta(transcription.text,treino_gina)
    historico_gina.append({"role": "assistent", "content": resposta})
    # Retornar a transcrição
    return resposta

#pegar a resposta da imagem com gemmini
async def getByGemini(file,text):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    
    # Assumindo que o modelo espera uma imagem de certa forma, por favor, ajuste conforme necessário
    response = model.generate_content([text, img])
    
    return {"response": response.text}

    
@app.post('/gina')
async def gina(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
       

        if 'jpg' in file.filename or 'png' in  file.filename or 'jpeg' in file.filename:
            pergunta=getByGemini(file,pergunta)
        elif 'wav' in file.filename or 'mp3' in  file.filename or 'WAV' in  file.filename:
            pergunta=transcribe_audio(file)
        

    
    historico_gina.append({"role": "user", "content": pergunta})
    resposta=getResposta(pergunta,treino_gina) 
    historico_gina.append({"role": "assistent", "content": resposta})
    # Retornar a transcrição
    return resposta

@app.post('/dina')
async def dina(pergunta: str, file: Optional[UploadFile] = File(None)):
    historico_dina.append({"role": "user", "content": pergunta})
    resposta=getResposta(pergunta,treino_dina)
    historico_dina.append({"role": "assistent", "content": resposta})
    # Retornar a transcrição
    return resposta

@app.post('/junior')
async def junior(pergunta: str, file: Optional[UploadFile] = File(None)):
    historico_junior.append({"role": "user", "content": pergunta})
    resposta=getResposta(pergunta,treino_junior)
    historico_junior.append({"role": "assistent", "content": resposta})
    # Retornar a transcrição
    return resposta

    

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
    
@app.post("/uploadimage/")
async def create_upload_file(file: UploadFile = File(...), text: str = Form(...)):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    
    # Assumindo que o modelo espera uma imagem de certa forma, por favor, ajuste conforme necessário
    response = model.generate_content([text, img])
    
    return {"response": response.text}

