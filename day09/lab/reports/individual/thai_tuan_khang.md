# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Thái Tuấn Khang  
**Vai trò trong nhóm:** MCP Owner  
**Ngày nộp:** 2026-04-14  

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

Phần việc của tôi là làm chủ tương tác Tool Function Calling và External APIs thông qua Protocol "Model Context Protocol" (MCP). Tôi thiết kế module `mcp_server.py` và tích hợp module phân tích ở tệp `policy_tool.py` nhằm bắt các exception chuyên sâu. Tôi cũng đã cung cấp mô-đun HTTP FastAPI Web Endpoint để đáp ứng phần tính điểm Bonus cho bài Lab.

**Module/file tôi chịu trách nhiệm:**
- File chính: `mcp_server.py`, `workers/policy_tool.py`
- Functions tôi implement: `analyze_policy(task, chunks)`, `dispatch_tool(...)`

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Worker Synthesis cuối cùng của bạn Minh cần các Rules đặc biệt (Ví dụ "Digital Refund Exception") để Penalty hoặc Rewrite câu chốt. Dữ liệu này chỉ có thể bóc tách từ File Analyst mà tôi Setup ngầm từ Module OpenAI.

**Bằng chứng:**
Tôi trực tiếp Code Request FastApi tại `mcp_server.py` Endpoint `/tools/call`.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Sử dụng "JSON Object Mode" của Thư viện OpenAI API `response_format={"type": "json_object"}`.

**Lý do:**
Worker Policy Tool bắt buộc Output phải là dạng Dictionary Python chuẩn để truyền xuống biểu đồ trạng thái (AgentState). Nếu để GPT tự tạo String Text tự do, quá trình Parse (json.loads) sẽ dễ gặp rủi ro nếu model chèn thêm các chuỗi định dạng markdown.

**Trade-off đã chấp nhận:**
Vì JSON Object Mode luôn trả ra các Key chuẩn chỉnh nhưng đôi khi Output Text Explain của model có thể bị gãy gọn, ngắn gọn quá mức, không tự nhiên, làm giảm chất lượng nội dung Report, tuy nhiên máy lại hiểu được hệ thống System.

**Bằng chứng từ trace/code:**
```python
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
            ],
            temperature=0.1
        )
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** OpenAI Missing Authentication (API_KEY missing).

**Symptom (pipeline làm gì sai?):**
Lỗi xuất hiện trên màn Console `⚠️ OpenAI Policy Check failed: The api_key client option must be set`. Worker của tôi chạy xong nhưng trả về list Exception trống lốc, khiến AI hoàn luận sai luật đối với các trường hợp bị hạn chế.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**
Do Python bị lạc Context `os.environ`. File `.env` chứa Pass nằm tại thư mục CWD nhưng Script lại thực thi cách ra, không tự Load vào.

**Cách sửa:**
Inject thủ công module `load_dotenv()` vô đầu từng tệp worker độc lập.

**Bằng chứng trước/sau:**
Trước khi sửa:
`  policy_applies: True
  MCP calls: 0` (Trả về ngầm định do lỗi Exception Catch)
Sau khi khắc phục, Output Trace JSON Analysis bắt đầu hiện: `exceptions_found: [{"type": "activated_exception"}]`

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Triển khai API server độc lập (`mcp_server`) có thể gọi qua REST, mô phỏng khá gần với hệ thống thực tế và đáp ứng kỹ thuật của bài đánh giá nhóm.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Sử dụng Model OpenAI có xu hướng tiêu hao Token khá lớn. Đáng lý có thể sử dụng Prompt ngắn gọn và tối ưu hơn thay vì System Instruction hơi dài dòng.

**Nhóm phụ thuộc vào tôi ở đâu?** 
Nếu Policy Worker xử lý sai sót, hệ thống có thể đối mặt với rủi ro "Trả lời vi phạm chính sách nội bộ". Bước rào chắn này có vai trò rất quan trọng trong workflow.

**Phần tôi phụ thuộc vào thành viên khác:** 
Tôi cần Code Baseline Graph Orchestrator từ bạn Luân để Test cái Cổng kết nối Request Tools của tôi.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Tôi sẽ thử làm Token Authentication Bearer tích hợp vô Uvicorn Web Endpoint thay vì mở cửa `0.0.0.0` tuỳ tiện vì trace của câu chạy Production cho thấy nếu Deploy lên VPS, Endpoint /tools/call có rủi ro bị DDOS làm cháy túi Token của tài khoản OpenAPI.
