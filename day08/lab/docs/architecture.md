# Architecture — RAG Pipeline (Day 08 Lab)

> Template: Điền vào các mục này khi hoàn thành từng sprint.
> Deliverable của Documentation Owner.

## 1. Tổng quan kiến trúc

```
[Raw Docs (5 files .txt)]
    ↓
[index.py: Preprocess → Chunk → Embed → Store]
    ↓
[ChromaDB Vector Store (29 chunks)]
    ↓
[rag_answer.py: Query → Retrieve → Rerank → Generate]
    ↓
[Grounded Answer + Citation]
```

**Mô tả ngắn gọn:**
> Hệ thống trợ lý nội bộ cho khối CS + IT Helpdesk, trả lời câu hỏi về chính sách, SLA ticket, quy trình cấp quyền và FAQ bằng chứng cứ retrieve có kiểm soát. Pipeline sử dụng ChromaDB vector store, OpenAI embedding (`text-embedding-3-small`) và OpenAI chat model (`gpt-4o-mini`) để tạo câu trả lời grounded kèm citation.

---

## 2. Indexing Pipeline (Sprint 1)

### Tài liệu được index
| File | Nguồn | Department | Số chunk |
|------|-------|-----------|---------|
| `policy_refund_v4.txt` | policy/refund-v4.pdf | CS | 6 |
| `sla_p1_2026.txt` | support/sla-p1-2026.pdf | IT | 5 |
| `access_control_sop.txt` | it/access-control-sop.md | IT Security | 7 |
| `it_helpdesk_faq.txt` | support/helpdesk-faq.md | IT | 6 |
| `hr_leave_policy.txt` | hr/leave-policy-2026.pdf | HR | 5 |

### Quyết định chunking
| Tham số | Giá trị | Lý do |
|---------|---------|-------|
| Chunk size | 400 tokens (~1600 ký tự) | Cân bằng giữa context và precision, tránh chunk quá dài |
| Overlap | 80 tokens (~320 ký tự) | Đảm bảo continuity giữa chunks, tránh mất thông tin ở biên |
| Chunking strategy | Heading-based + paragraph-based | Ưu tiên cắt tại section heading (===), sau đó paragraph để giữ cấu trúc tự nhiên |
| Metadata fields | source, section, effective_date, department, access | Phục vụ filter theo department, freshness check, access control, và citation |

### Embedding model
- **Model**: text-embedding-3-small (OpenAI Embeddings API)
- **Vector store**: ChromaDB (PersistentClient, cosine similarity)
- **Similarity metric**: Cosine

---

## 3. Retrieval Pipeline (Sprint 2 + 3)

### Baseline (Sprint 2)
| Tham số | Giá trị |
|---------|---------|
| Strategy | Dense (embedding similarity) |
| Top-k search | 10 |
| Top-k select | 3 |
| Rerank | Không |

### Variant (Sprint 3)
| Tham số | Giá trị | Thay đổi so với baseline |
|---------|---------|------------------------|
| Strategy | Hybrid (dense + sparse với RRF) | Thêm BM25 sparse retrieval kết hợp với dense |
| Top-k search | 10 | Giữ nguyên |
| Top-k select | 3 | Giữ nguyên |
| Rerank | Không | Giữ nguyên |
| Query transform | Không | Giữ nguyên |

**Lý do chọn variant này:**
> Chọn hybrid vì corpus có cả văn bản chính sách tự nhiên (policy, FAQ) và nhiều keyword/alias quan trọng (P1, refund, Level 3, ERR-403). Dense retrieval tốt với ngữ nghĩa nhưng có thể bỏ lỡ exact term; sparse BM25 bổ sung khả năng tìm keyword chính xác, kết hợp bằng Reciprocal Rank Fusion để cân bằng cả hai.

---

## 4. Generation (Sprint 2)

### Grounded Prompt Template
```
You are a helpful assistant that answers questions based on the provided context.
IMPORTANT RULES:
1) Do NOT use external knowledge or make guesses.
2) If specific information is missing, answer "Tôi không biết" or "Không đủ dữ liệu về vấn đề này."
3) If context is related but not exact, state what context says.
4) Add citations [1], [2], ... when possible.
5) Keep answer short (2-4 sentences), clear, factual.
6) Respond in the same language as the question.

Question: {query}

Context:
[1] {source} | {section} | score={score}
{chunk_text}

[2] ...

Answer:
```

### LLM Configuration
| Tham số | Giá trị |
|---------|---------|
| Model | gpt-4o-mini (OpenAI) |
| Temperature | 0 (để output ổn định cho eval) |
| Max tokens | 512 |

---

## 5. Failure Mode Checklist

> Dùng khi debug — kiểm tra lần lượt: index → retrieval → generation

| Failure Mode | Triệu chứng | Cách kiểm tra |
|-------------|-------------|---------------|
| Index lỗi | Retrieve về docs cũ / sai version | `inspect_metadata_coverage()` trong index.py |
| Chunking tệ | Chunk cắt giữa điều khoản | `list_chunks()` và đọc text preview |
| Retrieval lỗi | Không tìm được expected source | `score_context_recall()` trong eval.py |
| Generation lỗi | Answer không grounded / bịa | `score_faithfulness()` trong eval.py |
| Token overload | Context quá dài → lost in the middle | Kiểm tra độ dài context_block |

---

## 6. Diagram

```mermaid
graph LR
    A[User Query] --> B[OpenAI Embedding<br/>text-embedding-3-small]
    B --> C[ChromaDB Vector Search<br/>Cosine Similarity]
    C --> D[Top-10 Candidates]
    D --> E{Mode}
    E -->|Dense| G[Top-3 Select]
    E -->|Hybrid| F[BM25 Sparse + RRF]
    F --> G
    G --> H[Build Context Block + Citations]
    H --> I[Grounded Prompt]
    I --> J[OpenAI GPT-4o-mini<br/>Temperature=0]
    J --> K[Answer + Sources]
```
