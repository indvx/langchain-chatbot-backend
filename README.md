# LangChain Chatbot Backend

An AI Chatbot Backend built with **FastAPI**, **LangChain**, **ChromaDB**, and **SQLAlchemy**. This service powers context-aware RAG (Retrieval-Augmented Generation) conversations using multi-provider LLMs (Google Gemini & OpenAI), features automated document ingestion, supports multi-channel integrations (WhatsApp Cloud API & Telegram Bot API), and provides relational management for employees and documents.

---

## Key Features

- **Multi-Provider LLM Integration**: Flexible switching between Google Gemini and OpenAI models for chat generation and vector embeddings via configuration.
- **Hybrid RAG & Text-to-SQL**: Blends document knowledge retrieval powered by **ChromaDB** with relational Text-to-SQL database querying.
- **Automated Document Ingestion Pipeline**: Background directory monitor using **APScheduler** that automatically detects, parses (PDF, DOCX, TXT, Web URLs), chunks, and embeds documents into ChromaDB.
- **Multi-Channel Messaging Integrations**:
  - **WhatsApp Cloud API**: Meta webhook verification and automated reply handling.
  - **Telegram Bot API**: Telegram webhook integration for instant chatbot replies.
- **Database & Migrations**: **SQLAlchemy ORM** backed by MySQL, with **Alembic** schema migration support.
- **Type-Safe Configuration**: Environment management powered by `pydantic-settings`.

---

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **AI & RAG Orchestration**: [LangChain](https://www.langchain.com/), `langchain-google-genai`, `langchain-openai`, `langchain-chroma`
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Database & Migration**: MySQL, [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/)
- **Background Tasks**: APScheduler
- **Configuration**: Pydantic v2 & `pydantic-settings`

---

## Repository Structure

```text
langchain-chatbot-backend/
├── main.py                        # FastAPI application setup, CORS, route registration & scheduler initialization
├── db.py                          # SQLAlchemy engine setup & session dependency
├── alembic.ini                    # Alembic migration configuration
├── alembic/                       # Database migration scripts & env setup
├── core/
│   └── config.py                  # Pydantic BaseSettings configuration
├── models/                        # Pydantic schemas for request validation & API models
│   ├── chat_bot.py
│   ├── document.py
│   ├── employee_addresses.py
│   └── employees.py
├── routers/                       # FastAPI router endpoints
│   ├── address.py                 # Employee address management endpoints
│   ├── chat_bot.py                # Conversational AI QA endpoints
│   ├── document.py                # Document upload and ingestion endpoints
│   ├── employees.py               # Employee profile and listing endpoints
│   ├── telegram.py                # Telegram webhook listener
│   └── whatsapp.py                # WhatsApp Cloud API webhook listener
├── services/                      # Core business logic & AI orchestration
│   ├── document.py
│   ├── document_ingestion_service.py
│   ├── document_reader.py
│   ├── employee.py
│   ├── employee_address.py
│   ├── langchain_service.py
│   ├── llm_service.py
│   ├── telegram_service.py
│   ├── utility.py
│   └── whatsapp_service.py
├── sql/                           # Database ORM models and CRUD handlers
│   ├── cruds/
│   ├── models/
│   └── schemas/
├── utils/
│   └── logger.py                  # Logger configuration
├── documents/                     # Local document staging directory for automated ingestion
├── Dockerfile                     # Multi-stage container build configuration
├── docker-compose.yml             # Docker service definitions
└── requirements.txt               # Project dependencies
```

---

## Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### Configuration Variables (`.env`)

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| **LLM_PROVIDER** | LLM model provider (`gemini` or `openai`) | `gemini` |
| **LLM_MODEL_NAME** | LLM model name | `gemini-1.5-flash` / `gpt-4o-mini` |
| **LLM_EMBEDDING_MODEL** | Embedding model name | `models/embedding-001` / `text-embedding-3-small` |
| **GOOGLE_API_KEY** | Google Gemini API key | `AIzaSy...` |
| **OPENAI_API_KEY** | OpenAI API key | `sk-...` |
| **META_VERIFY_TOKEN** | WhatsApp Meta Webhook verification token | `your_custom_verify_token` |
| **META_ACCESS_TOKEN** | Meta Graph API permanent or access token | `EAA...` |
| **META_PHONE_NUMBER_ID** | Meta WhatsApp Phone ID | `1006...` |
| **META_GRAPH_API_URL** | Meta Graph API endpoint URL | `https://graph.facebook.com/v22.0` |
| **TELEGRAM_BOT_TOKEN** | Telegram Bot API token from BotFather | `123456789:ABC...` |
| **TELEGRAM_API_URL** | Telegram API base URL | `https://api.telegram.org` |
| **DB_CONNECTION** | Database driver connection string | `mysql+pymysql` |
| **DB_HOST** | MySQL database host | `localhost` |
| **DB_PORT** | MySQL port | `3306` |
| **DB_USER** | MySQL username | `root` |
| **DB_PASSWORD** | MySQL password | `password` |
| **DB_NAME** (or **DB_DATABASE**) | MySQL database name | `ai_chatbot_db` |
| **DOCUMENT_DIR_NAME** | Staging folder for document ingestion | `./documents` |

---

## Installation & Setup

### 1. Clone Repository & Prepare Virtual Environment

```bash
cd langchain-chatbot-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Database Migration Setup

Ensure your MySQL database server is running and the target database exists. Then apply database migrations using Alembic:

```bash
# Run database migrations to create latest tables
alembic upgrade head
```

### 4. Run Development Server

Launch the server with Uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The interactive API documentation (Swagger UI) will be available at:
**`http://localhost:8000/docs`**

### 5. Run with Docker (Alternative)

Build and launch the application container using Docker Compose:

```bash
docker compose up --build
```

---

## Messaging Integrations Setup Guide

### Telegram Bot Setup (via BotFather)

1. **Create a Telegram Bot**:
   - Open Telegram and search for [@BotFather](https://t.me/BotFather).
   - Send `/newbot` command and follow the instructions to set a name and username for your bot.
   - BotFather will generate an **HTTP API Token** (e.g. `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

2. **Configure Environment**:
   In your `.env` file, add:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   TELEGRAM_API_URL=https://api.telegram.org
   ```

3. **Expose Local Host & Set Webhook**:
   - Expose your local backend server via a public URL (using `ngrok` or server deployment):
     ```bash
     ngrok http 8000
     ```
   - Register the webhook URL with Telegram API:
     ```bash
     curl -X POST "https://api.telegram.org/bot123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ/setWebhook" \
       -H "Content-Type: application/json" \
       -d '{"url": "https://<your-public-domain>.ngrok-free.app/telegram/webhook"}'
     ```

4. **Verify**:
   - Send any message to your bot on Telegram. The bot will receive updates via `/telegram/webhook` and reply automatically using the RAG model.

---

### WhatsApp Cloud API Setup (Meta)

1. **Set Up Meta Developer Application**:
   - Log in to [Meta for Developers](https://developers.facebook.com/).
   - Go to **My Apps** -> **Create App** -> Select **Other** / **Business**.
   - Under **Add products to your app**, select **WhatsApp** and click **Set up**.

2. **Obtain API Credentials**:
   - In the left menu, navigate to **WhatsApp** -> **API Setup**.
   - Copy the **Temporary Access Token** (or create a permanent System User Token) -> set as `META_ACCESS_TOKEN`.
   - Copy the **Phone Number ID** -> set as `META_PHONE_NUMBER_ID`.

3. **Configure Environment Variables**:
   Update your `.env` file with your Meta credentials:
   ```env
   META_VERIFY_TOKEN=my_secure_custom_verify_token
   META_ACCESS_TOKEN=your_meta_access_token_here
   META_PHONE_NUMBER_ID=your_phone_number_id_here
   META_GRAPH_API_URL=https://graph.facebook.com/v22.0
   ```

4. **Configure Meta Webhook**:
   - Go to **WhatsApp** -> **Configuration** in the Meta dashboard.
   - Click **Edit** under Webhook:
     - **Callback URL**: `https://<your-public-domain>.ngrok-free.app/whatsapp/webhook`
     - **Verify Token**: Must match `META_VERIFY_TOKEN` (e.g. `my_secure_custom_verify_token`).
   - Click **Verify and Save** (Meta triggers a verification request to `/whatsapp/webhook`).
   - Under **Webhook fields**, click **Manage** and subscribe to **`messages`**.

---

## API Endpoints Overview

### Chatbot & QA
- `POST /chat-bot/` - Send conversational query; executes hybrid Text-to-SQL and document vector search.

### Document Management
- `POST /doc/upload` - Upload document file (`PDF`, `DOCX`, `TXT`) for automated vector ingestion.
- `POST /doc/url/upload` - Ingest web page content from external URL.
- `GET /doc/list` - List paginated documents (supports `filter`, `order_by`, `order_direction`, `type`, `limit`, `page`).
- `DELETE /doc/{id}` - Delete document record, remove file from disk, and purge embeddings from ChromaDB.

### Employee Management
- `POST /employee` or `POST /employee/signup` - Register a new employee record.
- `GET /employee/list` - List paginated employees (supports `filter`, `order_by`, `order_direction`, `limit`, `page`).
- `GET /employee/{id}` - Get single employee details with associated addresses.
- `PUT /employee/{id}` - Update employee profile.
- `DELETE /employee/{id}` - Delete employee record.

### Employee Addresses
- `POST /employee/{employee_id}/address` - Add new address for an employee.
- `GET /employee/{employee_id}/address/list` - List all addresses attached to an employee.
- `DELETE /employee/address/{id}` - Remove an address by ID.

### Messaging Webhooks
- `GET /whatsapp/webhook` - Meta webhook verification handshake.
- `POST /whatsapp/webhook` - Receive incoming WhatsApp messages and respond via Meta Graph API.
- `POST /telegram/webhook` - Handle incoming Telegram updates and trigger bot replies.

---

## Quick Usage Example

### 1. Send Chat Query
```bash
curl -X 'POST' \
  'http://localhost:8000/chat-bot/' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What are our internal company policies on annual leave?"
  }'
```

### 2. Upload Document
```bash
curl -X 'POST' \
  'http://localhost:8000/doc/upload' \
  -F 'file=@handbook.pdf' \
  -F 'type=public'
```

---

## License

Distributed under the MIT License.
