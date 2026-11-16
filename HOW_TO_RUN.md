# Cách chạy bài làm — Day 7

Bài làm: Nguyễn Thành Nam · 2A202603934 · L3B. Báo cáo: [report/individual/2A202603934_NguyenThanhNam.md](report/individual/2A202603934_NguyenThanhNam.md). Benchmark và tiêu chí chọn: [benchmark/README.md](benchmark/README.md).

| Thành phần | Lựa chọn |
|---|---|
| Corpus | *Think Python 2e* (CC BY-NC 3.0), 203 trang, 528 chunk B của Day 6 — [data/day7/chunks.json](data/day7/chunks.json) |
| Vector store | PostgreSQL 16 + pgvector 0.8.7 của Day 6 (Docker), cosine, exact search |
| Embedding | `BAAI/bge-base-en-v1.5`, 768 chiều, local CPU |
| Retrieval | M1 dense · M2 BM25 · M3 hybrid RRF · lân cận cùng mục (H1) |
| Agent | Gemini (`gemini-3.5-flash`, cấu hình chọn dùng `gemini-3.5-flash-lite`), 1 tool `search_book`, ≤ 3 lần tìm |
| Cấu hình chọn | `c_lite` — [results/selection.json](results/selection.json) |

## 1. Chuẩn bị (một lần)

Cần Python 3.11+, Docker Desktop, repo Day 6 ([Ishodayo/K5-L3B-DAY06-NguyenThanhNam-2A202603934-DataIngestion](https://github.com/Ishodayo/K5-L3B-DAY06-NguyenThanhNam-2A202603934-DataIngestion), commit `9cbecf5`) đã ingest vào pgvector, và một Gemini API key (trả phí; mỗi lượt 18 câu dev ≈ $0.15 với 3.5-flash, ≈ $0.02 với lite).

```bash
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```
Điền `GEMINI_API_KEY` trong `.env` (không commit file này). Bật DB Day 6 (mở Docker Desktop trước):
```bash
docker compose -f <đường-dẫn-repo-Day6>\starter\docker-compose.yml -p day6_student_starter up -d --wait
```
Nếu chưa có dữ liệu trong DB: trong repo Day 6 chạy `python -m src.run ingest` (xem README Day 6).

## 2. Kiểm tra kết nối và dữ liệu

```bash
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python -m src.run info --save
.\.venv\Scripts\python -m src.run export-chunks
.\.venv\Scripts\python -m src.run build-benchmark
.\.venv\Scripts\python -m src.run verify-benchmark
.\.venv\Scripts\python -m src.run search "How do I open a file for writing?" --method hybrid
```
Mong đợi: test OK; `rows: 528`, `vector_dimensions: 768`; `exported 528 chunks`; `RESULT: all checks passed`. (`build-benchmark`/`verify-benchmark` chỉ cần `chunks.json`, không cần DB.)

## 3. Retrieval (local, không tốn phí)

```bash
.\.venv\Scripts\python -m src.run retrieval-eval --split dev --configs dense,bm25,hybrid,dense_8k,dense_nb,dense_nb2,bm25_code,hybrid_code,hybrid_nb
```
Kết quả: `results/retrieval/{config}_dev.jsonl` (trace từng câu), `summary_dev.csv`.

## 4. Agent (gọi Gemini, tốn phí)

```bash
.\.venv\Scripts\python -m src.run ask "What does the // operator do in Python?"
.\.venv\Scripts\python -m src.run agent-eval --split dev --config baseline
```
Cấu hình có sẵn: `baseline`, `m2_bm25`, `m3_hybrid`, `c1_neighbors`, `c2_budget`, `c_lite` (`src/eval_agent.py`). `agent-eval` ghi đè trace của cấu hình đó: `results/agent/{config}_{split}_traces.json`, `_auto.json`.

## 5. Chấm nhãn, so sánh, chọn cấu hình

```bash
.\.venv\Scripts\python -m src.run review-sheet --split dev --configs baseline,c_lite
.\.venv\Scripts\python -m src.run import-reviews --split dev --configs baseline,m2_bm25,m3_hybrid,c1_neighbors,c2_budget,c_lite
.\.venv\Scripts\python -m src.run compare --split dev
.\.venv\Scripts\python -m src.run select
```
`review-sheet` tạo `{config}_{split}_review.md` (đọc) + `.csv` (điền `answer_grade`, `citation_support`, `abstention_correct`, `reason`; không ghi đè CSV đã điền); thêm `--context` để chấm context 0/1/2. Nhãn: AI hỗ trợ, gợi ý; học viên duyệt và xác nhận — đọc lại câu trả lời, đối chiếu với text chunk. `select` áp tiêu chí chốt trước trong `benchmark/README.md`.

## 6. Test (đã chạy một lần sau khi chọn — không chạy lại)

```bash
.\.venv\Scripts\python -m src.run retrieval-eval --split test --configs dense,dense_nb2 --confirm-test
.\.venv\Scripts\python -m src.run agent-eval --split test --config c_lite --confirm-test
.\.venv\Scripts\python -m src.run compare --split test --configs baseline,c_lite
```
Lần chạy test được ghi trong `results/*/test_runs.json` và `results/selection.json`.

## Cấu trúc thêm vào repo

```text
src/day6/            code store/embedding copy nguyên từ Day 6
src/config.py        đường dẫn, .env
src/day6_store.py    adapter pgvector Day 6 → schema Day 7 (M1 dense)
src/retrievers.py    BM25, hybrid RRF
src/context.py       đóng gói context, chunk lân cận
src/agent.py         agent Gemini + tool search_book
src/benchmark.py     build/verify benchmark, quy tắc hit
src/eval_retrieval.py, src/eval_agent.py, src/reviews.py, src/compare.py, src/run.py
benchmark/           câu hỏi Day 6, câu thiếu evidence, README
data/day7/           chunks, sources, questions, agent_cases
results/             trace, nhãn, metrics, so sánh, selection
tests/test_day6_adapter.py, test_benchmark.py, test_retrieval.py, test_agent_loop.py
```
