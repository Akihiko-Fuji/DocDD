# 変更管理 / Change Management

- 文書ID: DOC-MGT-053
- 最終更新日: 2026-03-23

## 1. 方針
仕様変更時は要求、仕様、設計、テスト、記録の順に影響確認を行う。

## 2. 変更手順
1. 変更要求の起点文書を特定する
2. コア10文書への影響有無を確認する
3. 必要なら ADR / Decision Log を更新する
4. 仕様・設計・テスト・traceability を同期更新する
5. Change Log / Review Log へ結果を残す

## 3. 変更分類
- Intent / Scope 変更
- Requirement 変更
- External Spec 変更
- Internal Design 変更
- Test / Record 更新のみ

## 4. 受入観点
- code first ではなく document first の手順になっていること
- Spec-Driven / Acceptance-Driven / Diagram-Driven の 3 観点で影響確認できること
- 変更理由が記録文書へ残ること
