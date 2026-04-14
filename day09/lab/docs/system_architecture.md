# System Architecture — Lab Day 09

**Nhóm:** Nhóm 3  
**Ngày:** 2026-04-14  
**Version:** 1.0

---

## 1. Tổng quan kiến trúc

> Mô tả ngắn hệ thống của nhóm: chọn pattern gì, gồm những thành phần nào.

**Pattern đã chọn:** Supervisor-Worker  
**Lý do chọn pattern này (thay vì single agent):**

Thay vì gom tất cả context vào một prompt khổng lồ như Single Agent, Supervisor-Worker cho phép gọi từng component một cách tách biệt. Điều này giúp dễ quản lý luồng dữ liệu, hỗ trợ gọi External Tools (qua MCP server) một cách độc lập không bị lẫn vào luồng context LLM, đồng thời bổ sung cờ HITL (Human In The Loop) với những truy vấn nguy hiểm (Risk factor) mà model LLM dễ bị Hallucinate (ảo giác).

---

## 2. Sơ đồ Pipeline

> Vẽ sơ đồ pipeline dưới dạng text, Mermaid diagram, hoặc ASCII art.
> Yêu cầu tối thiểu: thể hiện rõ luồng từ input → supervisor → workers → output.

**Sơ đồ thực tế của nhóm:**

```
User Query
     │
     ▼
┌────────────────┐
│   Supervisor   │
│ (keyword match)│ 
└──────┬─────────┘
       │
      /|\
     / │ \
    /  │  \ route_decision
   /   │   \
  ▼    ▼    ▼
 Retrieval Policy Tool
 Worker    Worker ---→ MCP Server
  │        │ (LLM GPT-4o-mini & JSON Format)
  │        │
  └───┬────┘
      │
      ▼
 Synthesis Worker
 (LLM + Confidence Metric)
      │
      ▼
 Final Output & Trace
```

---

## 3. Vai trò từng thành phần

### Supervisor (`graph.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Phân loại intent của user query và rẽ nhánh luồng dữ liệu. |
| **Input** | `state["task"]` (Câu hỏi của user) |
| **Output** | supervisor_route, route_reason, risk_high, needs_tool |
| **Routing logic** | Rule-based (Keyword matching) với các list "refund, flash sale" -> policy, "P1, ticket" -> retrieval. |
| **HITL condition** | `task` có chứa "err-xxx" cộng cờ risk_high sẽ route vào "human_review". |

### Retrieval Worker (`workers/retrieval.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Tìm kiếm dữ liệu liên quan từ vector db (Semantic search). |
| **Embedding model** | `all-MiniLM-L6-v2` từ thư viện `sentence_transformers` |
| **Top-k** | Default 5 |
| **Stateless?** | Yes |

### Policy Tool Worker (`workers/policy_tool.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Phân tích JSON properties bằng GPT-4o-mini để bắt lỗi ngoại lệ dựa vào quy định công ty. |
| **MCP tools gọi** | `search_kb`, `check_access_permission`, `get_ticket_info` |
| **Exception cases xử lý** | flash_sale_exception, digital_product_exception, activated_exception |

### Synthesis Worker (`workers/synthesis.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **LLM model** | `gpt-4o-mini` qua thư viện gốc `openai` |
| **Temperature** | 0.1 |
| **Grounding strategy** | Đưa chunks kèm policy_rules vào system context để khống chế output. Bắt buộc trích xuất Source citation. |
| **Abstain condition** | Khi câu trả lời LLM sinh ra là "Không đủ thông tin" hoặc khi điểm average chunk score tự tính điểm < 0.4. |

### MCP Server (`mcp_server.py`)

| Tool | Input | Output |
|------|-------|--------|
| search_kb | query, top_k | chunks, sources |
| get_ticket_info | ticket_id | ticket details |
| check_access_permission | access_level, requester_role | can_grant, approvers |
| mcp_http_fastapi | Request payload với endpoints | Standard JSON Tool Result Response |

---

## 4. Shared State Schema

> Liệt kê các fields trong AgentState và ý nghĩa của từng field.

| Field | Type | Mô tả | Ai đọc/ghi |
|-------|------|-------|-----------|
| task | str | Câu hỏi đầu vào | supervisor đọc |
| supervisor_route | str | Worker được chọn | supervisor ghi |
| route_reason | str | Lý do route | supervisor ghi |
| retrieved_chunks | list | Evidence từ retrieval | retrieval ghi, synthesis đọc |
| policy_result | dict | Kết quả kiểm tra policy | policy_tool ghi, synthesis đọc |
| mcp_tools_used | list | Tool calls đã thực hiện | policy_tool ghi |
| final_answer | str | Câu trả lời cuối | synthesis ghi |
| confidence | float | Mức tin cậy | synthesis ghi |
| risk_high | bool | Cờ cảnh báo tác vụ không an toàn | supervisor ghi, policy_tool đọc |

---

## 5. Lý do chọn Supervisor-Worker so với Single Agent (Day 08)

| Tiêu chí | Single Agent (Day 08) | Supervisor-Worker (Day 09) |
|----------|----------------------|--------------------------|
| Debug khi sai | Khó — không rõ lỗi ở đâu | Dễ hơn — test từng worker độc lập thông qua Trace logs |
| Thêm capability mới | Phải sửa toàn prompt | Thêm worker/MCP tool riêng độc lập |
| Routing visibility | Không có | Có route_reason trong trace (VD: 56% Retrieval, 43% Policy) |
| LLM Hallucination | Tỷ lệ cao, hay bịa thêm ý | Kiểm soát triệt để, có abstain metric dựa trên confidence |

**Nhóm điền thêm quan sát từ thực tế lab:**

Với mô hình Multi-Agent này, chúng ta có thể mở rộng được HTTP Request từ ngoài vào `mcp_server` để kết nối vào luồng RAG. Lượng Tokens chạy qua LLM tuy nhiều hơn, độ trễ lâu hơn, nhưng rào được hoàn toàn các rủi ro như cho phép user refund sai sản phẩm kĩ thuật số. 

---

## 6. Giới hạn và điểm cần cải tiến

> Nhóm mô tả những điểm hạn chế của kiến trúc hiện tại.

1. Model Embeddings (Sentence Transformers) vẫn đang bị Re-load trên mỗi lần Agent gọi (ở `retrieval.py`), điều này làm Server chiếm nhiều RAM và Latency lớn.
2. Hard-code rule based Route ở Supervisor sẽ không hoạt động tốt nếu keyword của user mập mờ, thiếu dữ kiện.
3. Không có Self-Corretion Workflow để auto re-route khi Confidence xuống quá thấp.
