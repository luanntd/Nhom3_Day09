# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Nguyễn Thành Luân  
**Vai trò trong nhóm:** Supervisor Owner  
**Ngày nộp:** 2026-04-14  

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

Trong Sprint 1 vừa qua, tôi chịu trách nhiệm chính ở việc xây dựng kiến trúc định tuyến Supervisor nhằm rẽ nhánh cho Graph. Cụ thể tôi đã cải tiến logic Router thành cơ chế Keyword-based matching cơ bản nhưng ổn định. Công việc của tôi đóng vai trò điều phối luồng xử lý chính, kết nối với phần cấu hình Server của bạn Khang để đảm bảo những nhánh Task không liên quan sẽ không kích hoạt gọi HTTP thừa.

**Module/file tôi chịu trách nhiệm:**
- File chính: `graph.py`
- Functions tôi implement: `supervisor_node(state: AgentState)`

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Graph do tôi phát triển là cánh cổng đầu tiên phân loại ý định của Request Input. Output State do Supervisor cung cấp sẽ làm Input Contract cho khối Logic mà bạn Minh và bạn Khang biên soạn, giúp đồng đội nhận được input đã qua xử lý sàng lọc cơ bản.

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**
Trong module `graph.py` có hàm Routing: `if any(kw in task for kw in policy_keywords) -> route = "policy_tool_worker"`.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Dùng Rule-base Keyword thay vì LLM Zero-Shot Classifier ở Supervisor.

**Lý do:**
Việc gọi thêm một lượt Prompt tới LLM chỉ để phân loại câu hỏi (Ví dụ: Đây là câu hỏi về Chính sách hay Lịch làm việc?) là tiêu tốn Token và lãng phí thời gian không đáng có. 

**Trade-off đã chấp nhận:**
Đánh đổi lại, hệ thống sẽ gặp rủi ro "rơi vào Default Route (Retrieval)" nếu người dùng gõ sai Keyword hoặc Keyword quá mới chưa được map sẵn trong Source Code.

**Bằng chứng từ trace/code:**
```python
    task = state["task"].lower()
    route = "retrieval_worker"         
    route_reason = "default route"    

    policy_keywords = ["hoàn tiền", "refund", "flash sale", "license", "cấp quyền", "access", "level 3"]
    retrieval_keywords = ["p1", "sla", "ticket", "escalation", "sự cố"]

    if any(kw in task for kw in policy_keywords):
        route = "policy_tool_worker"
        route_reason = "task contains policy/access keyword"
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** Tác vụ rơi vào "Abstain Loop" (Vòng lặp không xác định).

**Symptom (pipeline làm gì sai?):**
Lúc đầu chạy Script kiểm thử, có câu hỏi chèn mã lỗi ngoại lệ kiểu "ERR-2038". Hệ thống cố nhồi vào Retrieval nhưng file Vector Document nào cũng chỉ match có 0.001 Cosine Score. Agent cuối cùng sinh ảo giác "Có lẽ mã lỗi này liên đới đến P1".

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**
Lỗi nằm ở Supervisor chưa có điểm rào trước những keyword nguy hiểm.

**Cách sửa:**
Tôi đã cắm Cờ "risk_high" chặn ngay tại `graph.py`.

**Bằng chứng trước/sau:**
Trước khi sửa: Output `route=retrieval_worker, Final Answer: P1 SLA là 15 phút (Abstain)`.
Sau khi sửa: Output Trace ngắt mạch:
`[08/15] q08: Ticket ghi ERR-809, không có thêm content gì...` -> `route_reason: unknown error code → human review` -> Kích hoạt HITL.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Ở việc tổ chức mã nguồn (Clean Code) và đưa ra quyết định Trade-off rõ ràng giúp tối ưu Latency cho hệ thống.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Chưa thành thạo việc nhúng FastAPI nên phải để bạn Tuấn Khang làm.

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_
Nếu `graph.py` của tôi bị lỗi Syntax, sẽ không có dữ liệu nào chảy được sang `workers`. Đó là Node thượng nguồn gốc rễ cực kỳ quan trọng.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_
Tôi cần bạn Minh cung cấp kết quả I/O output của Component Retrieval để hoàn thiện Type Annotation trong code tôi gọi wrapper.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Tôi sẽ thử Semantic Routing nội bộ ở Supervisor thay vì rule-based if-else, vì trace của các câu test mập mờ có xu hướng fallback sang mặc định `retrieval_worker`. Việc dùng Cosine Similarity nhẹ có thể giúp routing chính xác hơn mà không ngốn LLM Call.
