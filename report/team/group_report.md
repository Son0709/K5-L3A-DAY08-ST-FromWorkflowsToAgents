# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Làm cá nhân, một thành viên (Lê Hoàng Sơn)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 68d2410

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

Bài toán là xử lý claim hoàn phí của LogiX-VN sao cho tiền, approval và idempotency do code quyết, còn model chỉ soạn chữ. Mình làm một mình, theo thứ tự workflow, single, orchestrator, rồi chạy crash suite và benchmark, sau đó chọn shape bằng số đo.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

Cả ba shape đọc claim qua `get_claim_view`, kiểm `order_id` và `lookup_order`, tính quote bằng `compute_compensation` từ order row (bỏ qua số ngày trong ticket), rồi gọi `durability.issue_refund` với quote đầy đủ và `crash_at`. `InjectedCrash` không bị bắt: shape ghi trace rồi raise lại.

- **workflow**: các bước Python cố định, một lần MockLLM để soạn câu trả lời.
- **single**: vòng `run_react` tối đa 8 bước, `decide()` chỉ chọn tool đọc theo quy tắc cố định; sau vòng lặp code của shape gọi host.
- **orchestrator**: tạo handoff bằng `make_handoff` (facts rỗng, 4 tool đọc), chạy `run_readonly_investigators`, rồi orchestrator là bên duy nhất gọi host. Trace ghi handoff đã sanitize, không ghi parent context.

Trace chỉ ghi order view qua allowlist, quote, kết quả host và quyết định. Không ghi claim row, order row hay ticket.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

Nguồn: `src/reports/benchmark.json` (14 claim x 5 seed) và `src/reports/crash.json`.

| Shape | Pass | pass^5 | Seed min-max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 1.000-1.000 | 0.000000 | 28.78 | 3.43 / 4 |
| single | 1.000 | 1.000 | 1.000-1.000 | 0.000000 | 38.99 | 5.29 / 6 |
| orchestrator | 1.000 | 1.000 | 1.000-1.000 | 0.000000 | 57.50 | 4.36 / 5 |
| swarm | 0.986 | 0.929 | 0.929-1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Crash safety: 20/20. Swarm fail T02 ở seed 55. Chưa chạy `student_drop/`, nên chưa có số hidden.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

- Chạy `-k single` trong pytest khớp cả tên test `test_public_single_run_cases` của mọi shape, nên lần đầu thấy 60 failed. Xử lý: lọc kết quả fail theo shape; sau khi viết xong cả ba shape thì ma trận student ra 248 passed.
- Lệnh pip in `NativeCommandError` trên PowerShell chỉ vì thông báo nâng cấp pip, cài đặt vẫn thành công.

## 6. Tổng hợp đóng góp

Mình làm một mình nên toàn bộ đóng góp là của Lê Hoàng Sơn, ghi trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/2A202603662_LeHoangSon.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

Bộ public chỉ có 14 claim và MockLLM tất định, nên pass 1.000 không chứng minh được pass rate hidden. `decide()` của single là quy tắc cố định chứ không phải model thật. Kết luận có thể đổi nếu bộ hidden cho thấy workflow dưới 0.75 ở loại claim cần hiểu văn bản tự do.

## 8. Tài liệu tham khảo

- Tài liệu lab trong repo (README, docs/business_rules.md, docs/contracts.md).
- Google Research 2026, *Towards a Science of Scaling Agent Systems* (nêu trong research card; mình chưa đọc nguyên văn).
