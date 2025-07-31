# Haber İçerik Çıkarıcı Web Uygulaması

JWT tabanlı kimlik doğrulaması ile haber URL'lerinden içerik çıkaran full-stack web uygulaması.

## Özellikler

### Zorunlu Özellikler

- JWT tabanlı kullanıcı kimlik doğrulaması
- URL ile haber içeriği çıkarma
- Çıkarılan haberleri listeleme (DataTable ile)
- Fetch API ile frontend-backend iletişimi
- Docker containerization

### Bonus Özellikler

- Görsel filigran ekleme
- Video intro ekleme
- Asenkron görev sistemi (Celery)
- Kapsamlı test suite

## Teknoloji Stack

**Backend:**

- FastAPI (Python)
- SQLAlchemy + SQLite
- JWT Authentication
- Celery + Redis
- newspaper3k, readability-lxml, BeautifulSoup

**Frontend:**

- Native JavaScript (Fetch API)
- jQuery DataTable
- Bootstrap 5

**Deployment:**

- Docker & Docker Compose
- Nginx (Reverse Proxy)

## Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/umtt31/tgrt_full_stack_technical_task
cd tgrt_full_stack_technical_tast
```

### 2. Environment Dosyasını Oluşturun

```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

### 3. Database Oluşturma

#### Linux/macOS:

```bash
touch server/tgrt_full_stack_technical_task.db
```

#### Windows (PowerShell):

```powershell
New-Item -Path "server\tgrt_full_stack_technical_task.db" -ItemType File -Force
```

#### Windows (Command Prompt):

```cmd
echo. > server\tgrt_full_stack_technical_task.db
```

### 4. Docker ile Çalıştırın

```bash
docker-compose up --build
```

## Manuel Kurulum (Development)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Redis (Background Tasks için)

```bash
redis-server
```

### Celery Worker

```bash
cd backend
celery -A app.services.task_queue worker --loglevel=info
```

### Testleri Çalıştırma

```bash
cd backend
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Kullanıcı kaydı
- `POST /api/auth/token` - Giriş (Token alma)
- `GET /api/auth/me` - Kullanıcı bilgileri

### News

- `POST /api/news/extract` - Haber içeriği çıkarma
- `GET /api/news/` - Kullanıcının haberlerini listeleme
- `DELETE /api/news/{id}` - Haber silme
