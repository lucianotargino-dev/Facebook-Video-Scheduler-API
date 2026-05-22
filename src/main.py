# Importações
print("Script para agendamento de videos no Facebook")
import traceback
import sys
import requests
import time
import pytz
import json
import random
import os
import subprocess
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm









try:
    # Declaração de variaveis
    diretorio_execucao = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_diretorio_log = os.path.join(diretorio_execucao, "log", datetime.now().strftime("%Y"), datetime.now().strftime("%B"))
    arquivo_log = os.path.join(caminho_diretorio_log, f"log_{datetime.now().strftime("%Y-%m-%d")}.txt")

    projetos_opusclip_db = os.path.join(diretorio_execucao, "data", "database.xlsx")

    if not os.path.exists(projetos_opusclip_db):
        print("Banco de dados não encontrado. Encerrando execução.")
        raise FileNotFoundError

    dados_projetos_db = pd.read_excel(projetos_opusclip_db, sheet_name="Dados Projetos")
    contador_status = 0










    # Obtendo configurações do banco de dados
    print("Obtendo configurações do banco de dados")
    configuracoes = pd.read_excel(projetos_opusclip_db, sheet_name="Configurações Facebook")
    dias_limite_agendamento = configuracoes[configuracoes["Configuração"] == "Dias limite para agendamento"]["Valor"].iloc[0]
    quantidade_maxima_agendamento_por_execução = configuracoes[configuracoes["Configuração"] == "Quantidade máxima de agendamentos por execução"]["Valor"].iloc[0]
    tempo_espera_entre_ciclos = configuracoes[configuracoes["Configuração"] == "Tempo de espera entre agendamentos em segundos"]["Valor"].iloc[0]
    horarios_agendamento = [{"hora": int(h), "minuto": int(m)} for h, m in (hora.split(":") for hora in (configuracoes[configuracoes["Configuração"] == "Horários para agendamento"]["Valor"].iloc[0]).split(","))]
    ACCESS_TOKEN = configuracoes[configuracoes["Configuração"] == "ACCESS_TOKEN"]["Valor"].iloc[0]
    PAGE_ID = str(configuracoes[configuracoes["Configuração"] == "PAGE_ID"]["Valor"].iloc[0])
    url_facebook = configuracoes[configuracoes["Configuração"] == "url_Facebook"]["Valor"].iloc[0]
    timezone = pytz.timezone(configuracoes[configuracoes["Configuração"] == "timezone"]["Valor"].iloc[0])
    tempo_seguranca = configuracoes[configuracoes["Configuração"] == "Tempo de segurança pós horário atual ou agendamento em minutos"]["Valor"].iloc[0]
    BOT_TOKEN = configuracoes[configuracoes["Configuração"] == "Bot Token Telegram"]["Valor"].iloc[0]
    CHAT_ID = str(configuracoes[configuracoes["Configuração"] == "Chat ID Telegram"]["Valor"].iloc[0])
    url_telegram = configuracoes[configuracoes["Configuração"] == "url_Telegram"]["Valor"].iloc[0]










    # Declaração de funções
    def sleep_com_contador(segundos):
        for restante in range(segundos, 0, -1):
            minutos = restante // 60
            segundos_rest = restante % 60
            sys.stdout.write(f"\r⏳ Próximo upload em {minutos:02d}:{segundos_rest:02d}")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r✅ Continuando execução...            \n")


    def animacao_status():
        global contador_status
        contador_status += 1
        if contador_status == 0:
            animaçãostatus = "|"
        elif contador_status == 1:
            animaçãostatus = "/"
        elif contador_status == 2:
            animaçãostatus = "—"
        elif contador_status == 3:
            animaçãostatus = "\\"
        elif contador_status == 4:
            animaçãostatus = "|"
            contador_status = 0
        return animaçãostatus


    def log(mensagem):
        os.makedirs(caminho_diretorio_log, exist_ok=True)
        with open(arquivo_log, "a", encoding="utf-8") as arquivo:
            arquivo.write(f"{datetime.now().strftime("%Y/%m/%d %H:%M:%S")}: {mensagem}\n")


    def print_log(mensagem):
        log(mensagem)
        print(mensagem)


    def print_telegram(mensagem):
        while True:
            try:
                requests.post(url_telegram + BOT_TOKEN + "/sendMessage",data={"chat_id": CHAT_ID, "text": mensagem})
                break
            except:
                print_log("Erro, mensagem para o telegram não enviada, tentando novamente...")
                time.sleep(10)

        print_log(mensagem)


    def agendamento_facebook(video, titulo, descricao, data_hora): #resumable upload

        TamanhoVideo = os.path.getsize(video)

        # -------------------------
        # 1?? START
        # -------------------------
        params_start = {
            "upload_phase": "start",
            "file_size": TamanhoVideo,
            "access_token": ACCESS_TOKEN
        }

        while True:
            try:
                response_start = requests.post(url_facebook + PAGE_ID + "/videos", data=params_start)

                if response_start.status_code == 200:
                    if {"video_id","start_offset","end_offset","upload_session_id"}.issubset(response_start.json()):
                        upload_session_id = response_start.json()["upload_session_id"]
                        start_offset = int(response_start.json()["start_offset"])
                        end_offset = int(response_start.json()["end_offset"])
                        video_id = response_start.json()["video_id"]
                        break
                    else:
                        print_telegram(f"Conteudo da resposta da solicitação de inicio de sessão para upload não contem um ou varios dos elementos a seguir: video_id, start_offset, end_offset e upload_session_id. Tentando novamente.\n\n{json.dumps(response_start.json(), indent=4, ensure_ascii=False)}")
                else:
                    print_telegram(f"Resposta da solicitação de agendamento de post não retornou 200. Tentando novamente.\n\n{response_start}\n\n{json.dumps(response_start.json(), indent=4, ensure_ascii=False)}")

            except:
                print_telegram("Algo de errado aconteceu com a requisição de inicio de sessão e upload. Tentando novamente.")

        print_log(f"Sessão e upload iniciado")


        # -------------------------
        # 2?? TRANSFER
        # -------------------------
        with open(video, "rb") as Arquivo:

            with tqdm(total=TamanhoVideo, unit="B", unit_scale=True, desc="Upload") as pbar:

                while start_offset < TamanhoVideo:

                    Arquivo.seek(start_offset)
                    chunk = Arquivo.read(end_offset - start_offset)

                    params_transfer = {
                        "upload_phase": "transfer",
                        "upload_session_id": upload_session_id,
                        "start_offset": start_offset,
                        "access_token": ACCESS_TOKEN
                    }

                    files = {
                        "video_file_chunk": chunk
                    }

                    while True:
                        try:
                            response_transfer = requests.post(url_facebook + PAGE_ID + "/videos", data=params_transfer, files=files)

                            if response_transfer.status_code == 200:
                                if {"start_offset","end_offset"}.issubset(response_transfer.json()):
                                    new_start_offset = int(response_transfer.json()["start_offset"])
                                    end_offset = int(response_transfer.json()["end_offset"])
                                    break
                                else:
                                    print_telegram(f"Conteudo da resposta durante upload não contem um ou varios dos elementos a seguir: start_offset, end_offset.\nTentando novamente.\n\n{json.dumps(response_transfer.json(), indent=4, ensure_ascii=False)}")
                            else:
                                print_telegram(f"Resposta durante upload não retornou 200.\nTentando novamente.\n\n{response_transfer}\n\n{json.dumps(response_transfer.json(), indent=4, ensure_ascii=False)}")
                        
                        except:
                            print_telegram("Algo de errado aconteceu com o upload de uma das chunks. Tentando novamente.")

                    pbar.update(new_start_offset - start_offset)
                    start_offset = new_start_offset

                    log(f"Upload em andamento: {(start_offset / TamanhoVideo) * 100:.2f}%")


        # -------------------------
        # 3?? FINISH
        # -------------------------
        params_finish = {
            "upload_phase": "finish",
            "upload_session_id": upload_session_id,
            "title": titulo,
            "description": descricao,
            "access_token": ACCESS_TOKEN,
            "published": False,
            "scheduled_publish_time": int(data_hora.timestamp())
        }
        
        while True:
            try:
                response_finish = requests.post(url_facebook + PAGE_ID + "/videos", data=params_finish)
                
                if response_finish.status_code == 200:
                    if "success" in response_finish.json():
                        if response_finish.json()["success"]:
                            print_log("Sessão e upload finalizado")
                            return video_id
                            # break
                        else:
                            print_telegram(f"Conteudo da resposta de finalização de upload e sessão retornou False. Tentando novamente.\n\n{json.dumps(response_finish.json(), indent=4, ensure_ascii=False)}")
                    else: 
                        print_telegram(f"Conteudo da resposta de finalização de upload e sessão não contem o elemento \'success\'. Tentando novamente.\n\n{json.dumps(response_finish.json(), indent=4, ensure_ascii=False)}")
                else:
                    print_telegram(f"Resposta de finalização de upload e sessão não retornou 200. Tentando novamente.\n\n{response_finish}\n\n{json.dumps(response_finish.json(), indent=4, ensure_ascii=False)}")

            except:
                print_telegram("Algo de errado aconteceu com a finalização de sessão e upload. Tentando novamente.")


    def status_facebook(video_id):
        params = {
            "fields": "post_id,status",
            "access_token": ACCESS_TOKEN
        }
        
        while True:
            try:
                response_status = requests.get(url_facebook + video_id, params=params)

                if response_status.status_code == 200:

                    if "status" in response_status.json():

                        if "video_status" in response_status.json()["status"]:
                            video_status = response_status.json()["status"]["video_status"]
                        else:
                            print_telegram(f"Conteudo do elemento \'status\' não contem o elemento \'video_status\' na resposta da solicitação de status de agendamento.\n\n{json.dumps(response_status.json(), indent=4, ensure_ascii=False)}")
                            raise Exception()
                        
                        if video_status == "ready":
                            if "publishing_phase" in response_status.json()["status"]:
                                if "publish_time" in response_status.json()["status"]["publishing_phase"]:
                                    publish_time = str(datetime.fromisoformat(response_status.json()["status"]["publishing_phase"]["publish_time"]).astimezone(timezone))                    
                                else:
                                    print_telegram(f"Conteudo do elemento \'publishing_phase\' não contem o elemento \'publish_time\' na resposta da solicitação de status de agendamento.\n\n{json.dumps(response_status.json(), indent=4, ensure_ascii=False)}")
                                    raise Exception()
                            else:
                                print_telegram(f"Conteudo do elemento \'status\' não contem o elemento \'publishing_phase\' na resposta da solicitação de status de agendamento.\n\n{json.dumps(response_status.json(), indent=4, ensure_ascii=False)}")
                                raise Exception()
                        else:
                            publish_time = ""
                            
                    else:
                        print_telegram(f"Conteudo da resposta da solicitação de status de agendamento não contem o elemento \'status\'.\n\n{json.dumps(response_status.json(), indent=4, ensure_ascii=False)}")
                        raise Exception()
                    
                    if "post_id" in response_status.json():
                        post_id = PAGE_ID + "_" + response_status.json()["post_id"]
                    else:
                        print_telegram(f"Conteudo da resposta da solicitação de status de agendamento não contem o elemento \'post_id\'.\n\n{json.dumps(response_status.json(), indent=4, ensure_ascii=False)}")
                        raise Exception()

                else:
                    print_telegram(f"Resposta da solicitação de status de agendamento não retornou 200.\n\n{response_status}\n\n{json.dumps(response_status.json(), indent=4, ensure_ascii=False)}")
                    raise Exception()
                
                return video_status, post_id, publish_time
                break
            
            except Exception:
                print_log("Tentando novamente.")

            except:
                print_log("Algo de errado aconteceu com a solicitação de status. Tentando novamente.")


    def formatar_tamanho(bytes):
        for unidade in ["B", "KB", "MB", "GB", "TB"]:
            if bytes < 1024:
                return f"{bytes:.2f} {unidade}"
            bytes /= 1024


    def obter_duracao_video(video):
        comando = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video
        ]

        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        segundos = float(resultado.stdout.strip())

        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos = int(segundos % 60)

        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"










    # Obtendo dados do ultimo agendamento
    print_log("Obtendo dados do ultimo agendamento")
    response_ultimoagendamento = requests.get(url_facebook + PAGE_ID + "/scheduled_posts",params={"fields": "created_time", "limit": 1, "access_token": ACCESS_TOKEN},)
    if response_ultimoagendamento.status_code == 200:
        if "data" in response_ultimoagendamento.json():
            if len(response_ultimoagendamento.json()["data"]) == 1:
                if "created_time" in response_ultimoagendamento.json()["data"][0]:
                    data_hora_inicial_agendamento = datetime.fromisoformat(response_ultimoagendamento.json()["data"][0]["created_time"]).astimezone(timezone) + timedelta(minutes=tempo_seguranca)
                else:
                    print_telegram(f"Conteudo do elemento 'data[0]' não contem o elemento 'created_time' na resposta da solicitação para obter dados do ultimo agendamento.\nEncerrando execução.\n\n{json.dumps(response_ultimoagendamento.json(), indent=4, ensure_ascii=False)}")
                    raise SystemExit
            else:
                data_hora_inicial_agendamento = datetime.now().astimezone(timezone) + timedelta(minutes=tempo_seguranca)
        else:
            print_telegram(f"Conteudo da resposta da solicitação para obter dados do ultimo agendamento não contem o elemento 'data'.\nEncerrando execução.\n\n{json.dumps(response_ultimoagendamento.json(), indent=4, ensure_ascii=False)}")
            raise SystemExit
    else:
        print_telegram(f"Resposta da solicitação para obter dados do ultimo agendamento não retornou 200.\nEncerrando execução.\n\n{response_ultimoagendamento}\n\n{json.dumps(response_ultimoagendamento.json(), indent=4, ensure_ascii=False)}")
        raise SystemExit










    #Agendador de postagem de videos no Facebook por API
    print_telegram("-------------------------------------------------")
    print_telegram("Iniciando execução de agendamentos de videos para o Facebook")
    data_agendamento = data_hora_inicial_agendamento.replace(hour=0, minute=0, second=0, microsecond=0)
    contador_agendamento = 0
    encerrar_agendamentos = False
    dias_limite = ((datetime.now() + timedelta(days=dias_limite_agendamento)).date() - data_hora_inicial_agendamento.date()).days
    quantidade_agendamentos_total_dias = dias_limite * len(horarios_agendamento) - sum((h["hora"], h["minuto"]) < (data_hora_inicial_agendamento.hour, data_hora_inicial_agendamento.minute) for h in horarios_agendamento)

    if quantidade_maxima_agendamento_por_execução > quantidade_agendamentos_total_dias:
        quantidade_agendamento_por_execucao = quantidade_agendamentos_total_dias
    else:
        quantidade_agendamento_por_execucao = quantidade_maxima_agendamento_por_execução

    for dia in range(dias_limite):
        if dia != 0:
            data_agendamento = data_agendamento + timedelta(days=1)
        
        for horario in horarios_agendamento:
            data_hora_agendamento = data_agendamento + timedelta(hours=horario["hora"], minutes=horario["minuto"])
            video_encontrado = False

            if data_hora_agendamento >= data_hora_inicial_agendamento:
                contador_agendamento += 1
                print_telegram("####################################")
                print_telegram(f"Agendamento {contador_agendamento} de {quantidade_agendamento_por_execucao}")

                for i, registro_projetos in enumerate(dados_projetos_db.itertuples()):
                    planilha_db = pd.read_excel(projetos_opusclip_db, sheet_name=str(registro_projetos.ID))
                    planilha_db["Facebook_ID"] = planilha_db["Facebook_ID"].astype("string")
                    planilha_db["Facebook_Agendamento"] = planilha_db["Facebook_Agendamento"].astype("string")
                    planilha_db["Metodo"] = planilha_db["Metodo"].astype("string")
                    for registro_videos in planilha_db.itertuples():
                        sys.stdout.write(f"\rBuscando no banco de dados registro de video não postado. ({registro_projetos.ID}:{registro_videos.ID}) ")
                        sys.stdout.flush()
                        time.sleep(0.01)
                        if pd.isna(registro_videos.Facebook_ID) and pd.isna(registro_videos.Facebook_Agendamento):
                            sys.stdout.write("\n")
                            print_log("Registro encontrado no banco de dados.") 
                            print_telegram(f"Iniciando agendamento de postagem")
                            print_telegram(f"Nome do projeto: {registro_projetos.Nome_Projeto}")
                            print_telegram(f"Titulo do video: {registro_videos.Facebook_Titulo}")
                            print_telegram(f"Dados do video - Tamanho: {formatar_tamanho(os.path.getsize(registro_videos.Local_Video))}, Comprimento: {obter_duracao_video(registro_videos.Local_Video)}")
                            print_telegram(f"Horario agendamento: {data_hora_agendamento.strftime('%d/%m/%Y %H:%M:%S')}")


                            #Agendamento-------------------------------------------------------------------------------------------------------
                            video_id = agendamento_facebook(registro_videos.Local_Video, registro_videos.Facebook_Titulo, registro_videos.Facebook_Descrição, data_hora_agendamento)

                            print_telegram("Video agendado")
                            print_log(f"VIDEO_ID do agendamento: {video_id}")
                            print_telegram("Iniciando verificação de status")


                            #Verificação_de_status---------------------------------------------------------------------------------------------
                            status, post_id, data_hora_agendamento_facebook = status_facebook(video_id)

                            # contador_status = 0
                            while status != "ready":
                                sys.stdout.write(f"\rStatus: {status} {animacao_status()}")
                                sys.stdout.flush()
                                log(f"Status: {status}")
                                status, post_id, data_hora_agendamento_facebook = status_facebook(video_id)
                                
                            sys.stdout.write("\n")
                            print_telegram(f"Status: {status}")


                            #Preenchimento_de_banco_de_dados-----------------------------------------------------------------------------------
                            print_telegram("Preenchendo banco de dados")
                            print_telegram(f"Facebook_ID: {post_id}")
                            print_telegram(f"Facebook_Agendamento: {data_hora_agendamento_facebook}")
                            print_telegram("Metodo: Agendamento")
                            planilha_db.loc[planilha_db["ID"] == registro_videos.ID, "Facebook_ID"] = post_id
                            planilha_db.loc[planilha_db["ID"] == registro_videos.ID, "Facebook_Agendamento"] = data_hora_agendamento_facebook
                            planilha_db.loc[planilha_db["ID"] == registro_videos.ID, "Metodo"] = "Agendamento"
                            with pd.ExcelWriter(projetos_opusclip_db, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                                planilha_db.to_excel(writer, sheet_name=str(registro_projetos.ID), index=False)
                            print_telegram("Banco de dados preenchido")

                            #-------------------------------------------------------------------------------------------------------
                            print_telegram("####################################")

                            video_encontrado = True
                            break
                    if video_encontrado:
                        break
                    
                    if i == len(dados_projetos_db) -1:
                        sys.stdout.write("\n")
                        print_telegram("+++ No momento não existem mais videos para agendar +++")
                        print_telegram("####################################")
                        encerrar_agendamentos = True
                        # video_encontrado = True
                        break

                if encerrar_agendamentos:
                    break

                if contador_agendamento == quantidade_agendamento_por_execucao:
                    encerrar_agendamentos = True
                    break
                else:
                    print_telegram(f"Próximo agendamento em aproximadamente {tempo_espera_entre_ciclos} segundos")
                    sleep_com_contador(random.randint(tempo_espera_entre_ciclos -20, tempo_espera_entre_ciclos +20))
        
        if encerrar_agendamentos:
            break
    
    if contador_agendamento == 0 and quantidade_agendamento_por_execucao == 0:
        print_telegram("+++ No momento não existem mais horários de agendamentos disponiveis +++")

    print_telegram("Agendamentos finalizados")
    print_telegram("-------------------------------------------------")

except SystemExit:
    raise

except FileNotFoundError:
    raise

except:
    print_telegram(f"Ocorreu um erro.\nEncerrando execução.\n\n{traceback.format_exc()}")
