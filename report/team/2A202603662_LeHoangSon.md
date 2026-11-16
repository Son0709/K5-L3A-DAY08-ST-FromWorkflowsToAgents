# Báo cáo cá nhân — 2A202603662_LeHoangSon

## 1. Thông tin thành viên

- Họ tên: Lê Hoàng Sơn
- MSSV: 2A202603662
- Email: leson07092004@gmail.com 
- GitHub: Son0709

## 2. Phần việc phụ trách

Shape, module hoặc phần báo cáo bạn phụ trách.

Làm một mình toàn bộ bài: ba shape (workflow, single, orchestrator), chạy crash suite và benchmark, chọn shape và viết báo cáo.

## 3. Đóng góp cụ thể

Commit chính (hash), test đã thêm hoặc sửa, quyết định kỹ thuật bạn đưa ra.

- Commit: ab4980b (workflow), bae4f5e (single), 9e07c98 (orchestrator).
- Test thêm: `src/tests/test_workflow_shape.py` (workflow bỏ qua số ngày trong ticket ở seed 55, trace không chứa secret, gọi lại vẫn một dòng ledger).
- Quyết định: truyền quote đầy đủ vào `issue_refund`; không đưa ticket vào trace hay prompt; chọn workflow vì cùng pass 1.000 mà cost/success thấp nhất (28.78).

## 4. Bằng chứng

Link commit, tên test, run id hoặc trích đoạn report liên quan.

- Ma trận student: 248 passed; cổng host: `python -m pytest -q` xanh.
- `src/reports/crash.json`: 20/20. `src/reports/benchmark.json`: xem ADR.
- Run id dẫn chứng: R-workflow-C-002-s55.

## 5. Công cụ AI đã dùng

Công cụ, dùng vào việc gì, và bạn đã tự kiểm tra kết quả thế nào (xem [RULES.md](../../RULES.md)).

Claude Code (Claude): đọc đề, gợi ý và viết code ba shape, chạy test và benchmark, điền báo cáo. Mình kiểm lại bằng cách chạy ma trận student, cổng host, crash suite, grep 880 file trace tìm secret và đối chiếu số trong ADR với `benchmark.json`.

## 6. Tự đánh giá

**Làm được:** cả ba shape qua đủ 62 test student của mỗi shape, cổng host xanh, crash suite 20/20. Trên bộ public cả ba shape đều đạt pass 1.000 và variance 0, trong khi swarm fail T02 ở seed 55. Mình chọn workflow vì khi chất lượng ngang nhau thì nó rẻ nhất (cost/success 28.78 so với 57.50 của orchestrator) và ít tự chủ nhất. Bộ tự kiểm `student_drop/` chạy hết 40 claim × 5 seed × 3 shape không lỗi và không trial nào nghi lộ secret.

**Hiểu chắc:** tiền, approval và idempotency do code quyết nên model không có chỗ để sai ở đó; phải truyền quote đầy đủ vào `issue_refund` vì host tự trừ phần đã hoàn theo đơn, tự trừ trước thì T14 bị trừ hai lần; trace là ranh giới bảo mật nên chỉ ghi dữ liệu đã qua allowlist, không ghi claim row, order row hay ticket.

**Còn yếu:** bộ public chỉ có 14 claim và MockLLM tất định, nên pass 1.000 chưa chứng minh được workflow đạt ≥ 0.75 trên bộ hidden có nhãn. Bộ `student_drop/` không có nhãn nên chỉ cho biết shape chạy được và không lộ secret, không cho pass rate. Mình chưa tự viết test cho single và orchestrator ngoài ma trận có sẵn, và `decide()` của single là quy tắc cố định chứ không phải model thật.

**Nếu làm lại:** mình sẽ viết test cho các nhánh hidden (approval của claim khác, đơn đã hoàn đủ, policy hết hiệu lực) cho cả ba shape ngay từ đầu, và đọc paper trước khi đặt hypothesis cho ablation.
