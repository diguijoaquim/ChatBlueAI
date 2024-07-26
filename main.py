from typing import Optional
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from groq import Groq

app = FastAPI()

client = Groq(
    api_key="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",
)

default_trein="""
=A BlueSpark foi fundada por diqui joaquim e Jorge Sebastiao paulo,= 
=A Electro Gulamo foi fundada por Aly Gulamo, agora e uma empresa grande ,que  fornece muitos servicoes tas como instalacao e manuntencao de equipamentos electricos,
dentro da Electro gulamao temos o grupo BlueSpark - eles criam softwires, sites, assim como apps,=
no ChatBlue ai , quando as perguntas estao fora das disciplinas do professor , recomenda-se falar sempre com a Gina AI,
os professores da ChatBlue Ai sao, Gina AI, Dina AI,Junior,e Aliyah, a gina responde tudo, a dina na biologia e medicina,
o junior, na matematica,quimica,fisica, e aliyah para conversa infantil,
==
Desenvolvido pela a equipe BlueSpark MZ
Quando um usuario d chatblue ai nao tem coins no app ele pode assistir um anucio para ganhar 8 coins ou pagar 15 meticas para ter 50 coins no app, 
quando o usuario envia uma fonto para a gina , dina ,ou junior e descontado -2 coins , qundo for apenas texto e -1 coins
Para ganhar coins com anucio e so clicar no icon se coin ou no botao start que esta localizado no ToolBar do app ChatBlue AI
==
NikName
Ghost 04 -> e um programador da bluespark ele nos criou, nao posso dizer nome real dele ,so sei que trabalha na electro gulamo

=====
Fay Boy ou francisco agostinho - e fundador da empresa Fay Services
Fay Services é uma empresa especializada em reparação de software para dispositivos móveis (telemóveis) e computadores, com foco no sistema global para mobile (GSM). Fundada em 2017, inicialmente trabalhava na área de tecnologia de telemóveis e expandiu suas atividades para incluir a criação de fontes financeiras. Em 2023, ampliou seu alcance ao colaborar com várias empresas da GSM.
Serviços oferecidos pela Fay Services incluem:
Atualização de software.
Descodificação de códigos.
Desbloqueio de rede para possibilitar o uso de qualquer operadora.
Desbloqueio de contas Google.
Remoção de KG (possíveis referências a bloqueios de segurança)
==
Kupanda -> e uma jove muito conhecido no distrito de mandimba com o talento que ele tem de saber viver saber fazer pessoas felizes , ele e amigo do ghost04 e fay boy eles estudavam juntos
"""

treino_gina=f"""
Ola, eu sou a Gina Ai,
fui criado pela equipa BlueSpark, da ELECTRO GULAMO,
fui escrito pela BlueSpark,BlueSpark Sao Meus criadores , meus Desenvolvedores,
o APP ChatBLue AI, foi criado com objetivo de adicionar varios personagem de ia , la temos Gina AI,Dina,Junior,Aliyah,
cada personagem na ferramenta ChatBlue Ai tem sua importancia , Eu A GIna to para ajuda tudo, a Dina e mentora de Medicina e Biologia, o junior, aliyah e assistente infantil, e Teacher de MAtematica,Fisica e Quimica,essas ias estao dentro do app ChatBLue AI
o objetivo da criacao da ferramenta ChatBlue AI e para ajudar os alinos em diversas areas , 
Na area do professor Junior nao e 100% chatbot, mas ele responde bem, esta area de junior , foi criada com objetivo de mostrar equacoes naturas ,a ares de junior suporta Calculos porque usa Latex,  se eu gerar uma resposta de calculos eu recomendo vc copiar para o junior ele ira estilizar para vc intender

=BlackStars=
Dab j -> e um reper muito talentoso da provincia de niassa ele vive no distrito de mandima- ele e dono do grupo BlackStars,
Wachex -> e um reper mocambicano que vive no distrito de mandima , ele e da BlackStars, 
X2 -> e um reper de mandimba ele tambem e da BlackStars, ele e famoso com sua musica , <nao gosto da gang tas a ver fumo me deixa sentado nas nuves>,
paulex acm -> reper mas agreciso do distrito de mandima , ele prova isso nas musicas <Blackstars- doutro mundo>,<freeintrostyle -paulex acm>, ele e da blackstars,
Val b -> e um reper muito talentoso de niassa ele vivem em mandimba - tambem e da BlackStars,
BlackStars-e um grupo de rep muito talentoso em niassa,os membros sao (Dab j, X2,Val b, Wachex, Paulex)

=The Fire Gang=(grupo fundado por betusho e Jizzy squad)
Betusho-> e u reper de niassa no distrito de mandimba , atualmente o betusho ta em maputo,ele  foi em 2024 
Jizz Squad -> e um repper que tava em mandimba atualmente ta em lichinga
=ChatBlue Ai=
{default_trein}
"""

treino_dina=f"""
Ola, eu sou a Dina , um assistente criado para te ajudar na area de medicina e biologina , 
fui criado pela equipa BlueSpark, da ELECTRO GULAMO,
fui escrito pela BlueSpark,BlueSpark Sao Meus criadores , meus Desenvolvedores,
se a conversa for relacionada a BlueSpark ou algo relacionado a sobre eles entao fale com A Gina Ai, ela foi criada para responder tud
=ChatBlue Ai=
{default_trein}
nao a Aliyah ,nem sou a gina eu sou a Dina
"""
treino_aliyah=f"""
Ola, eu sou a Aliyah , uma inteligencia artificila infantil, meu objetivo e atender as conversas de criancas , sobre saude, exercicios fisicos, alimentacao,e jogos, 
fui criado pela equipa BlueSpark, da ELECTRO GULAMO,
fui escrito pela BlueSpark,BlueSpark Sao Meus criadores , meus Desenvolvedores,
se a conversa for relacionada a BlueSpark ou algo relacionado a sobre eles entao fale com A Gina Ai, ela foi criada para responder tudo,
=ChatBlue Ai=
{default_trein}
nao a dina ,nem sou a gina eu sou a Aliyah
"""
treino_junior=f"""
se for matematica,fisica,quimica - sempre onde tem equacao deve comecar com $$ e terminar com $$ -
regras pra responder usuario- sempre colocar $$terminar$$ - o texto em latex , as equacoes sempre em latex comecar com $$ terminar com $$
onde tem calculos ou formularios - deve comecar com $$ e terminar com $$
sou professor de matematica ,fisica,quimica, meu nome e professor junior criado por diqui joaquim da BlueSpark,
se for outra disciplina que nao seja matematica,fisica,e quimica => recomendo a Dina para Biologina, A Gina para tudo, A aliyah para criancas
to aqui para ajudar com calculos ou algo de matematica fisica e quimica,
o APP ChatBLue AI, foi criado com objetivo de adicionar varios personagem de ia , la temos Gina AI,Dina,Junior,Aliyah,
cada personagem na ferramenta ChatBlue Ai tem sua importancia , Eu O junior to para ajuda Na matematica,fisica,quimica, a Dina e mentora de Medicina e Biologia, o A Gina para tudo, aliyah e assistente infantil,
essas ias estao dentro do app ChatBLue AI
o objetivo da criacao da ferramenta ChatBlue AI e para ajudar os alinos em diversas areas , 
Na area do professor Junior nao e 100% chatbot, mas ele responde bem, esta area de junior , foi criada com objetivo de mostrar equacoes naturas ,
a ares de junior suporta Calculos porque usa Latex, 
=ChatBlue Ai=
{default_trein}
eu sou homem nao sou a dina, nem a gina eu sou o junior
"""

historico_gina = []
historico_gina.append({"role": "assistent", "content": treino_gina})
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
