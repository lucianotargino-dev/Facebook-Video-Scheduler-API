![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Status](https://img.shields.io/badge/status-active-success)
![Automation](https://img.shields.io/badge/automation-yes-orange)
![API](https://img.shields.io/badge/API-Facebook-blueviolet)

# 📅 Facebook Video Scheduler API

Automação em Python para agendamento de vídeos no Facebook utilizando a Graph API, com controle via planilha Excel.

---

## 🚀 Sobre o projeto

Este projeto automatiza o processo de upload e agendamento de vídeos em páginas do Facebook utilizando a Graph API.

Foi desenvolvido para resolver um problema real de automação de conteúdo, permitindo gerenciar múltiplos vídeos e projetos de forma eficiente, sem necessidade de uploads manuais.

---

## ⚙️ Funcionalidades

- 📤 Upload de vídeos via API do Facebook (resumable upload)
- 📅 Agendamento automático com base em horários definidos
- 📊 Controle de vídeos via planilha Excel
- 🔁 Verificação de status do processamento do vídeo
- 🤖 Notificações via Telegram
- ⏱️ Controle de intervalo entre postagens
- 📁 Suporte a múltiplos projetos
- 📝 Logs locais detalhados para monitoramento e diagnóstico
- 📈 Exibição e registro de progresso de upload
- 🎬 Obtenção automática da duração dos vídeos via ffprobe
- ♻️ Retry automático em falhas temporárias de rede/API

---

## 🗂️ Estrutura do projeto

```
Facebook-Video-Scheduler-API/
│
├── data/
│   └── database_fake.xlsx          # Banco de dados de exemplo
│
├── log/
│   └── 2026/
│       ├──April/
│       │  └── log_2026-04-30.txt   # Log
│       │
│       └──May/
│          └── log_2026-05-01.txt   # Log
│
├── src/
│   └── main.py                     # Script principal
├── requirements.txt
└── README.md
```

---

## 📊 Estrutura do banco de dados

O sistema utiliza um arquivo Excel com as seguintes abas:

### 1. Dados Projetos

Lista todos os projetos cadastrados. Esta aba contém:

- ID do projeto
- Nome do Projeto
- Link (Se houver. Esta informação também torna o banco de dados compativel com repositorios futuros)
- Quantidade de vídeos do projeto

---

### 2. Abas de projetos (uma para cada ID da aba 'Dados Projetos')

Cada aba representa um projeto da aba 'Dados Projetos' e lista todos os vídeos dos projetos com seus respectivos dados. Estas abas contêm:

- ID do vídeo
- Título
- Descrição
- Caminho do vídeo (No momento, o código aceita apenas caminhos absolutos para os vídeos)
- Status de postagem

Obs.: O nome das abas representa os IDs dos projetos na aba 'Dados Projetos', ou seja, se tiver um projeto na aba 'Dados Projetos' com ID 1, então terá uma aba de projeto nomeada com 1, tiver ID 2 então aba de projeto nomeada com 2 e assim sucessivamente. Caso tiver mais duvidas utilize o arquivo `database_fake.xlsx` para visualizar a estrutura do banco de dados.

---

### 3. Configurações Facebook

Contém parâmetros do sistema como:

- Horários de postagem
- Tokens de API
- Configurações de agendamento
- Telegram

---

## ⚠️ Importante

Este repositório NÃO inclui:

- Tokens de API
- IDs reais
- Banco de dados original

Utilize o arquivo `database_fake.xlsx` como base para criar o seu.

---

## 🛠️ Como usar

### 1. Clone o repositório

```
git clone https://github.com/lucianotargino-dev/Facebook-Video-Scheduler-API.git
cd Facebook-Video-Scheduler-API/src
```

---

### 2. Crie um ambiente (Opcional, recomendado)

Para evitar conflitos de dependências, recomenda-se utilizar um ambiente virtual.

```
python -m venv venv
```

Ativar:

**Windows**

```
venv\Scripts\activate
```

**Linux/Mac**

```
source venv/bin/activate
```

---

### 3. Instale as dependências

```
pip install -r requirements.txt
```

---

### 4. Instale o FFmpeg

O projeto utiliza o `ffprobe` para obter automaticamente a duração dos vídeos.

Instale o FFmpeg e certifique-se de que o comando abaixo funciona no terminal:

```bash
ffprobe -version
```

Download oficial: https://ffmpeg.org/download.html

---

### 5. Configure o banco de dados

- Copie o arquivo:

```
data/database_fake.xlsx
```

- Renomeie para:

```
database.xlsx
```

- Preencha com:
  - Seus projetos de videos
  - Seus vídeos (caminhos absolutos)
  - ACCESS_TOKEN
  - PAGE_ID
  - Configurações de horário

---

### 6. Execute o script

Certifique-se de estar dentro da pasta `src`:

```
python main.py
```

---

## 📝 Logs locais

O sistema gera logs locais automaticamente para facilitar:

- Monitoramento de uploads
- Diagnóstico de erros
- Rastreamento de execução
- Observabilidade do scheduler

Os logs são organizados automaticamente por ano e mês.

Exemplo:

```txt
log/2026/May/log_2026-05-01.txt
```

Para acompanhar logs em tempo real no Windows PowerShell:

```powershell
Get-Content .\log_2026-05-18.txt -Tail 20 -Wait -Encoding UTF8
```

---

## ⏰ Execução automatizada

O projeto foi desenvolvido para execução automática em segundo plano utilizando agendadores do sistema operacional.

Exemplos:

- Windows Task Scheduler (Windows)
- Cron/Crontab (Linux)
- launchd (macOS)

Atualmente o projeto é executado automaticamente via Windows Task Scheduler.

Como o sistema possui logs locais e notificações via Telegram, é possível monitorar execuções automáticas sem necessidade de interface gráfica.

---

## 🧠 Observações técnicas

- O upload utiliza o método **resumable upload** da API do Facebook
- O sistema evita repostagens verificando IDs no banco
- O agendamento respeita limite de dias e horários configurados
- Timezone configurável via planilha
- O sistema registra progresso de upload em logs locais
- O monitoramento pode ser realizado em tempo real via PowerShell
- O script possui retries automáticos para falhas temporárias

---

## 🚧 Melhorias futuras

- [ ] Separar variáveis sensíveis utilizando `.env`
- [ ] Implementar suporte a caminhos relativos para vídeos
- [ ] Implementar logs estruturados (JSON/logging)
- [ ] Adicionar timeout e política inteligente de retries
- [ ] Refatorar código para arquitetura modular
- [ ] Otimizar leitura do banco de dados para reduzir operações
- [ ] Migrar persistência de dados para banco de dados (ex: SQLite), substituindo uso de Excel

---

## 👨‍💻 Autor

Projeto desenvolvido para fins de automação e portfólio.

---

## 📄 Licença

Este projeto é de uso livre para estudos e adaptação.
Nenhuma garantia é fornecida.
