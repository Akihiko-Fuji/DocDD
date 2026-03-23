# 完了の定義 / Definition of Done

- 文書ID: DOC-QA-045
- 最終更新日: 2026-03-23

## 1. 本書の目的

本書は、実装や文書作業が「完了した」と言える条件を、**Product / Document / Traceability** の 3 種に分けて定義する。

---

## 2. Product completion
- A-TYPE 主軸のプレイ開始からゲームオーバーまでが成立している
- 10×18 盤面、NEXT 1 個、Hold なし、Hard drop なしが挙動と UI に反映されている
- T-Spin 採用が実装・表示・得点へ反映されている
- 一時停止、再開、再試行、タイトル復帰の主要導線が成立している

---

## 3. Document completion
- コア 10 文書と主要な周辺仕様文書に重大な矛盾がない
- README、文書地図、基準差分文書により入口説明が成立している
- 要求・仕様・設計・試験・記録の各層に最低 1 つ以上の中核文書があり、フェーズ1相当の骨格が成立している
- 周辺文書には簡易版・予約事項中心のものが含まれていてもよいが、その成熟度が誤解されない表現になっている
- 変更理由が Decision Log / Change Log / Review Log に残っている
- 変更事例文書により波及例を示せる

---

## 4. Traceability completion
- `16_traceability_matrix.md` が最新状態である
- 代表機能について BR から TC まで追える
- 代表 TC が `34_module_design.md` の Internal Contract に接続されている
- 非採用機能も制約として追跡されている
- T-Spin 採用のような変更が上流から下流まで同期している

---

## 5. DoD 判定ルール
- Product completion, Document completion, Traceability completion の 3 区分すべてが満たされて初めて、その対象フェーズにおける完了とする
- 一部のみ満たす場合は「部分完了」とし、未達区分と未成熟文書を明示する
