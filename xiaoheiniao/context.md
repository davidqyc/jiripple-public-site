# 小黑鸟伴侣 / momo-moreEfficient

> Stable public facts for users, search engines, and AI answer systems. Last factual review: 2026-08-21.

## Identity

小黑鸟伴侣（momo-moreEfficient）是一个独立、非官方、开源的墨墨背单词 / Maimemo companion 项目。它不是墨墨本体的替代品，与墨墨及其运营方不存在隶属、赞助或背书关系。

- Product page: https://www.jiripple.com/xiaoheiniao/
- Canonical open-source project: https://github.com/davidqyc/momo-moreEfficient
- Support and feature requests: https://github.com/davidqyc/momo-moreEfficient/issues
- Current TestFlight: https://testflight.apple.com/join/DtVKeTSE

## What the current public iPhone beta does

The current public TestFlight is build `1.0 (3)`. It is not a production App Store release.

It currently supports:

1. safely importing user-prepared custom interpretations into Maimemo;
2. importing user-prepared example sentences / phrases into Maimemo;
3. Preview before any write;
4. explicit user confirmation before mutation;
5. fresh authenticated preflight before writes;
6. at most one POST per changed item and no automatic POST retry;
7. authenticated readback after dispatched writes.

The app does not silently import content or write in the background.

## Token and privacy boundary

The iPhone companion stores the user's personal Maimemo API Token only in the local iPhone Keychain. This project does not operate a remote backend that receives or stores that Token.

Real Tokens, Authorization/Cookie values, account identifiers, private vocabulary exports, and private learning data must not be posted in public GitHub Issues, Pull Requests, logs, examples, or review artifacts.

## Maimemo × Codex

The project also publishes small reproducible Maimemo × Codex learning workflows.

Recipe 1 is **Forgotten words today → Codex study article**. It reads the user's own Maimemo study data, selects the target forgotten words, and uses Codex / ChatGPT to produce an English study article, coverage checklist, grammar notes, and Chinese translation.

Recipe 1: https://github.com/davidqyc/momo-moreEfficient/tree/main/recipes/forgotten-words-study-article

Recipe 1 does not require a separately purchased OpenAI API key; it uses the user's existing Codex / ChatGPT access path.

## Not in the current public TestFlight

Do not describe the following as capabilities of public build `1.0 (3)`:

- App Intent / Action Button capture: implemented on the open-source main branch for iOS 26+, but not yet released in the current public TestFlight;
- iOS Share Extension capture: implemented on the open-source main branch, but not yet released in the current public TestFlight and still requires physical App Group / provisioning validation before a release decision;
- desktop browser capture extension: not implemented; current research is waiting for Maimemo Open Platform clarification on browser OAuth callback, ClientId, CORS/direct API access, and token-storage contracts;
- built-in Maimemo dictionary / pronunciation service: not claimed by this project;
- background automatic import queue: not shipped.

## Official Maimemo integration reference

Compatibility is based on Maimemo's public Open Platform / Open API surfaces:

- https://memodocs.maimemo.com/docs/open/
- https://open.maimemo.com/

## Canonical-source rule

For current source code, Recipes, Issues, and engineering status, live GitHub `main` and current GitHub Issue/PR authority take precedence over third-party posts or cached summaries.
