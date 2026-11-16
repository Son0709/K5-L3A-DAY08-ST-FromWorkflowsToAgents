# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 68d2410
- Run id dẫn chứng: R-workflow-C-002-s55 (T02 seed 55, swarm fail còn workflow denied đúng); benchmark workflow 70/70 trial
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000 (src/reports/benchmark.json, 14 claim x 5 seed)
- Cost per success (mô phỏng, VND): 28.78 (single 38.99, orchestrator 57.50, swarm 49.57)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public (quét 880 file trace không có CANARY_SECRET, parent_secret, raw_headers). Tự kiểm `student_drop/` (src/reports/hidden_selfcheck.json): workflow chạy hết 40 claim x 5 seed không lỗi, 0 trial nghi lộ secret; không có nhãn nên chưa có pass rate hidden
Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Cả ba shape tự viết (workflow, single, orchestrator) đạt pass 1.000 và pass^5 1.000, variance 0 trên cùng 14 claim public x 5 seed (11,22,33,44,55), cùng bảng giá mô phỏng. Swarm đạt 0.986 / pass^5 0.929 vì fail T02 ở seed 55 (tin số ngày trong ticket). Khi chất lượng ngang nhau thì chọn shape ít tự chủ nhất và rẻ nhất: workflow có cost/success 28.78, bằng khoảng một nửa orchestrator (57.50) và 74% single (38.99), với 3.43 bước trung bình. Tiền, approval và idempotency đều do code quyết, nên model không có việc gì để tự chủ trong task này.

## Có đáng đổi lấy multi-agent không

Giữ workflow. Trên bộ public multi-agent không cho pass cao hơn mà chỉ tốn gấp đôi. Quyết định sẽ đảo lại nếu bộ hidden cho thấy workflow pass dưới 0.75 ở một loại claim mà cần suy luận trên văn bản tự do (ví dụ ticket mơ hồ về order hoặc policy), và một shape có agent sửa được điều đó với pass tăng rõ rệt trên cùng 40 claim x 5 seed. Khi đó mới đáng trả thêm cost. Hiện chưa có bằng chứng như vậy.

## Trace và bằng chứng

Trace của workflow ghi: `lookup_order` (chỉ order view đã qua allowlist `ORDER_FIELDS`), `quote`, `issue_refund` (ok, reason, conflict), `decision`, và `crash` khi có crash. Cố ý không ghi: nguyên claim row (có `parent_secret`, `raw_headers`), nguyên order row (SĐT, địa chỉ, ghi chú nội bộ, tên hàng) và nội dung `ticket`, vì ticket là dữ liệu người dùng và có thể mang secret. Shape đọc claim qua `get_claim_view` và chỉ dùng `order_id`, `principal_id`. Trace chỉ nằm ở `traces/<run_id>.json`, nơi grader quét. Kiểm bằng cách grep 880 file trace và test `test_workflow_trace_has_no_secret_or_pii`.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.

Bộ public chỉ có 14 claim và MockLLM tất định, nên pass 1.000 ở đây không chứng minh được pass rate hidden. Kết luận chỉ đúng với bộ public. Cost là cost mô phỏng. Bộ `student_drop/` không có nhãn nên chưa có pass rate hidden.
