# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 · Scaling |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Kim, Liu và cộng sự (Google Research, Google DeepMind, MIT), *Towards a Science of Scaling Agent Systems*, arXiv 2512.08296 (https://arxiv.org/abs/2512.08296); blog Google Research 28/01/2026 (https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/). Loại bằng chứng: benchmark có kiểm soát. Thông tin ban đầu lấy từ tìm kiếm web (tóm tắt, blog) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Thêm agent thường chạm trần và có thể làm giảm kết quả. Lợi ích chủ yếu ở việc chia song song được. Ở các task suy luận tuần tự, mọi biến thể multi-agent đều làm giảm hiệu năng 39-70%. Task nhiều tool chịu overhead phối hợp nặng hơn (theo tóm tắt và blog) |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Thí nghiệm trên một tập benchmark và ba họ model thật, so 5 kiến trúc (single, independent, centralized, decentralized, hybrid). Số cấu hình khác nhau giữa các nguồn (180 ở blog và v1, 260 ở bản sau), nên số cụ thể cần kiểm trên arXiv. Không áp dụng trực tiếp cho MockLLM tất định và 14 claim giả của lab |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Task claim chủ yếu tuần tự (đọc order, quote, ghi). Đổi workflow sang orchestrator (thêm investigator) sẽ không tăng pass rate (vẫn 1.000) và làm cost/success tăng khoảng 1.5-2 lần |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool đọc, seed 11,22,33,44,55, corpus public 14 claim, pricing.yaml, grader. Biến thay đổi duy nhất: shape (workflow so với orchestrator) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: investigator làm lộ field qua handoff. Đo bằng pass rate, pass^5, variance, cost/success và số CANARY_SECRET trong trace |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json` (by_shape.workflow, by_shape.orchestrator), commit 68d2410
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng. Pass rate cả hai đều 1.000, pass^5 1.000, variance 0. Cost/success workflow 28.78 so với orchestrator 57.50 (gấp 2.0 lần). Chỉ kết luận trong phạm vi bộ public.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
