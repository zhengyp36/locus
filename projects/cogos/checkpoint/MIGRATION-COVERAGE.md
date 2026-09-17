# MIGRATION-COVERAGE｜实测（2026-09-17）

源 `/home/zhengyp/work/A/checkpoint` 共 5143 文件。实测核对：

| 源 | 源文件数 | 迁入 | 排除 | 实测 |
|---|---|---|---|---|
| `probe-e0/` | 522 | 522（tar） | 0 | tar 内 522 ✓ |
| `probe-tendency/` | 1572 | 1572（tar） | 0 | tar 内 1572 ✓ |
| `probe-compress/` | 2976 | 2976（tar） | 0 | tar 内 2976 ✓ |
| `s4-target/` | 19 | 10（直拷） | 9（`__pycache__`4 ＋ `.pytest_cache/`5） | 10 ✓ |
| `dogfood/` | 6 | 6 | 0 | 6 ✓ |
| `dogfood-timer/` | 3 | 3 | 0 | 3 ✓ |
| 散装 `.md` | 45 | 45（43→cogos，2→kilo） | 0 | 43＋2 ✓ |
| **合计** | **5143** | **5134** | **9** | **5143 ✓** |

- 排除项仅为缓存（pyc / pytest_cache），非内容。
- probe 目录的 tar 为**整目录证据**，其中含各目录的 .md（与根下副本重复，属有意冗余，保证证据完整）。
- 迁入位置：`locus/projects/cogos/checkpoint/26-09-17-agent-theory/`、`locus/projects/kilo-resident/checkpoint/26-09-17-phone-number-contacts/`。
- 源目录**尚未删除**，待整体文档完成、两库 commit 后再清（Phase 4）。
