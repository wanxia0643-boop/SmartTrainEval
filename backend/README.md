# 软件实训评价系统 · 后端

基于 **FastAPI + SQLAlchemy 2.0 + PyMySQL + LangChain + Pydantic** 的分层后端框架。

## 技术栈

| 分类 | 选型 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0（Mapped 声明式） |
| 数据库 | MySQL 8.0（PyMySQL 驱动） |
| 校验 | Pydantic v2 / pydantic-settings |
| 认证 | JWT（python-jose）+ BCrypt（passlib） |
| 大模型 | LangChain |
| 日志 | loguru |

## 目录结构

```
backend/
├── app/
│   ├── main.py              # 应用入口（工厂 + 中间件 + 路由挂载）
│   ├── core/                # 核心层：配置/数据库/安全/依赖/响应/异常
│   │   ├── config.py        # 配置（.env）
│   │   ├── database.py      # SQLAlchemy 引擎与会话、get_db 依赖
│   │   ├── security.py      # 密码哈希 + JWT 生成/校验
│   │   ├── deps.py          # 当前用户依赖 + require_roles 权限校验
│   │   ├── response.py      # 统一响应 {code,msg,data}
│   │   └── exceptions.py    # 自定义异常 + 全局异常处理
│   ├── models/              # 数据模型层（ORM）
│   ├── schemas/             # 数据校验层（Pydantic）
│   ├── services/            # 业务层（含 CRUDBase 基础封装）
│   ├── routers/             # 路由层
│   ├── ai/                  # AI 模块（LangChain 封装：文件解析/代码核查/智能评价）
│   └── utils/               # 工具层（日志、枚举）
├── alembic/                 # 数据库迁移（env.py 动态注入连接串与 Base 元数据）
│   └── versions/            # 迁移脚本目录
├── alembic.ini              # Alembic 配置
├── scripts/init_db.py       # 仅初始化角色/管理员（建表交给 Alembic）
├── requirements.txt
└── .env.example
```

## 分层职责

- **routers**：接收请求、参数绑定、调用 service、返回统一响应。
- **services**：业务逻辑；`services/base.py` 提供通用 `CRUDBase`（含逻辑删除、分页）。
- **models**：SQLAlchemy ORM；`TimestampMixin` 统一 `id/create_time/update_time/is_deleted`。
- **schemas**：Pydantic 入参校验与出参序列化。
- **utils**：日志、枚举等横切工具。
- **ai**：大模型能力封装入口（当前为预留空方法）。

## 快速开始

### 1. 环境准备
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置
```bash
cp .env.example .env   # Windows: copy .env.example .env
# 修改 .env 中的数据库连接、JWT_SECRET_KEY、LLM_API_KEY
```
先在 MySQL 中创建数据库（或执行项目根目录 `sql/smart_train_eval.sql`）：
```sql
CREATE DATABASE smart_train_eval DEFAULT CHARACTER SET utf8mb4;
```

### 3. 建表（Alembic 迁移）
首次使用先生成迁移脚本，再升级到最新版本：
```bash
# 根据 ORM 模型自动生成迁移脚本（需数据库已创建）
alembic revision --autogenerate -m "init schema"
# 应用迁移，创建全部数据表
alembic upgrade head
```
常用命令：
```bash
alembic current        # 查看当前版本
alembic history        # 查看迁移历史
alembic downgrade -1   # 回退一个版本
```
> 模型有变更后，重复 `revision --autogenerate` + `upgrade head` 即可。
> 也可直接执行项目根目录 `sql/smart_train_eval.sql`（含完整业务索引）作为权威建表脚本。

### 4. 初始化基础数据（角色 + 默认管理员）
建表完成后写入种子数据：
```bash
python -m scripts.init_db
# 默认管理员账号：admin / admin123
```
> `init_db.py` 仍保留 `create_all` 作为兜底，但生产建议以 Alembic 管理表结构。

### 5. 启动
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

## API 模块一览

所有接口挂载在 `API_PREFIX`（默认 `/api/v1`）下，均返回统一 `{code,msg,data}` 结构。

| 模块 | 前缀 | 说明 | 写操作权限 |
|------|------|------|-----------|
| 认证 | `/auth` | 登录、当前用户 | 公开 / 登录 |
| 用户 | `/users` | 用户 CRUD | 管理员 |
| 组织 | `/orgs` | 组织机构树 CRUD | 管理员 |
| 实训项目 | `/projects` | 项目 CRUD | 教师 / 管理员 |
| 实训成果 | `/achievements` | 成果提交与管理 | 学生提交 / 教师审改 |
| 评价指标 | `/indicators` | 指标体系 CRUD | 教师 / 管理员 |
| 评价结果 | `/eval-results` | 评分录入与修订 | 教师 / 企业导师 / 管理员 |
| 大模型日志 | `/llm-logs` | 调用日志（只读） | 管理员 |
| 报表记录 | `/reports` | 报表生成记录 | 教师 / 管理员 |

> 读接口（列表/详情）默认仅要求登录；写接口按上表角色控制。所有删除均为逻辑删除。

## 认证与权限

1. 调用 `POST /api/v1/auth/login` 获取 `access_token`。
2. 后续请求头携带：`Authorization: Bearer <token>`。
3. 接口权限通过 `require_roles(...)` 依赖控制，支持 4 种角色：
   `STUDENT` / `TEACHER` / `ENTERPRISE` / `ADMIN`。

示例：
```python
from app.core.deps import require_roles
from app.utils.enums import RoleCode

@router.post("", dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def create_xxx(): ...
```

## 统一响应格式

```json
{ "code": 0, "msg": "success", "data": {} }
```
- `code = 0` 表示成功；非 0 为业务/系统错误码。
- 校验失败、业务异常、未捕获异常均由全局处理器转为该结构。

## 成果得分汇总

`eval_result_service.recalc_final_score(db, achievement_id)` 按指标权重汇总并回填
`train_achievement.final_score`（百分制 0-100）：

1. 同一指标下多条评价（AI / 教师 / 企业导师 / 自评）按 `eval_type` 权重求加权平均（默认等权，可改 `DEFAULT_TYPE_WEIGHTS`）；
2. 换算为得分率 `score / max_score`；
3. 以指标 `weight` 对各指标得分率加权平均，×100 得最终得分（与权重是否合计 100 无关）。

录入 / 修订 / 删除评价时自动触发重算；也可手动调用
`POST /api/v1/eval-results/recalc/{achievement_id}`。

## AI 模块

`app/ai/evaluator.py` 中 `AIEvaluator` 预留三个入口（当前抛 `NotImplementedError`）：
- `parse_file()`：成果文件解析
- `check_code()`：代码核查
- `evaluate()`：智能评价

LLM 实例统一由 `app/ai/llm.py::get_llm()` 构建，便于切换模型厂商。
