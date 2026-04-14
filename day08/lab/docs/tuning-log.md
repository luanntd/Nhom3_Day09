# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  
**Config:**
```
embedding_model = "text-embedding-3-small" (OpenAI)
retrieval_mode = "dense"
chunk_size = 400 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.80/5 |
| Answer Relevance | 4.90/5 |
| Context Recall | 5.00/5 |
| Completeness | 4.10/5 |

**Câu hỏi yếu nhất (điểm thấp):**
- q10 (VIP refund): faithfulness=4/5, completeness=3/5 do policy không có quy trình VIP riêng và câu trả lời chưa nêu đủ mốc thời gian xử lý chuẩn.
- q07 (Approval Matrix): faithfulness=4/5, completeness=4/5 do truy hồi đúng Access Control SOP nhưng vẫn thiếu diễn giải rõ tên cũ/tên mới.
- q01/q04/q05/q06/q08: completeness=4/5 vì có đủ ý chính nhưng còn thiếu 1 chi tiết phụ theo expected answer.

**Giả thuyết nguyên nhân (Error Tree):**
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [x] Retrieval: Dense bỏ lỡ exact keyword / alias
- [ ] Retrieval: Top-k quá ít -> thiếu evidence
- [x] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài -> lost in the middle

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13  
**Biến thay đổi:** retrieval_mode = dense -> hybrid (dense + BM25 + RRF)  
**Lý do chọn biến này:**
> Baseline cho thấy các câu chứa alias/thuật ngữ riêng (q07, q09) vẫn yếu. Vì vậy chọn hybrid để tăng khả năng match keyword exact (BM25) trong khi vẫn giữ ngữ nghĩa từ dense embedding.

**Config thay đổi:**
```
retrieval_mode = "hybrid"
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.80/5 | 4.70/5 | -0.10 |
| Answer Relevance | 4.90/5 | 4.70/5 | -0.20 |
| Context Recall | 5.00/5 | 5.00/5 | +0.00 |
| Completeness | 4.10/5 | 3.90/5 | -0.20 |

**Nhận xét:**
> Variant 1 không cải thiện chất lượng tổng thể. Các câu q02-q05 giữ gần như tương đương, nhưng q06 và q07 giảm rõ; q10 có faithfulness cao hơn nhưng relevance thấp hơn, nên tổng thể vẫn kém baseline.

**Kết luận:**
> Variant 1 không tốt hơn baseline. Bằng chứng: cả 3 metric chính đều giảm (faithfulness, relevance, completeness), chỉ context recall giữ nguyên. Quyết định giữ baseline dense cho pipeline chính.

---

## Variant 2 (nếu có thời gian)

**Biến thay đổi:** Prompt grounding nghiêm ngặt hơn cho câu hỏi thiếu dữ liệu  
**Config:**
```
prompt rule:
- chi tra loi dua tren context retrieve
- neu khong co du lieu cu the thi tra loi "Toi khong biet" hoac "Khong du du lieu"
- uu tien trich dan [1], [2]
```

**Scorecard Variant 2:**
| Metric | Baseline | Variant 1 | Variant 2 | Best |
|--------|----------|-----------|-----------|------|
| Faithfulness | 4.80 | 4.70 | N/A | Baseline |
| Answer Relevance | 4.90 | 4.70 | N/A | Baseline |
| Context Recall | 5.00 | 5.00 | N/A | Tie |
| Completeness | 4.10 | 3.90 | N/A | Baseline |

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
	> Mismatch giữa alias trong câu hỏi và thuật ngữ canonical trong tài liệu (ví dụ "Approval Matrix" vs "Access Control SOP"), làm giảm chất lượng answer dù recall nguồn vẫn cao.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
	> Retrieval mode. Việc chuyển từ dense sang hybrid làm giảm đáng kể faithfulness/relevance/completeness trên bộ test hiện tại.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
	> Thử query expansion theo alias map trước retrieval (giữ dense), sau đó đo lại q07 và q10 để kiểm chứng cải thiện completeness mà không làm giảm relevance.

