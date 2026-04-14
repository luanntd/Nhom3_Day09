# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Phạm Văn Thành  
**Vai trò trong nhóm:** Trace & Docs Owner  
**Ngày nộp:** 2026-04-14  

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

Tôi phụ trách phần xử lý dấu vết (Traces) và phát triển kịch bản Đánh giá Báo Cáo trong `eval_trace.py`. Dựa vào logs lưu lượng, tôi thực hiện mã lệnh đo lường `avg_latency` và lập bảng so sánh (Comparison) giữa kết quả Day 08 và kiến trúc thực nghiệm mới Day 09. Đồng thời, tôi soạn thảo các Template Report tài liệu để đóng gói theo khuôn mẫu Markdown của Lab.

**Module/file tôi chịu trách nhiệm:**
- File chính: `eval_trace.py`, Các docs Markdown ở `docs/`
- Functions tôi implement: `analyze_traces`, `compare_single_vs_multi`, `save_eval_report`.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Luồng Script Grading `--grading` của tôi phụ thuộc vào quá trình thực thi từ 3 Agents đằng trước (do Luân, Minh, Khang triển khai) để có thể tạo Output jsonl tự động nộp bài.

**Bằng chứng:**
Đoạn Code Terminal xuất File `docs/system_architecture.md` cùng Log Output Metric Bảng `total_traces: 16`.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Viết báo cáo Bảng Metrics So sánh bằng giả định đối với các dữ dội bị Missing ở Data Day 08. 

**Lý do:**
File `day08` cũ chỉ chạy `eval.py` lưu Thang Điểm chất lượng, không thu thập các chỉ số kỹ thuật như Latency. Để report `single_vs_multi_comparison` hiển thị số liệu tương quan, tôi cần xử lý thay thế bằng ước tính thời gian thủ công.

**Trade-off đã chấp nhận:**
Gây ra tình trạng con số ở bảng Day 08 mang tính chất ước lượng "Rule of thumb" chứ không phải log system native.

**Bằng chứng từ trace/code:**
```markdown
| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) |
|--------|----------------------|---------------------|
| Avg latency (ms) | Thấp (~3.5s) | 14148ms |
| Routing visibility | ✗ Không có | ✓ Có route_reason |
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** Tụt hậu phiên bản Code Evaluation.

**Symptom (pipeline làm gì sai?):**
Khi chạy `eval_trace` để nộp 15 câu Test, hàm so sánh Baseline Day 08 vs Day 09 sinh cấu trúc Metric bị lệch so với Template JSON `artifacts/eval_report.json` và văng Exception KeyError ở khâu in.

**Root cause:**
Tôi đã quên bóc Object JSON `day08_baseline` thành biến Model cục bộ trước khi truyền vào Output.

**Cách sửa:**
Áp dụng cơ chế Python Try/Catch OS check.

**Bằng chứng trước/sau:**
Thêm module Catch File để check `results/scorecard_baseline.md`:
```python
    if day08_results_file and os.path.exists(day08_results_file):
        with open(day08_results_file) as f:
            day08_baseline = json.load(f)
```
Khối lệnh cẩn thận thêm điều kiện kiểm tra tồn tại này tránh tình trạng lỗi file script nếu môi trường thiếu data baseline thủ công cũ.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Trình bày nội dung kỹ thuật rõ ràng trong Báo Cáo Markdown. Lưu Log Traces đúng định dạng yêu cầu của kịch bản chấm điểm.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Quá trình làm Code Eval Trace của tôi khá chậm nên chiếm thời gian rà soát Output của Team. Tôi bị động vào hệ thống Output Schema của các bạn khác.

**Nhóm phụ thuộc vào tôi ở đâu?** 
Các tài liệu nộp tại thư mục `docs` đều do tôi phụ trách quản trị định dạng theo Template của Giảng viên. Bất cứ lỗi sai Header / Formatting nào cũng có thể khiến kịch bản Auto-grader gặp lỗi.

**Phần tôi phụ thuộc vào thành viên khác:** 
Tôi cần Luân (Orchestrator) truyền đủ List Arguments theo File Hợp Đồng `Worker_Contracts` thì File Logger Trace của tôi mới parse (bóc text) Json Log được.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Tôi sẽ thử Visualize Output JSON Trace thành biểu đồ Chart (Nhúng React Rechart / Plotly) để so sánh 4 thông số: `Faithfulness`, `Avg_latency`, `Confidence` và `Abstain_Rate` của File Trace cuối Report, khiến báo cáo trở nên đẹp và dễ đọc hơn thay vì in Print Text Terminal khô khan!
