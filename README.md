# SmartTrainEval

SmartTrainEval（智训评）是一套面向软件项目实训的 AI 教学、过程辅导、多主体评价与成长分析系统。

## 国三演示闭环

- 教师创建课程和实训项目，AI 生成项目、里程碑与评价量规草案。
- 学生加入课程，通过课程知识库和启发式 AI 学伴完成项目并提交成果。
- AI 进行提交前预检，但不直接写入最终成绩。
- 教师与企业导师按评价指标分别评分；有企业导师时按教师 60% + 企业 40% 汇总。
- 管理员查看 AI 调用质量、知识库覆盖和流程状态，数字人播报真实项目数据。

## 本地启动

```powershell
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m scripts.init_db
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

前端地址为 `http://127.0.0.1:5173`，后端文档为 `http://127.0.0.1:8000/docs`。演示流程见 [DEMO_SCRIPT.md](DEMO_SCRIPT.md)。
