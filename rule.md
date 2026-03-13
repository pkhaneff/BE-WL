Báo cáo nguyên tắc xây dựng dự án Python FastAPI chuẩn production
1. Mục tiêu kiến trúc

Xây dựng codebase theo hướng:

dễ scale theo team

dễ test

dễ review

dễ thay đổi nghiệp vụ

dễ tách module hoặc service về sau

Dự án phải tách rõ:

API layer

application/service layer

domain/business rule layer

infrastructure layer

shared/core layer

FastAPI nên được dùng như framework ở rìa hệ thống, không để business logic phụ thuộc trực tiếp vào framework. FastAPI hỗ trợ tổ chức app nhiều file/module bằng APIRouter, phù hợp cho app lớn.

2. Nguyên tắc tổ chức codebase

Ưu tiên tổ chức theo feature/module nghiệp vụ, không tổ chức thuần theo technical layer.

Mỗi module nghiệp vụ tự chứa:

router

schema

service

repository

exception

selector/query nếu cần

Không gom toàn bộ hệ thống thành các thư mục kiểu:

routers/

services/

repositories/

models/
khi dự án đã vượt mức nhỏ.

Mục tiêu là:

code cùng nghiệp vụ nằm gần nhau

giảm coupling

giảm xung đột khi nhiều người cùng làm

dễ tách bounded context

3. Cấu trúc thư mục khuyến nghị cho dự án vừa và lớn

Cấu trúc chuẩn:

project/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── router.py
│   │   ├── deps.py
│   │   └── exception_handlers.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   ├── constants.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── migrations/
│   │   └── models/
│   ├── modules/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── roles/
│   │   ├── permissions/
│   │   ├── orders/
│   │   ├── payments/
│   │   └── notifications/
│   ├── infrastructure/
│   │   ├── cache/
│   │   ├── messaging/
│   │   ├── storage/
│   │   ├── mail/
│   │   └── external_clients/
│   └── shared/
│       ├── enums.py
│       ├── types.py
│       ├── pagination.py
│       └── utils.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── alembic/
├── scripts/
├── pyproject.toml
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env
├── .env.example
└── README.md

main.py: entrypoint ứng dụng

api/: wiring HTTP, dependency, exception mapping

core/: config, logging, security, constant, base exception

db/: session, base ORM, migration

modules/: từng feature/bounded context

infrastructure/: kết nối hệ ngoài

shared/: primitive dùng chung, không được biến thành “sọt rác”

4. Quy tắc đặt tên

Thư mục: snake_case

File: snake_case.py

Class: PascalCase

Function/method/variable: snake_case

Constant: UPPER_SNAKE_CASE

Boolean variable:

is_active

has_permission

can_publish

Tên phải phản ánh vai trò:

router.py: khai báo endpoint

schemas.py: request/response contract

service.py: use case nghiệp vụ

repository.py: truy cập persistence

selectors.py: read/query optimized

exceptions.py: exception theo module

Không đặt tên mơ hồ:

common.py

helper.py

manager.py

util.py
trừ khi thực sự có phạm vi cực kỳ rõ ràng

5. Quy tắc phân lớp trách nhiệm

router

chỉ nhận request

gọi dependency

gọi service

trả response

không viết business logic

schema

chỉ định nghĩa contract request/response

không query DB

không chứa logic nghiệp vụ

service

chứa use case

điều phối transaction

kiểm tra business rule

không phụ thuộc FastAPI

repository

chỉ truy cập dữ liệu

không chứa nghiệp vụ

không commit transaction

domain

chứa business rule cốt lõi, contract, domain exception

không phụ thuộc framework

infrastructure

triển khai adapter DB, cache, queue, email, file storage, external API

6. Nguyên tắc SOLID áp dụng bắt buộc

SRP:

mỗi file/class chỉ có một lý do để thay đổi

OCP:

mở rộng bằng interface/protocol, không sửa lõi nghiệp vụ liên tục

LSP:

các implementation thay thế nhau được mà không phá hành vi

ISP:

interface nhỏ, đúng ngữ cảnh, không tạo interface khổng lồ

DIP:

service phụ thuộc abstraction, không phụ thuộc adapter cụ thể

Áp dụng thực tế:

service phụ thuộc UserRepositoryProtocol, không phụ thuộc SQLAlchemyUserRepository

mail service phụ thuộc EmailSender, không phụ thuộc thẳng SMTP/client cụ thể

7. Quy tắc clean code bắt buộc

Route phải mỏng

Service phải rõ một use case

Hàm ngắn, tên rõ nghĩa

Không comment để chữa code xấu

Không truyền Request, Response, Depends xuống service

Không truyền session/database connection đi lung tung giữa nhiều tầng mà không có boundary rõ ràng

Không để ORM model trôi tự do qua toàn bộ hệ thống

Không dùng magic string cho role, status, type

Không catch Exception chung chung rồi nuốt lỗi

Không viết “god class”, “god service”, “god repository”

8. Quy tắc ENV và config

Toàn bộ config phải đi qua một cổng vào duy nhất

Không gọi os.getenv() rải rác trong code nghiệp vụ

Dùng pydantic-settings cho settings/config

Dùng .env cho local/dev

Dùng environment variables hoặc secret manager cho staging/prod

Có .env.example nhưng không commit .env

Tách rõ:

app config

db config

cache config

jwt/security config

third-party config

Khuyến nghị prefix ENV theo hệ thống

APP_

DB_

REDIS_

JWT_

S3_

Pydantic Settings hỗ trợ load config từ environment variables và secrets files; FastAPI cũng khuyến nghị dùng settings theo cách này và dùng cache cho settings object để tránh đọc lại .env mỗi request. Twelve-Factor cũng khuyến nghị lưu config trong environment thay vì hard-code hoặc nhúng trong code.

9. Chuẩn tên ENV

Quy ước:

APP_NAME

APP_ENV

APP_DEBUG

APP_PORT

DB_HOST

DB_PORT

DB_USER

DB_PASSWORD

DB_NAME

REDIS_HOST

REDIS_PORT

JWT_SECRET_KEY

JWT_ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES

Rule:

dùng UPPER_SNAKE_CASE

tên rõ nghĩa

không viết tắt khó hiểu

secret không được có giá trị mặc định trong production

validate fail ngay khi app startup nếu thiếu config bắt buộc

10. Kết nối DB chuẩn production

Dùng SQLAlchemy 2.x

Engine tạo một lần theo vòng đời process

Session là đối tượng ngắn hạn

Tạo session bằng sessionmaker

Mỗi request hoặc mỗi use case dùng một session rõ ràng

Đóng session đúng cách

Rollback khi lỗi

Không dùng global session chia sẻ giữa nhiều request

Bật pool_pre_ping để giảm lỗi connection stale

Tắt autocommit

Tắt autoflush nếu team không kiểm soát tốt flush timing

Có migration bằng Alembic, không sửa DB schema thủ công

SQLAlchemy tài liệu chính thức mô tả sessionmaker là factory tạo Session; Session được dùng để quản lý transaction begin/commit/rollback; còn transaction control ở ORM public API đi qua Session.

11. Quy tắc transaction

repository không được commit()

repository không được quyết định transaction boundary

service hoặc unit_of_work là nơi quyết định:

begin

commit

rollback

Một use case nghiệp vụ quan trọng tương ứng một transaction boundary rõ ràng

Nếu nghiệp vụ nhiều repository:

dùng unit_of_work

Nếu CRUD đơn giản:

service commit là đủ

Không commit rải rác ở nhiều nơi trong cùng flow

12. Quy tắc Repository

Repository chỉ làm:

lấy dữ liệu

lưu dữ liệu

query/filter/paginate

map model persistence

Repository không làm:

policy nghiệp vụ

HTTP exception

auth logic

formatting response

Tách read/write nếu dự án lớn:

command repository

query repository / selector

Query phức tạp cho màn hình list/report:

để ở selectors.py hoặc query service

không ép repository CRUD gánh mọi loại query

13. Quy tắc Service/Application layer

Service đại diện cho use case

Mỗi method service phải mô tả hành động nghiệp vụ rõ ràng

Service không được phụ thuộc:

FastAPI request object

response object

framework-specific decorator/dependency

Service nhận vào:

primitive

DTO nội bộ

repository interface

unit of work

context user nội bộ nếu cần

Service chịu trách nhiệm:

validate business rule

gọi repository

điều phối transaction

phát domain event nếu có

gọi external provider qua abstraction

14. Quy tắc API layer

Dùng APIRouter theo module

Gom router bằng api/router.py

Prefix version rõ ràng:

/api/v1

Không viết query DB trực tiếp trong endpoint

Không format nghiệp vụ trực tiếp trong endpoint

Endpoint chỉ nên:

parse input

gọi service

return schema

FastAPI hỗ trợ APIRouter để nhóm path operations và include vào app hoặc router khác, phù hợp cho cấu trúc nhiều file/module.

15. Quy tắc schema/request/response

Tách riêng:

request schema

response schema

internal DTO nếu cần

Không trả ORM model trực tiếp ra API

Không dùng chung một schema cho cả create, update, response nếu ngữ nghĩa khác nhau

Response phải ổn định, không phụ thuộc cấu trúc DB

Có schema riêng cho:

create

update

detail

list item

filter/pagination

16. Quy tắc model domain và model persistence

Tách rõ:

domain entity

ORM model

API schema

Không để SQLAlchemy model đóng vai:

domain entity

response object

validation model
cùng lúc

Với dự án vừa và lớn, ba lớp model này phải tách tối thiểu về mặt trách nhiệm, kể cả khi có thể chưa tách thành ba loại object hoàn toàn độc lập từ ngày đầu

17. Quy tắc exception

Tách exception theo tầng:

DomainError

ApplicationError

InfrastructureError

Business rule violation:

ném custom exception

API layer:

map custom exception sang HTTP status code

Không ném HTTPException từ domain/service

Không trả message lỗi nội bộ DB/stack trace cho client

Có global exception handler

Có log đầy đủ khi exception đi qua boundary

18. Quy tắc logging

Bắt buộc structured logging

Log tối thiểu:

timestamp

level

request_id

trace_id nếu có

module

action/use_case

status_code

latency

user_id nếu có

Không log:

password

token đầy đủ

secret

PII nhạy cảm nếu không cần

Tách log:

application log

access log

error log

audit/security log nếu có

19. Quy tắc bảo mật

Secret chỉ lấy từ ENV hoặc secret manager

JWT key, DB password, API key tuyệt đối không hard-code

Bắt buộc:

input validation

auth middleware/dependency rõ ràng

permission check ở service hoặc policy layer

rate limit nếu public API

CORS cấu hình theo môi trường

tắt debug ở production

Phân quyền:

không hard-code role check rải rác

gom thành policy/permission service

20. Quy tắc dependency injection

Chỉ inject ở API boundary hoặc app wiring

Không lạm dụng DI tới mức mọi thứ đều factory

Nên inject:

db session

current user

repository

service

settings

Không nên inject trực tiếp framework object vào domain logic

FastAPI có hệ dependency rõ ràng, phù hợp để wiring session, settings và services ở API boundary.

21. Quy tắc chia module cho dự án vừa và lớn

Chia theo bounded context/feature:

auth

users

identity_access

catalog

orders

payments

billing

notifications

reporting

Mỗi module tự quản:

router

schema

service

repository

exception

Shared code phải cực kỳ tiết chế

Chỉ đưa vào shared/ những thứ thật sự generic và ổn định

Không đẩy code vào shared/ chỉ vì chưa biết để đâu

22. Quy tắc query và read optimization

Phân biệt rõ:

write model

read model

Những màn hình list/report/search phức tạp:

tách sang selector/query service

Không ép service write phải gánh query dashboard/report

Cho phép projection riêng cho read side nếu giúp tối ưu hiệu năng và độ rõ ràng

23. Quy tắc test

Bắt buộc tách:

unit

integration

e2e

Unit test:

domain rule

service logic

validator

permission logic

Integration test:

repository

DB transaction

migration

API với test DB

E2E test:

auth flow

permission flow

nghiệp vụ quan trọng

Mỗi bug production phải có regression test

FastAPI có hướng dẫn test app bằng test client; với dự án production nên giữ tách lớp test như trên để kiểm soát tốt độ tin cậy.

24. Quy tắc migration và schema evolution

Bắt buộc dùng Alembic

Mỗi thay đổi schema phải đi qua migration

Không sửa DB thủ công rồi mới cập nhật code

Migration phải:

review được

rollback được nếu cần

có naming rõ

Không gộp nhiều thay đổi schema lớn vào một migration mơ hồ

25. Quy tắc cho production readiness

Bắt buộc có:

health check

readiness/liveness endpoint

structured logging

migration pipeline

config theo ENV

Docker build chuẩn

CI lint/test

error monitoring

metrics

Process phải stateless

Dữ liệu bền vững phải nằm ở backing services như DB/cache/object storage

Đây cũng là nguyên tắc cốt lõi của Twelve-Factor cho ứng dụng cloud-native.

26. Quy tắc mở rộng cho team nhiều người

Có module ownership rõ

Có coding convention thống nhất ngay từ đầu

Bắt buộc review checklist:

có business logic trong router không

có commit trong repository không

có dùng config trực tiếp từ os.getenv() không

có tách request/response schema không

có custom exception đúng tầng không

có test cho business rule không

Không merge code phá boundary kiến trúc chỉ vì “cho nhanh”

27. Những điều cấm trong codebase

Cấm query DB trực tiếp trong router

Cấm commit trong repository

Cấm hard-code secret

Cấm os.getenv() rải rác

Cấm return ORM model trực tiếp ra API

Cấm business logic trong dependency function

Cấm dùng utils.py như thùng rác

Cấm except Exception: pass

Cấm import vòng giữa module

Cấm tạo shared package quá sớm cho những thứ chưa ổn định

28. Bộ tiêu chuẩn ngắn gọn để áp dụng ngay

Kiến trúc dùng modular monolith

Tổ chức theo feature-first

FastAPI chỉ ở API boundary

Config dùng pydantic-settings

Config/secret đi qua ENV

Persistence dùng SQLAlchemy + Alembic

Engine sống dài, Session sống ngắn

Transaction boundary nằm ở service/unit_of_work

Repository chỉ làm persistence

Response luôn qua schema

Exception nghiệp vụ là custom exception

Logging có request id/trace id

Test tách unit/integration/e2e

Shared code cực kỳ tiết chế

29. Kết luận áp dụng cho dự án vừa và lớn

Chọn kiến trúc:

modular monolith

feature-first

clean layering

Chọn nguyên tắc vận hành:

ENV-first

stateless process

session-per-request hoặc session-per-use-case

transaction ở service

migration bắt buộc

Chọn tiêu chuẩn coding:

SOLID

clean code

strict naming convention

strict layer boundary

Đây là hướng phù hợp với cách FastAPI khuyến nghị tổ chức app lớn bằng nhiều file/router, cách Pydantic Settings xử lý config từ ENV/secrets, và cách SQLAlchemy khuyến nghị quản lý Session/transaction.