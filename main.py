from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from starlette.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
from typing import Optional

genai.configure(api_key=os.getenv("GEMINI"))

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
from groq import Groq
from treino import *

app = FastAPI()
# Configure o middleware CORS para permitir todas as origens, métodos e cabeçalhos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

client = Groq(
    api_key=os.getenv("GINA"),
)

historico_gina = []
historico_dina = []
historico_junior = []
historico_gina.append({"role": "assistant", "content": treino_gina})
historico_dina.append({"role": "assistant", "content": treino_dina})
historico_junior.append({"role": "assistant", "content": treino_junior})

def getResposta(pergunta, modelo):
    response = client.chat.completions.create(
        messages=[
            {"role": "assistant", "content": modelo},
            {"role": "user", "content": pergunta},
        ],
        model="llama3-8b-8192",
    )
    return response.choices[0].message.content

async def transcribe_audio(file):
    contents = await file.read()
    audio_buffer = io.BytesIO(contents)
    audio_buffer.name = file.filename
    transcription = client.audio.transcriptions.create(
        file=(audio_buffer.name, audio_buffer.read()),
        model="whisper-large-v3",
        response_format="verbose_json",
        language="pt",
    )
    return transcription

async def getByGemini(file, text):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    response = model.generate_content([text, img])
    return response.text

#rota da Dina
@app.post('/gina')
async def gina(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            pergunta = await getByGemini(file, pergunta)
            
        elif 'wav' in file.filename or 'mp3' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename or 'ogg' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_gina.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_gina)
    historico_gina.append({"role": "assistant", "content": resposta})
    return resposta

#Rota da Dina
@app.post('/dina')
async def dina(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            pergunta = await getByGemini(file, pergunta)
            
        elif 'wav' in file.filename or 'mp3' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename or 'ogg' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_dina.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_dina)
    historico_dina.append({"role": "assistant", "content": resposta})
    return resposta

#Rota Junior 
@app.post('/junior')
async def junior(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            pergunta = await getByGemini(file, pergunta)
            
        elif 'wav' in file.filename or 'mp3' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename or 'ogg' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_junior.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_junior)
    historico_junior.append({"role": "assistant", "content": resposta})
    return resposta

#Rota da Aliyah
@app.post('/aliyah')
async def aliyah(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            pergunta = await getByGemini(file, pergunta)
            
        elif 'wav' in file.filename or 'mp3' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename or 'ogg' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_dina.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_dina)
    historico_dina.append({"role": "assistant", "content": resposta})
    return resposta


#Rota da Eva
@app.post('/eva')
async def eva(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            pergunta = await getByGemini(file, pergunta)
            
        elif 'wav' in file.filename or 'mp3' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename or 'ogg' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_dina.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_dina)
    historico_dina.append({"role": "assistant", "content": resposta})
    return resposta
