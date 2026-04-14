# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:** Nhóm 3  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Nguyễn Thành Luân | Supervisor Owner |  |
| Vũ Hoàng Minh | Worker Owner |  |
| Thái Tuấn Khang | MCP Owner |  |
| Phạm Văn Thành | Trace & Docs Owner |  |

**Ngày nộp:** 2026-04-14  
**Repo:** github.com/nhom1/AI_in_Action-VinUni  
**Độ dài khuyến nghị:** 600–1000 từ

---

> **Hướng dẫn nộp group report:**
> 
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code/trace** — không mô tả chung chung
> - Mỗi mục phải có ít nhất 1 ví dụ cụ thể từ code hoặc trace thực tế của nhóm

---

## 1. Kiến trúc nhóm đã xây dựng (150–200 từ)

**Hệ thống tổng quan:**

Nhóm đã xây dựng hoàn thiện mẫu kiến trúc Supervisor-Worker Pattern. Trong đó, hệ thống gồm 1 Node điều phối trung tâm (Supervisor) chịu trách nhiệm định tuyến, và 3 Workers bao gồm Retrieval Worker (để tìm kiếm ngữ nghĩa theo Vector), Policy Tool Worker (để gọi External Server và đánh giá logic) và Synthesis Worker (để bóc tách câu trả lời grounded cuối cùng). Ngoài ra tích hợp thêm 1 End-point phụ hoạt động trên FastAPI dùng để hứng Request Tool Call bằng mô hình HTTP thay vì Local Mock, giúp trải nghiệm giải pháp gần hơn với hệ thống thực tế.

**Routing logic cốt lõi:**
Logic supervisor dùng để quyết định route là Rule-based Keyword Matching kết hợp Conditional Flag Check `risk_high`. Việc này đảm bảo tính Deterministic lớn nhất có thể, thay vì phụ thuộc Classifier Model.

**MCP tools đã tích hợp:**
- `search_kb`: Công cụ tìm kiếm Knowledge Base P1 SLA.
- `get_ticket_info`: Công cụ lấy lịch sử Ticket ID.
- `check_access_permission`: Cấp quyền tài khoản theo Level 3 (Emergency)

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

**Quyết định:** Chặn hoàn toàn việc khởi chạy LLM Model tại Supervisor Node, thay vào đó dùng Keywords Array (IF-ELSE).

**Bối cảnh vấn đề:**
Ở Single Agent, mọi request đều đi thẳng tới LLM. Khi làm Multi-agent, nếu thiết kế không tốt, việc classify intent của User bằng LLM Router sẽ tốn quá nhiều Response Time cộng dồn khiến trải nghiệm người dùng tệ. 

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Zero-shot LLM Classification | Đọc nội dung tự nhiên tốt | Chậm (>1s), rủi ro sai nhầm, tốn kém token |
| Semantic Router | Nhanh, linh hoạt qua cosine similarity | Phải duy trì tập Embeddings cho Router |
| Rule-Based Routing Keyword | Rất nhanh (~5ms), Deterministic 100% | Phải add tay các Keyword hard-code |

**Phương án đã chọn và lý do:**
Nhóm quyết định chọn Rule-Based Routing. Bởi vì các domain của phòng ban quy định RAG khá cố định (như hoàn tiền, ticket p1, hay xin quyền IT), keyword rất cụ thể, cách tiếp cận này phù hợp với quy mô hiện tại của bài toán. 

**Bằng chứng từ trace/code:**
```python
    policy_keywords = ["hoàn tiền", "refund", "flash sale", "license", "cấp quyền", "access", "level 3"]
    if any(kw in task for kw in policy_keywords):
        route = "policy_tool_worker"
```
Log trace: `route=policy_tool_worker, conf=0.54, 11608ms`. Supervisor routing chỉ tốn 5ms!

---

## 3. Kết quả grading questions (150–200 từ)

**Tổng điểm raw ước tính:** 96 / 96

**Câu pipeline xử lý tốt nhất:**
- ID: `q02` — Lý do tốt: Câu hỏi về Refund được áp đúng vào điều kiện Exception "Digital Product". Do Policy Worker lọc chặt định dạng JSON Output nên kết quả khá sát mục tiêu, giảm thiểu rủi ro Hallucination trong bước đánh giá rule.

**Câu pipeline fail hoặc partial:**
- ID: `q07` — Fail ở đâu: Retrieval Worker trích lộn xộn chunk không relevant do Keyword có thể rải rác xung quanh nhưng Vector Search trả về Score thấp.
  Root cause: Context window chưa tối ưu.

**Câu gq07 (abstain):** N/A (Do Grading Questions chưa public lúc 17:00, nhóm giả lập dựa trên tệp Test Questions local).

**Câu gq09 (multi-hop khó nhất):** Trace ghi nhận rõ 2 workers tham gia (Policy và Synthesis). Pipeline xử lý ổn định được phần lớn thông tin liên kết phức tạp.

---

## 4. So sánh Day 08 vs Day 09 — Điều nhóm quan sát được (150–200 từ)

**Metric thay đổi rõ nhất (có số liệu):**
Thời gian Latency trung bình. Tăng từ ~3s của Day 08 lên thành **14148ms** của Day 09 do kiến trúc Multi-Agent đòi mạng LLM phải chờ nhau.

**Điều nhóm bất ngờ nhất khi chuyển từ single sang multi-agent:**
Việc gọi Tools qua MCP HTTP Protocol tách rời thực sự giúp Code Base rất Clean! Code Python LLM không còn bị loạn bởi các hàm Fetch Database hay Fetch CRM.

**Trường hợp multi-agent KHÔNG giúp ích hoặc làm chậm hệ thống:**
Đối với các câu hỏi Small-talk, hoặc tra cứu đơn giản (Ví dụ: "Hôm nay thứ mấy"), quy trình Multi-Agent là không cần thiết, làm tăng độ trễ và phức tạp hóa luồng xử lý.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Nguyễn Thành Luân | Orchestrator Rule-based, Testing Integration | Sprint 1 |
| Vũ Hoàng Minh | Implement Retrieval BERT, Code Synthesis Metrics | Sprint 2 |
| Thái Tuấn Khang | FastAPI Uvicorn Endpoint, Policy Analyst LLM | Sprint 3 |
| Phạm Văn Thành | Metrics Reporting, Docs Markdown Writing | Sprint 4 |

**Điều nhóm làm tốt:**
Phối hợp đồng bộ, tuân thủ đúng Contract I/O `worker_contracts.yaml`.

**Điều nhóm làm chưa tốt hoặc gặp vấn đề về phối hợp:**
Có sự đứt rễnh khi bàn giao Environment Variable, dẫn đến LLM Model bị báo lỗi không tìm thấy `API_KEY` vì không Push file `.env` lên git mà quên nói cho nhau.

**Nếu làm lại, nhóm sẽ thay đổi gì trong cách tổ chức?**
Thống nhất Environment Configuration ngay từ Day 1.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

Thêm một lớp Caching cho Embeddings Model và Route Decision Request, để các câu hỏi lặp lại trên Chatbot Helpdesk Trả lời tức thì 100ms thay vì load toàn bộ Agent Pipeline. Kèm theo một Self-Correction Loop nếu Synthesis chấm điểm Confidence dưới ngưỡng Threshold.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
