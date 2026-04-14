# Routing Decisions Log — Lab Day 09

**Nhóm:** Nhóm 3  
**Ngày:** 2026-04-14

> **Hướng dẫn:** Ghi lại ít nhất **3 quyết định routing** thực tế từ trace của nhóm.
> Không ghi giả định — phải từ trace thật (`artifacts/traces/`).
> 
> Mỗi entry phải có: task đầu vào → worker được chọn → route_reason → kết quả thực tế.

---

## Routing Decision #1

**Task đầu vào:**
> "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?"

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task contains policy/access keyword`  
**MCP tools được gọi:** `search_kb` (với input query hỏi về thời gian hoàn tiền)  
**Workers called sequence:** `policy_tool_worker` -> `synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): "Có thể yêu cầu trong 5 ngày với rule Policy Refund V4"
- confidence: `0.30`
- Correct routing? Yes 

**Nhận xét:**

Quyết định hợp lý vì Key-word "hoàn tiền" đã kích hoạt trúng rule tại Supervisor. Thay vì truyền thẳng sang Retrieval, luồng xử lý được chuyển cho Policy Worker, giúp worker này có thể chủ động gọi Tool `search_kb` qua mạng MCP để lấy dữ kiện trước khi kiểm tra luật.

---

## Routing Decision #2

**Task đầu vào:**
> "Nhân viên được làm remote tối đa mấy ngày mỗi tuần?"

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `default route`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `retrieval_worker` -> `synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): "Nhân viên được làm remote tối đa 2 ngày theo HR Leave Policy."
- confidence: `0.71`
- Correct routing? Yes 

**Nhận xét:**

Sử dụng nhánh `default_route` là phương án phù hợp. Vì không thuộc luồng policy phức tạp, semantic search thông thường qua `retrieval_worker` vẫn đảm bảo thời gian phản hồi tốt và kết quả đúng.

---

## Routing Decision #3

**Task đầu vào:**
> Một task cố ý chứa lỗi `err-102` không thuộc văn bản hiểu được của module.

**Worker được chọn:** `human_review`  
**Route reason (từ trace):** `unknown error code → human review`  
**MCP tools được gọi:** Không  
**Workers called sequence:** `human_review`

**Kết quả thực tế:**
- final_answer (ngắn): Chặn tiến trình, Fallback.
- confidence: `0`
- Correct routing? Yes

**Nhận xét:**

Quyết định chính xác. Tận dụng tốt cờ HITL để chặn các tác vụ ngoài phạm vi xử lý thay vì để LLM tiếp tục tạo sinh kết quả sai.

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | 9 | 56% |
| policy_tool_worker | 7 | 43% |
| human_review | 1 | 6% |

(*Tổng count là > 15 do tính theo Trace node hit)

### Routing Accuracy

> Trong số 16 câu nhóm đã chạy, bao nhiêu câu supervisor route đúng?

- Câu route đúng: 16 / 16
- Câu route sai (đã sửa bằng cách nào?): 0
- Câu trigger HITL: 1

### Lesson Learned về Routing

> Quyết định kỹ thuật quan trọng nhất nhóm đưa ra về routing logic là gì?  
> (VD: dùng keyword matching vs LLM classifier, threshold confidence cho HITL, v.v.)

1. Sử dụng Keyword Matching mang lại độ phản hồi nhanh hơn so với mô hình LLM Classifier, giúp tiết kiệm thời gian xử lý bước đầu.
2. Thiết lập cấu hình Unknown Error tại mức Supervisor để ngắt luồng sớm, thay vì đợi bước Synthesis trả về Abstain làm trễ nhịp Pipeline.

### Route Reason Quality

> Nhìn lại các `route_reason` trong trace — chúng có đủ thông tin để debug không?  
> Nếu chưa, nhóm sẽ cải tiến format route_reason thế nào?

Chỉ có vài Route Reason quá chung chung (Như `default route`). Nhóm sẽ cải thiện bằng cách ghi thêm `default route - Keyword detected: none` để debug chắc chắn hơn LLM không miss Key word.
