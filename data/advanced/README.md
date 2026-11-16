# Thử thách nâng cao — WHO *World health statistics 2023*

## Tài liệu
- *World health statistics 2023: monitoring health for the SDGs, sustainable development goals*, WHO, 2023. ISBN 9789240074323. Nguồn: https://www.who.int/publications/i/item/9789240074323
- Giấy phép **CC BY-NC-SA 3.0 IGO** (dùng phi thương mại, ghi nguồn, chia sẻ cùng giấy phép). File PDF **không commit**; tải về và đặt ở `starter/data/advanced/9789240074323-eng.pdf` (thư mục đã bị `.gitignore` của đề bỏ qua). sha256 `26292b8da46851a146e02861356fded41fc408f65597b9ec18d4fcd94d9b6674`, 136 trang PDF (119 trang đánh số; trang in = trang PDF − 12).
- Dữ liệu trích xuất trong repo (`chunks.json`, `vision.json`) là tác phẩm phái sinh, giữ cùng giấy phép CC BY-NC-SA 3.0 IGO.

## Index (`src/advanced/ingest.py`, `index.py`)
| Loại chunk | Cách làm | Số chunk |
|---|---|---:|
| text | Đoạn văn từ text layer (pymupdf), ≤ 1400 ký tự, không vượt trang; bỏ 32 trang bảng phụ lục | 257 |
| table | Annex 1 (PDF p96–127): mỗi quốc gia/vùng × mỗi phần (1-1…1-4) = 1 chunk; ghép trang trái (tên nước) với trang phải (cùng thứ tự dòng); nhãn cột = chỉ số + loại số liệu + giới + năm | 824 |
| visual | 39 trang có biểu đồ/bản đồ/sơ đồ: render 150 dpi → `gemini-3.5-flash` chép tiêu đề, loại hình, trục/đơn vị, chú giải, mọi số in trên hình, ghi chú; giá trị không in được đánh dấu "≈" | 99 |

Không xử lý được / bỏ: 10 trang trống hoặc chỉ có hình trang trí (p2, 6, 12, 44, 94, 132–136: bìa, trang trắng); ảnh trang bìa chương (p13, 45, 83) chỉ có tiêu đề. Giá trị biểu đồ không in số chỉ có ước lượng "≈". Kiểm tra vision so với bản gốc: `results/advanced/vision_check.json` (13 trang, 3 lỗi được ghi).

Vector store: bảng riêng `adv_chunks` trong Postgres/pgvector của Day 6 (bảng `chunks` Day 6 không đổi), `bge-base-en-v1.5` 768 chiều; 415/1180 chunk dài hơn 512 token bị cắt khi embed (BM25 vẫn dùng toàn văn).

## Benchmark (`questions.json`, `cases.json`)
Chia dev/test **trước khi thử nghiệm**; dev và test không trùng câu trả lời.

| Nhóm | Dev | Test | Yêu cầu test |
|---|---:|---:|---:|
| Bảng (Annex 1, bảng hình 2.12) | 3 | 6 | ≥ 6 |
| Ảnh, sơ đồ (bản đồ 1.2/1.6/1.16/2.2/2.19, dòng thời gian 3.3) | 3 | 5 | ≥ 5 |
| Biểu đồ (1.12, 2.5b, 2.7, 2.13, 2.20b, 3.1, 3.2) | 3 | 5 | ≥ 5 |
| Multi-hop (≥ 2 trang/bảng/hình) | 2 | 4 | ≥ 4 |
| Text | 4 | 4 | ≥ 4 |
| Thiếu bằng chứng | 3 | 6 | ≥ 6 |
| **Tổng** | **18** | **30** | **≥ 30** |

Mỗi câu có đáp án ghi trang PDF và vùng evidence (hàng/cột bảng, hình/nhãn), đơn vị và phép tính. Câu thiếu bằng chứng ghi cách kiểm tra (regex quét toàn bộ 1180 chunk gồm cả bản chép hình = 0 kết quả). Kiểm chứng tự động: `python -m src.run adv bench` → `results/advanced/benchmark_verify.json`. Agent chỉ đọc `cases.json` (không có đáp án/evidence).

## Chấm
ADVANCED §3: mỗi câu test **đạt / không đạt**, đối chiếu bản gốc PDF; lỗi hệ thống/timeout = không đạt; tỷ lệ = đạt / 30, cần ≥ 27/30. Nhãn: AI hỗ trợ, gợi ý; học viên duyệt và xác nhận — đọc lại câu trả lời, đối chiếu với text chunk và trang gốc.

## Tiêu chí chọn cấu hình (chốt 2026-11-16, sau lượt dev đầu `a_hybrid`, trước khi chạy test)
1. Số câu dev **đạt** cao nhất (theo cách chấm trên).
2. Hòa → chi phí/câu thấp hơn.
3. Vẫn hòa → ít lượt search hơn.
Test chạy **một lần** với cấu hình đã chọn.

## Nhật ký
- 2026-11-16: ingest + vision ($1.01, 39 trang), index 1180 chunk, benchmark 48 câu; dev `a_hybrid`: 17/18 (ad_mh2 từ chối nhầm vì evidence p062:t01 bị bỏ do budget 12000 đầy).
- 2026-11-16: dev `a_hybrid_k8` (top-8, budget 20000, ≤ 5 search): 18/18 → chọn `a_hybrid_k8` (results/advanced/selection.json, 07:22 UTC) trước khi chạy test.
- 2026-11-16: test chạy 1 lần (07:22–07:35 UTC): gợi ý chấm 28/30 = 93,3 % (bảng 6/6, ảnh 5/5, biểu đồ 4/5, multi-hop 3/4, text 4/4, thiếu 6/6); 2 câu trượt (at_ch3, at_mh4) do evidence đã tìm thấy nhưng bị bỏ vì budget 20000 đầy. Chi phí test $1.08.
- 2026-11-16: phát hiện sau test: regex kiểm tra vắng mặt của at_u1 bỏ sót câu p34 'As of March 2023, about 13 billion doses…'. Câu hỏi hỏi số cuối 2022 nên vẫn không có evidence; **không sửa câu hỏi sau khi xem kết quả**, chỉ ghi lại.
