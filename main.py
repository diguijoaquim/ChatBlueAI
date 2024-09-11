from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import google.generativeai as genai
from starlette.middleware.cors import CORSMiddleware
from PIL import Image
import io
from fpdf import FPDF
import os
import imagehash
from typing import Optional
from datetime import datetime

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
        messages=modelo
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


# Função para calcular o hash perceptual de uma imagem
def calculate_image_hash(image: Image.Image):
    return imagehash.phash(image)


# Função para comparar dois hashes e verificar a diferença
def compare_hashes(hash1, hash2, limiar=10):
    diferenca = hash1 - hash2
    return diferenca, diferenca < limiar


async def getByGemini(file, text):
    print("passou no gemini")
    # Carregar a imagem original da pasta
    img_original = Image.open('./gina/gina.jpg')

    # Ler o conteúdo da imagem enviada pelo usuário
    contents_user = await file.read()
    img_user = Image.open(io.BytesIO(contents_user))

    # Calcular os hashes das duas imagens
    hash_original = calculate_image_hash(img_original)
    hash_user = calculate_image_hash(img_user)

    # Comparar os hashes
    diferenca, similar = compare_hashes(hash_original, hash_user)

    if similar:
        resposta = """
        A imagem que você enviou é da Gina AI. Ela apresenta um retrato de um robô
        com características femininas. O rosto do robô está pintado com as cores da bandeira de Moçambique,
        com o lado esquerdo exibindo as cores verde, amarelo e vermelho, e o lado direito apresentando preto
        e amarelo. O olho esquerdo é branco e o direito é verde vibrante. O robô usa fones de ouvido grandes
        e prateados, cobrindo parte do seu cabelo preto. A pele do robô é branca e brilhante, contrastando
        com as cores vibrantes da bandeira.
        O fundo da imagem é um borrão de um cenário urbano, com prédios altos e luzes brilhantes. O foco principal
        é o rosto do robô, que se destaca contra o fundo desfocado.
        """
        return resposta

    # Se as imagens forem diferentes, chamar o Gemini para processar a imagem
    response = model.generate_content([f"se a imagem tiver calculos deve retornar com latex se nao apenas descreva a imagem: {text}", img_user])
    print(response.text)
    return response.text


# Função para gerar o arquivo PDF com a resposta do chatbot
def generate_pdf(response_text: str, filename: str):
    pdf = FPDF()
    pdf.add_page()

    # Adiciona uma fonte Unicode (por exemplo, DejaVuSans)
    pdf.add_font("DejaVu", "", "./ttf/DejaVuSans.ttf", uni=True)  # Certifique-se de especificar o caminho correto para o arquivo .ttf
    pdf.set_font("DejaVu", size=12)

    # Use multi_cell para adicionar texto com caracteres Unicode
    pdf.multi_cell(0, 10, response_text)

    # Salva o arquivo PDF
    pdf.output(filename)


# Endpoint para download do arquivo PDF
@app.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join("documents", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filepath, media_type='application/pdf', filename=filename)


# Função auxiliar para salvar resposta em PDF
async def save_response_as_pdf(response, route_name):
    # Gerar nome do arquivo com base na data e hora atuais e na rota
    filename = f"{route_name}_response_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join("documents", filename)

    # Criar diretório se não existir
    os.makedirs("documents", exist_ok=True)

    # Gerar o arquivo PDF
    generate_pdf(response, filepath)
    return filename


# Rota da Gina
@app.post('/gina')
async def gina(pergunta: str, file: Optional[UploadFile] = File(None)):
    historico_gina.append({"role": "user", "content": pergunta})
    if file:
        if any(ext in file.filename for ext in ['jpg', 'png', 'jpeg']):
            descricao_imagem = await getByGemini(file, pergunta)
            historico_gina.append({"role": "assistant", "content": descricao_imagem})
            filename = await save_response_as_pdf(descricao_imagem, 'gina')
            return {'response': descricao_imagem, 'docs': f"/download/{filename}"}

        elif any(ext in file.filename for ext in ['wav', '3gp', 'WAV', 'OGG']):
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
        else:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
    
    historico_gina.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_gina)
    historico_gina.append({"role": "assistant", "content": resposta})
    filename = await save_response_as_pdf(resposta, 'gina')
    return {'response': resposta, 'docs': f"/download/{filename}"}

@app.post('/dina')
async def dina(pergunta: str, file: Optional[UploadFile] = File(None)):
    historico_dina.append({"role": "user", "content": pergunta})
    if file:
        if any(ext in file.filename for ext in ['jpg', 'png', 'jpeg']):
            descricao_imagem = await getByGemini(file, pergunta)
            historico_dina.append({"role": "assistant", "content": descricao_imagem})
            filename = await save_response_as_pdf(descricao_imagem, 'dina')
            return {'response': descricao_imagem, 'docs': f"/download/{filename}"}
        elif any(ext in file.filename for ext in ['wav', '3gp', 'WAV', 'OGG']):
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
        else:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
    
    historico_dina.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_dina)
    historico_dina.append({"role": "assistant", "content": resposta})
    filename = await save_response_as_pdf(resposta, 'dina')
    return {'response': resposta, 'docs': f"/download/{filename}"}



# Rota Junior 
@app.post('/junior')
async def junior(pergunta: str, file: Optional[UploadFile] = File(None)):
    historico_junior.append({"role": "assistant", "content": pergunta})
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            descricao_imagem = await getByGemini(file, pergunta)
            historico_junior.append({"role": "assistant", "content": descricao_imagem})
            return {'response': descricao_imagem, 'docs':''}
        elif 'wav' in file.filename or '3gp' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_junior.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_junior)
    historico_junior.append({"role": "assistant", "content": resposta})
    return {'response': resposta, 'docs': ""}


# Rota da Aliyah
@app.post('/aliyah')
async def Aliyah(pergunta: str, file: Optional[UploadFile] = File(None)):
    historico_aliyah.append({"role": "user", "content": pergunta})
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            descricao_imagem = await getByGemini(file, pergunta)
            historico_aliyah.append({"role": "assistant", "content": descricao_imagem})
            filename = await save_response_as_pdf(descricao_imagem, 'aliyah')
            return {'response': descricao_imagem, 'docs': f"/download/{filename}"}
        elif 'wav' in file.filename or '3gp' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_aliyah.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_aliyah)
    historico_aliyah.append({"role": "assistant", "content": resposta})
    filename = await save_response_as_pdf(resposta, 'aliyah')
    return {'response': resposta, 'docs': f"/download/{filename}"}


# Rota da Eva
@app.post('/eva')
async def Eva(pergunta: str, file: Optional[UploadFile] = File(None)):
    historico_eva.append({"role": "assistant", "content": pergunta})
    if file:
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            descricao_imagem = await getByGemini(file, pergunta)
            historico_eva.append({"role": "assistant", "content": descricao_imagem})
            filename = await save_response_as_pdf(descricao_imagem, 'eva')
            return {'response': descricao_imagem, 'docs': f"/download/{filename}"}
            
            resposta = getResposta(prompt, treino_junior)
        elif 'wav' in file.filename or '3gp' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    
    historico_eva.append({"role": "user", "content": pergunta})
    resposta = getResposta(pergunta, treino_eva)
    historico_eva.append({"role": "assistant", "content": resposta})
    filename = await save_response_as_pdf(resposta, 'eva')
    return {'response': resposta, 'docs': f"/download/{filename}"}

@app.get("/")
def home():
    return HTMLResponse("""
    <html>
        <head>
            <title>Chatbot</title>
        </head>
        <body>
            <h1>Welcome to the Chatbot</h1>
        </body>
    </html>
    """)
