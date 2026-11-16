# Benchmark Day 7 — Think Python 2e

Chốt ngày **2026-11-16**, **trước khi** chạy bất kỳ phương pháp retrieval hay agent nào của Day 7. Không sửa câu/nhãn test sau khi xem kết quả; nếu buộc phải sửa sẽ ghi ở mục *Nhật ký* và không coi test là holdout độc lập nữa.

## File

| File | Nội dung | Ai được đọc |
|---|---|---|
| `benchmark/day6_questions.jsonl` | 22 câu có đáp án, **copy nguyên** từ repo Day 6 (commit `9cbecf5`) | chỉ script build |
| `benchmark/unanswerable.json` | 4 câu thiếu evidence viết cho Day 7, kèm lý do và mẫu regex kiểm tra | chỉ script build/verify |
| `data/day7/questions.json` | 22 câu có đáp án theo schema Day 7: `id, split, type, question, expected_answer, gold[{source_id, page, evidence}], filter?` | **chỉ phần chấm** (metrics) |
| `data/day7/agent_cases.json` | 26 câu: `id, split, type, question, answerable, expected_behavior, filter?, absence_reason?` — **không có gold/đáp án** | agent runner + `starter/agent_metrics.py` |
| `data/day7/sources.json` | thông tin tài liệu: nguồn, giấy phép, phiên bản, sha256 | metadata chunk |
| `results/benchmark_verify.json` | kết quả kiểm chứng tự động | báo cáo |

Tạo lại và kiểm tra (từ thư mục gốc repo):
```bash
.\.venv\Scripts\python -m src.run export-chunks
.\.venv\Scripts\python -m src.run build-benchmark
.\.venv\Scripts\python -m src.run verify-benchmark
```

## Thống kê

| Loại | dev | test | tổng |
|---|---:|---:|---:|
| Có đáp án | 16 | 6 | 22 |
| — `direct` / `paraphrase` / `condition_exception` / `metadata_filter` | 4 / 4 / 5 / 3 | 1 / 2 / 1 / 2 | 5 / 6 / 6 / 5 |
| — có evidence thay thế (`gold` > 1 phần tử) | 3 | 2 | 5 |
| Thiếu evidence | 2 | 2 | 4 |
| **Tổng** | **18** | **8** | **26** |

Yêu cầu đề (BENCHMARK.md): dev ≥ 15 + 2, test ≥ 5 + 2 → **đạt**.

## Chia dev/test

Giữ nguyên cách chia của Day 6 — **theo chương**, không chương nào vừa ở dev vừa ở test:
- Dev: ch02, ch05, ch06, ch08, ch10, ch11, ch13, ch14, ch15, appendix_A
- Test: ch12, ch16, ch17, ch18, ch19, appendix_B

Câu thiếu evidence cũng theo chương: dev gần ch14/ch03, test gần ch18/ch19.

## Câu có đáp án

- `gold` = evidence chính + các evidence thay thế hợp lệ (vd mục Glossary); trúng **một** phần tử bất kỳ là đủ.
- `evidence` được lấy **nguyên văn từ text chunk** (để `evidence in chunk.text` đúng như starter yêu cầu). 18/27 đoạn chỉ khác bản Day 6 ở khoảng trắng/xuống dòng; bản gốc giữ ở `evidence_day6`. Kiểm tra: `match_key(evidence) == match_key(evidence_day6)` cho cả 18.
- Mọi evidence nằm trọn trong **một** chunk B đúng nguồn + trang (27/27).
- `filter` (`{"chapter_id": ...}`, 5 câu) là **phạm vi do người dùng cung cấp trước** (câu hỏi nêu tên chương bằng lời), không suy ra từ gold. Filter là cả chương, không phải trang gold.

## Câu thiếu evidence

Chọn chủ đề **gần** một chương có thật nhưng sách không đề cập (sách viết cho Python 3 năm 2015, không có các tính năng/kỹ thuật này):

| ID | Split | Câu hỏi (tóm tắt) | Gần chương | Kiểm tra trong corpus |
|---|---|---|---|---|
| du1 | dev | `with` statement tự đóng file | ch14 Files (chỉ dùng `open()`/`close()`) | regex `with … open`, `__enter__/__exit__`, `context manager` → 0 |
| du2 | dev | viết decorator, cú pháp `@` | ch03/ch06 Functions | `decorat`, `@name` trước `def` → 0 |
| tu1 | test | `async`/`await`, coroutine chạy đồng thời | ch19 (generator) | `async`, `await`, `asyncio`, `coroutine`, `concurren` → 0 |
| tu2 | test | `super()` gọi `__init__` của lớp cha | ch18 Inheritance | `super(` → 0 (chỉ có "Superstitious" ở p222) |

Kiểm tra quét **toàn bộ 528 chunk** (không dựa vào top-k), nên kết luận "thiếu evidence" dựa trên cả corpus. Các câu này không vào mẫu số của retrieval metrics. Hành vi mong đợi: agent có tìm (`search`) rồi từ chối/nói không đủ bằng chứng, không thêm khẳng định ngoài tài liệu.

## Quy tắc chấm evidence (dùng cho Hit@1, Evidence Hit@3, Context Evidence Rate)

Một chunk là **hit** khi cùng `source_id` + `page` với một phần tử `gold` **và** chứa evidence sau chuẩn hóa `match_key` (NFC → bỏ gạch nối cuối dòng → bỏ mọi khoảng trắng → chữ thường) — giống Day 6 (`src/benchmark.py: evidence_hit`).
- **Hit@1 / Evidence Hit@3**: có hit ở rank 1 / trong top-3, chia cho số câu có đáp án của split (dev 16, test 6). Luôn xuất top-3 kể cả khi pipeline dùng top-k khác.
- **Context Evidence Rate**: context cuối gửi model chứa ít nhất một chunk hit (mỗi câu chỉ cần một đoạn evidence) / số câu có đáp án.

## Tiêu chí chọn cấu hình (chốt trước khi chạy test)

Chỉ dùng **dev**. Theo thứ tự, bước sau chỉ dùng khi các ứng viên hòa ở bước trước:
1. **Context Evidence Rate** dev cao nhất; các cấu hình kém nhất ≤ 1 câu (1/16) coi như hòa.
2. **Grounded answer** trung bình (/2) trên dev cao nhất (chênh ≤ 0,1 coi như hòa).
3. **Abstention**: không từ chối nhầm nhiều hơn và vẫn từ chối đúng 2/2 câu thiếu evidence dev.
4. **Thời gian/chi phí** trung bình mỗi câu thấp hơn (vd model lite thắng nếu hòa ở 1–3).
5. Vẫn hòa → cấu hình đơn giản hơn (ít tool/lượt gọi hơn).

Test chạy **một lần** cho baseline và cấu hình đã chọn; kết quả test chỉ báo cáo, không dùng để chỉnh.

## Nguy cơ rò rỉ / giới hạn

- **Test Day 6 đã từng chạy** (2026-11-14) để báo cáo Hit@1/Hit@3 của 3 cách chunk A/B/C; không dùng để chỉnh cấu hình Day 6 và Day 7 dùng phương pháp retrieval/agent mới. Vẫn ghi là giới hạn: người làm đã thấy kết quả retrieval trên test (vd t05 trượt ở B).
- Cùng một cuốn sách, cùng tác giả → dev/test không độc lập hoàn toàn về chủ đề (vd `hashable` ở ch11 dev và appendix_B test).
- Câu hỏi do người làm viết sau khi đọc trang gold → có thể trùng từ với evidence, có lợi cho lexical retrieval. Câu `paraphrase` được viết lại để giảm trùng từ.
- Test nhỏ (6 + 2 câu): mỗi câu có đáp án = 16,7 điểm % → chỉ minh họa, không kết luận tổng quát.
- Người chấm là học viên (tác giả benchmark) → có thể thiên lệch; ghi lý do cho từng nhãn.

## Nhật ký

- 2026-11-16: tạo benchmark Day 7 từ 22 câu Day 6 + 4 câu thiếu evidence; verify: 27/27 evidence, 4/4 absence, starter validate ok.
- 2026-11-16: **chốt benchmark + tiêu chí chọn ở commit `88e0d72`**, trước khi chạy bất kỳ retrieval nào của Day 7 (GĐ3 chỉ chạy dev).
