# Báo cáo cá nhân — 2A202603662_LeHoangSon

## 1. Thông tin thành viên

- Họ tên: Lê Hoàng Sơn
- MSSV: 2A202603662
- Email:
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

Claude Code (Claude): đọc đề, gợi ý và viết code ba shape, chạy test và benchmark, điền báo cáo. Mình kiểm lại bằng cách chạy ma trận student, cổng host, crash suite, grep 280 file trace tìm secret và đối chiếu số trong ADR với `benchmark.json`.

## 6. Tự đánh giá

Code và số liệu đã kiểm bằng test. Phần chưa làm: chưa chạy bộ `student_drop/` nên chưa biết pass rate hidden; chưa đọc nguyên văn paper trong research card.
