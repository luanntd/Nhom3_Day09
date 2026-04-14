# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** Day08-RAG-Team  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Vũ Hoàng Minh | Tech Lead + Retrieval Owner |  |
| Thái Tuấn Khang | Eval Owner + Retrieval Owner |  |
| Nguyễn Thành Luân | Documentation Owner + Retrieval Owner |  |

**Ngày nộp:** 2026-04-13  
**Repo:** 2A202600204_NguyenThanhLuan_Day08
**Độ dài khuyến nghị:** 600–900 từ

---

## 1. Pipeline nhóm đã xây dựng

**Chunking decision:**
> Nhóm dùng chunk_size=400 tokens và overlap=80 tokens. Chiến lược cắt theo section heading trước, sau đó mới cắt theo độ dài để tránh mất nghĩa giữa các điều khoản policy/SLA.

**Embedding model:**
> OpenAI text-embedding-3-small, lưu vector vào ChromaDB (cosine similarity).

**Retrieval variant (Sprint 3):**
> Variant đã chọn là hybrid retrieval (dense + BM25 + RRF), với giả thuyết ban đầu rằng query có alias/keyword như Approval Matrix, ERR-code sẽ được cải thiện nhờ sparse matching.

---

## 2. Quyết định kỹ thuật quan trọng nhất

**Quyết định:** Dùng LLM-as-Judge có rubric rõ và hậu xử lý abstain cho câu thiếu ngữ cảnh

**Bối cảnh vấn đề:**
Pipeline ban đầu dùng heuristic/fallback chấm điểm nên một số câu dạng abstain đúng (đặc biệt q09 và gq07) vẫn bị chấm thấp, làm sai lệch đánh giá chất lượng thật. Điều này ảnh hưởng trực tiếp Sprint 4 vì scorecard và tuning-log sẽ không phản ánh đúng hành vi anti-hallucination mà lab yêu cầu.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Heuristic scoring | Nhanh, không tốn thêm API call | Không bám ngữ nghĩa tốt, dễ chấm sai abstain |
| LLM-as-Judge có rubric JSON | Linh hoạt theo ngữ cảnh, giải thích được notes | Tốn API và cần parse ổn định |

**Phương án đã chọn và lý do:**
Nhóm chọn LLM-as-Judge và bổ sung 3 lớp ổn định: bắt output JSON mode, normalize score về 1-5, retry khi parse lỗi. Ngoài ra thêm rule hậu xử lý cho câu không có expected sources: nếu answer abstain rõ ràng thì reward theo anti-hallucination.

**Bằng chứng từ scorecard/tuning-log:**
Baseline sau khi chuẩn hóa judge đạt Faithfulness 4.80, Relevance 4.90, Context Recall 5.00, Completeness 4.10.

---

## 3. Kết quả grading questions

**Ước tính điểm raw:** Chưa chấm tay theo từng criterion, nhưng log đủ 10 câu để giảng viên chấm /98

**Câu tốt nhất:** ID: gq06 — Lý do: tổng hợp đúng quy trình cấp quyền tạm thời trong incident, có nguồn từ nhiều tài liệu liên quan.

**Câu fail:** ID: gq08 — Root cause: answer còn thiên về mô tả tổng quát, có nguy cơ thiếu độ sắc nét về phân biệt policy trong ngữ cảnh 3 ngày.

**Câu gq07 (abstain):** Pipeline trả lời Không đủ dữ liệu về vấn đề này, phù hợp quy tắc anti-hallucination trong SCORING.

---

## 4. A/B Comparison — Baseline vs Variant

**Biến đã thay đổi (chỉ 1 biến):** retrieval_mode (dense -> hybrid)

| Metric | Baseline | Variant | Delta |
|--------|---------|---------|-------|
| Faithfulness | 4.80/5 | 4.70/5 | -0.10 |
| Relevance | 4.90/5 | 4.70/5 | -0.20 |
| Context Recall | 5.00/5 | 5.00/5 | +0.00 |
| Completeness | 4.10/5 | 3.90/5 | -0.20 |

**Kết luận:**
Variant hybrid kém hơn baseline trên bộ test hiện tại. Điểm giảm rõ nhất ở relevance và completeness, đặc biệt q07 chưa cải thiện như kỳ vọng. Vì vậy nhóm quyết định dùng baseline dense làm cấu hình chính để chạy grading_questions.

---

## 5. Phân công và đánh giá nhóm

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Vũ Hoàng Minh | Lead kỹ thuật, kiểm tra indexing/chunking, triển khai và thử nghiệm hybrid retrieval | 1, 3 |
| Thái Tuấn Khang | Dense retrieval baseline, chạy evaluation baseline/variant, rà soát grading log | 2, 4 |
| Nguyễn Thành Luân | Hoàn thiện architecture.md, tuning-log.md, tổng hợp A/B và viết group report | 4 |

**Điều nhóm làm tốt:**
Pipeline chạy end-to-end ổn định, artifacts đầy đủ (scorecard, log grading, docs). Nhóm bám A/B rule nghiêm túc, có bằng chứng định lượng trước khi kết luận.

**Điều nhóm làm chưa tốt:**
Chưa kịp thử Variant 2 thật sự bằng một lần chạy độc lập có số liệu riêng. Một số câu alias vẫn cần thêm query transform để tăng completeness.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì?

Nhóm sẽ ưu tiên query expansion theo alias map trước retrieval (ví dụ Approval Matrix -> Access Control SOP), sau đó thử rerank cross-encoder cho top-10 -> top-3 để giảm nhiễu. Mỗi lần chỉ đổi một biến và đo lại trên cùng bộ test để giữ tính so sánh. Mục tiêu là tăng completeness ở q07/q10 mà không làm giảm faithfulness.