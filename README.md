# Wishlist BE — Backend API

Backend cho ứng dụng **Wishlist** - môi trường cho các cặp đôi chia sẻ mong ước.

## Tech Stack

- **Python 3.10** · **FastAPI** · **PostgreSQL** · **SQLAlchemy 2.x** · **Alembic** · **Redis**

## Cấu trúc dự án

```
app/
├── core/         # config, security, exceptions, logging
├── db/           # session, base ORM, models
├── api/          # deps, exception_handlers, router
├── modules/      # feature modules (auth, users, rooms, wishes, admin)
└── shared/       # enums, pagination — dùng chung, cực kỳ tiết chế
```

## Khởi động nhanh

```bash
# 1. Copy .env và điền thông tin
cp .env.example .env

# 2. Khởi động DB và Redis
docker-compose up -d db redis

# 3. Tạo môi trường conda và kích hoạt
conda env create -f environment.yml
conda activate wishlist-be

# 4. Chạy migration
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head

# 5. Chạy app
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

## API Endpoints

| Module | Prefix | Mô tả |
|---|---|---|
| Auth | `/api/v1/auth` | register, login, refresh, logout |
| Users | `/api/v1/users` | profile CRUD |
| Rooms | `/api/v1/rooms` | tạo phòng, join, leave |
| Wishes | `/api/v1/rooms/{room_id}/wishes` | CRUD wish + confirm |
| Admin | `/api/v1/admin` | quản trị toàn hệ thống |

## Business Rules

- Mỗi Room tối đa **2 thành viên active**
- Mỗi User chỉ **active trong 1 room** tại một thời điểm
- Chỉ **đối phương** mới được confirm wish (không tự confirm wish của mình)
- Wish có 4 loại: `gift`, `habit`, `bad_habit`, `question`
