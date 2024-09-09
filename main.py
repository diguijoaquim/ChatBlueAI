from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from PIL import Image
import io
from fpdf import FPDF
import os
import imagehash
from typing import Optional
from datetime import datetime
import asyncio

app = FastAPI()

# Configure o middleware CORS para permitir todas as origens, métodos e cabeçalhos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

def generate_pdf(response_text: str, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, response_text)
    pdf.output(filename)

async def delete_file_after_one_hour(filepath: str):
    # Espera 1 hora (3600 segundos)
    await asyncio.sleep(3600)
    
    # Verifica se o arquivo ainda existe e o exclui
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Arquivo {filepath} deletado após 1 hora.")
    else:
        print(f"O arquivo {filepath} não existe ou já foi deletado.")

async def save_response_as_pdf(response, route_name):
    # Gerar nome do arquivo com base na data e hora atuais e na rota
    filename = f"{route_name}_response_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join("documents", filename)

    # Criar diretório se não existir
    os.makedirs("documents", exist_ok=True)

    # Gerar o arquivo PDF
    generate_pdf(response, filepath)
    
    # Iniciar a tarefa de deletar o arquivo após 1 hora
    asyncio.create_task(delete_file_after_one_hour(filepath))
    
    return filename

async def validate_file(file: UploadFile):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "audio/wav", "audio/ogg", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado.")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    return contents

# Função para calcular o hash perceptual de uma imagem
def calculate_image_hash(image: Image.Image):
    return imagehash.phash(image)

# Função para comparar dois hashes e verificar a diferença
def compare_hashes(hash1, hash2, limiar=10):
    diferenca = hash1 - hash2
    return diferenca, diferenca < limiar

async def getByGemini(file, text):
    img_original = Image.open('./gina/gina.jpg')
    contents_user = await file.read()
    img_user = Image.open(io.BytesIO(contents_user))
    hash_original = calculate_image_hash(img_original)
    hash_user = calculate_image_hash(img_user)
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
    response = model.generate_content([f"descreve em portugues: {text}", img_user])
    return response.text

@app.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join("documents", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filepath, media_type='application/pdf', filename=filename)

@app.post('/gina')
async def gina(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
        contents = await validate_file(file)
        
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            descricao_imagem = await getByGemini(file, pergunta)
            prompt = (f"Essa imagem foi processada com a Gina '{descricao_imagem}'. "
                      f"O usuário fez a seguinte pergunta: '{pergunta}'. "
                      f"Não fale muito além da resposta; essa imagem foi processada com Gina AI.")
            
            resposta = getResposta(prompt, treino_gina)
        elif 'wav' in file.filename or '3gp' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    else:
        resposta = getResposta(pergunta, treino_gina)
    
    filename = await save_response_as_pdf(resposta, 'gina')
    return {'response': resposta, 'docs': f"/download/{filename}"}

# Repita a mesma estrutura para as rotas /dina, /junior, /aliyah, /eva

# Exemplo para a rota /dina
@app.post('/dina')
async def dina(pergunta: str, file: Optional[UploadFile] = File(None)):
    if file:
        contents = await validate_file(file)
        
        if 'jpg' in file.filename or 'png' in file.filename or 'jpeg' in file.filename:
            descricao_imagem = await getByGemini(file, pergunta)
            prompt = (f"Essa imagem foi processada com a Dina '{descricao_imagem}'. "
                      f"O usuário fez a seguinte pergunta: '{pergunta}'. "
                      f"Não fale muito além da resposta; essa imagem foi processada com Dina AI.")
            
            resposta = getResposta(prompt, treino_dina)
        elif 'wav' in file.filename or '3gp' in file.filename or 'WAV' in file.filename or 'OGG' in file.filename:
            transcription = await transcribe_audio(file)
            pergunta = transcription.text
    else:
        resposta = getResposta(pergunta, treino_dina)
    
    filename = await save_response_as_pdf(resposta, 'dina')
    return {'response': resposta, 'docs': f"/download/{filename}"}
