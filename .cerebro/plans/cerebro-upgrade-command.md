# /cerebro-upgrade — Versioned Template Sync

**Objective:** Add a `/cerebro-upgrade` slash command that syncs template-owned files from the upstream `claude-xmen` repo (https://github.com/yelaco/claude-xmen.git) into a derived project at a user-chosen tagged release, with explicit conflict resolution for user-modified files and a recorded baseline so future upgrades can do accurate change detection.
**Risk Level:** MEDIUM

## Assumptions and Decisions

- Upstream remote is `https://github.com/yelaco/claude-xmen.git`; releases are git tags (e.g. `v0.3.0`). The command MUST take an explicit target ref (tag or commit SHA) and refuse to operate on `HEAD`/`main` to keep upgrades reproducible.
- Fetch strategy uses **git** as the primary mechanism (`git clone --filter=blob:none --depth=1 --branch <ref>` into a tmp dir under `.cerebro/upgrade-cache/<ref>/`). `gh` and the raw GitHub API are NOT required and are not relied on. If `git` is unavailable, the command fails fast with a clear remediation message. This avoids API rate limits, auth requirements, and partial-file fetch fragility.
- File ownership is declared in `.cerebro/upgrade-manifest.json` that ships with the template. Each entry has `path` (glob or exact), `ownership` (`template` | `user` | `merge`), and optional `notes`. The manifest is itself template-owned, but **the local copy's ownership overrides win** during upgrade — Cerebro reads the local manifest, not the upstream one, for ownership decisions on this run, then offers to update the manifest itself as a separately-gated step (Gate B).
- Ownership defaults (initial manifest content):
  - `template` (overwrite, no prompt): `.claude/agents/*.md`, `.claude/commands/cerebro-*.md`, `.claude/commands/to-me-my-x-men.md`, `.claude/hooks/*.sh`, `.cerebro/schemas/*.json`, `.cerebro/templates/*.md`, `.cerebro/templates/*.json`, `.cerebro/docs/skill-policy.md`, the `cerebro-upgrade` command file itself.
  - `merge` (unified diff shown, Gate A fires on conflict): `CLAUDE.md`, `README.md`, `.claude/settings.json`, `.cerebro/docs/*.md` other than `skill-policy.md`.
  - `user` (never touched, never listed in change report): `.cerebro/plans/**`, `.cerebro/notepads/**`, `.cerebro/boulder.json`, `.cerebro/.pending-todos`, `.cerebro/team-runs/**`, `.cerebro/project-context.md`, and anything not listed in the manifest.
- The `user_owned_patterns` in the manifest are the authoritative source at runtime. No hardcoded fallback list exists in the command file — if the manifest is absent the command aborts (first-run bootstrap must be run first).
- Baseline tracking: after each successful upgrade, Cerebro writes `.cerebro/upgrade-state.json` with `applied_ref`, `applied_sha`, `applied_at`, and a SHA-256 hash map of every template-owned and merge-owned file at the moment of application. This baseline drives change detection on the next run.
- First-run behavior: if `.cerebro/upgrade-state.json` is absent, every file is treated as a two-way diff against upstream. `template`-owned files are overwritten without prompt (unless `--strict`). `merge`-owned files that differ locally trigger Gate A.
- CLI flags: `/cerebro-upgrade <ref> [--dry-run] [--strict] [--only <glob>]`
  - `--dry-run`: produce the change report without writing anything.
  - `--strict`: even `template`-owned files prompt before overwrite if their local content differs from the recorded baseline.
  - `--only <glob>`: restrict the upgrade to files matching the glob.
- v1 deferrals: automated rollback after partial success (covered by git working tree), upgrading from a fork with a different remote, non-git fetch strategies, and split-file CLAUDE.md support. These are safe to defer because Gate D enforces a clean working tree before any write.
- Symlinks and executable bits: v1 does not preserve or restore symlinks or file mode bits (e.g. `+x` on hooks). The command writes file content only. If upstream changes a hook's executable bit, the user must `chmod +x` manually. This is noted in the change report for affected hooks.
- Deliberately deleted template-owned files: if a file appears in the manifest as `template` or `merge` but does not exist locally, it is classified as `add` and the upgrade recreates it. This is intentional — deliberate local deletions should be reflected by changing the entry to `user` in the local manifest before running the upgrade.
- Absent manifest on first run: the command bootstraps a default manifest from the default ownership list and prompts the user to confirm before proceeding. This is the only path where the command may run without a pre-existing manifest.

## Approval Gates

- [ ] **Gate A — Merge-owned file conflict.** Fires when a `merge`-owned file has diverged on both sides since the recorded baseline (or differs locally on first run). Cerebro presents a unified diff and asks the user to choose: `keep local`, `take upstream`, `merge manually` (writes both versions and a `.rej`-style conflict marker), or `skip`. Required before any merge-owned file is modified.
- [ ] **Gate B — Manifest update.** After file sync completes, if the upstream manifest at the target ref differs from the local manifest, Cerebro asks: adopt upstream manifest (full replace), merge ownership entries (union), or leave local untouched. Required because manifest changes alter future upgrade behavior.
- [ ] **Gate C — Strict-mode template overwrite.** When `--strict` is set and a template-owned file has drifted from baseline, Cerebro pauses and asks before overwriting. Without `--strict`, no gate fires for template files.
- [ ] **Gate D — Dirty working tree.** Before any write, Cerebro runs `git status --porcelain` in the target repo. If there are uncommitted changes that intersect template-owned or merge-owned paths, Cerebro pauses and asks the user to commit/stash or pass `--force-dirty`. This keeps rollback simple (`git restore .`).

## Acceptance Criteria

- [ ] `/cerebro-upgrade <ref>` fetches the upstream repo at `<ref>` into `.cerebro/upgrade-cache/<ref>/` using shallow `git clone`, validates the ref exists, and resolves it to a commit SHA stored in the change report.
- [ ] Running `/cerebro-upgrade <ref> --dry-run` against a checkout that already matches the upstream ref produces a zero-change report and exits without writing any files (verified by `git status --porcelain` remaining empty).
- [ ] Running `/cerebro-upgrade <ref>` where a template-owned file has been locally modified and `--strict` is NOT set overwrites that file without prompting and records the overwrite in the change report.
- [ ] Running `/cerebro-upgrade <ref>` where `CLAUDE.md` has local changes and upstream also has changes triggers Gate A with a unified diff; all four resolution choices produce the documented file state and the change report reflects each choice.
- [ ] User-owned paths (`.cerebro/plans/**`, `.cerebro/notepads/**`, `.cerebro/boulder.json`, `.cerebro/.pending-todos`, `.cerebro/team-runs/**`, `.cerebro/project-context.md`) are never written — verified by inspecting the change report and by `git status` showing none touched.
- [ ] After a successful non-dry-run, `.cerebro/upgrade-state.json` exists, parses as valid JSON, and contains `applied_ref`, `applied_sha`, `applied_at`, and a `hashes` map covering every template-owned and merge-owned file present in the local tree.
- [ ] Running `/cerebro-upgrade <ref>` immediately after a successful upgrade to the same `<ref>` is a no-op: zero-change report, no prompts fire, `upgrade-state.json` is rewritten with a new `applied_at`.
- [ ] A locally absent owned file (upstream-only) is classified as `add` in the change report and written without error — not an error exit.
- [ ] `.cerebro/upgrade-cache/` is listed in `.gitignore` (verified by `grep 'upgrade-cache' .gitignore`).
- [ ] `/cerebro-doctor` (with its new section 14) passes completely after all tasks land, including the check that `upgrade-manifest.json` parses and conforms to its schema.
- [ ] Running `/cerebro-doctor` section 14 with `.cerebro/upgrade-manifest.json` temporarily removed reports "no manifest present" and exits zero (informational, not a blocking failure — the manifest is a new artifact not all existing projects will have).
- [ ] The new slash command appears in `.claude/commands/` and `/cerebro-doctor`'s required-commands list is updated to include `cerebro-upgrade.md`.

## Tasks

### Task 1: Design and ship `.cerebro/upgrade-manifest.json` and its schema

**Owner:** Wolverine
**Files:** `.cerebro/upgrade-manifest.json` (create), `.cerebro/schemas/upgrade-manifest.schema.json` (create)
**What:** Author the initial manifest with the ownership defaults from Assumptions. Each entry: `{ "path": "<glob or exact>", "ownership": "template|user|merge", "notes": "<optional>" }`. Manifest top-level: `{ "version": 1, "entries": [...] }`. Author a JSON Schema (draft 2020-12) under `.cerebro/schemas/` mirroring `team-run.schema.json`'s style (`additionalProperties: false`, required fields, enums for ownership).
**TDD:** Not applicable: schema and manifest are data files validated entirely by the Verify command below.
**Verify:** `python3 -m json.tool .cerebro/upgrade-manifest.json > /dev/null && python3 -m json.tool .cerebro/schemas/upgrade-manifest.schema.json > /dev/null`
**Risk:** LOW
**Approval Gate:** None

### Task 2: Author `.claude/commands/cerebro-upgrade.md`

**Owner:** Wolverine
**Files:** `.claude/commands/cerebro-upgrade.md` (create), `.gitignore` (modify — append `.cerebro/upgrade-cache/`)
**What:** Write the slash command markdown following the structure of existing `cerebro-*.md` commands. The command body instructs Cerebro to:
  1. Parse args `<ref> [--dry-run] [--strict] [--only <glob>]`. Abort with a clear error if `<ref>` is empty, `HEAD`, `main`, or `master`.
  2. Abort with a clear error if `conflict_policy` in the local manifest is anything other than `skip_customized` or is missing — v1 implements only the ownership-type-based resolution; other policy values are not supported.
  3. Run Gate D (dirty working tree check).
  4. If `.cerebro/upgrade-manifest.json` is absent, run the bootstrap flow: generate default manifest from the canonical ownership list, present it to the user, and require confirmation before proceeding.
  5. `git clone --filter=blob:none --depth=1 --branch <ref> https://github.com/yelaco/claude-xmen.git .cerebro/upgrade-cache/<ref>/` (or pull + checkout if the cache dir already exists for this ref).
  6. Resolve `<ref>` to a full SHA via `git -C .cerebro/upgrade-cache/<ref> rev-parse HEAD`.
  7. Load the **local** `.cerebro/upgrade-manifest.json` for ownership decisions.
  8. Load `.cerebro/upgrade-state.json` if present; use its `hashes` map as the baseline. Use committed-content hashes (`git show HEAD:<path> | sha256sum`) not working-tree hashes to avoid capturing dirty state in the baseline.
  9. For each manifest entry, expand the glob in both the upstream cache and the local tree, then classify each file: `add` (upstream-only, including deliberately-deleted local files), `delete` (local-only, template-owned), `modify-template` (template-owned, content differs), `modify-merge-clean` (merge-owned, only upstream changed), `modify-merge-conflict` (merge-owned, both sides changed), `noop` (identical).
  10. Apply `template` writes silently (or trigger Gate C in `--strict` mode if local hash diverged from baseline). For each `add` file, write without prompt.
  11. For each `modify-merge-conflict`, fire Gate A with a unified diff (`diff -u`).
  12. In the summary table, for every file skipped due to `merge` ownership with only local changes (no upstream change), show a one-line diff hint: e.g. `skipped (local-only) — run diff <local_path> .cerebro/upgrade-cache/<ref>/<path> to review`.
  13. Emit the change report (printed to chat; also written to `.cerebro/upgrade-cache/<ref>/report.md`).
  14. After file sync, run Gate B if the local manifest differs from the upstream manifest.
  15. Write `.cerebro/upgrade-state.json` using a tempfile+rename for atomicity. In `--dry-run` mode, skip steps 10–14 writes and the state update.
  16. Append `.cerebro/upgrade-cache/` to `.gitignore` if not already present.
  The command must state explicitly that it does NOT create an agent team, does NOT touch `.cerebro/.pending-todos`, and does NOT spawn Wolverine or Storm. It is a Cerebro-led single-flow operation like `/cerebro-doctor`.
**TDD:** Not applicable: this is a command-spec markdown file. Behavioral verification happens in Tasks 4 and 5.
**Verify:** `test -f .claude/commands/cerebro-upgrade.md && rg -n 'upgrade-manifest|upgrade-state|Gate A|Gate B|Gate C|Gate D|--dry-run|--strict|--only' .claude/commands/cerebro-upgrade.md && grep 'upgrade-cache' .gitignore`
**Risk:** MEDIUM
**Approval Gate:** None

### Task 3: Define `.cerebro/schemas/upgrade-state.schema.json`

**Owner:** Wolverine
**Files:** `.cerebro/schemas/upgrade-state.schema.json` (create)
**What:** JSON Schema for `.cerebro/upgrade-state.json`. Required fields: `version` (const 1), `applied_ref` (string, minLength 1), `applied_sha` (string, pattern `^[0-9a-f]{40}$`), `applied_at` (ISO-8601 string), `hashes` (object mapping path strings to SHA-256 hex strings). `additionalProperties: false`.
**TDD:** Not applicable: schema is a data file validated by the Verify command.
**Verify:** `python3 -m json.tool .cerebro/schemas/upgrade-state.schema.json > /dev/null`
**Risk:** LOW
**Approval Gate:** None

### Task 4: End-to-end happy-path verification

**Owner:** Wolverine
**Files:** None (uses an isolated `/tmp` clone — does not modify the working repo)
**What:** Script the following sequence in a temp dir to verify Tasks 1–3 work together:
  1. `git clone <this repo> /tmp/upgrade-test && cd /tmp/upgrade-test`
  2. Simulate "project derived from template" state: ensure the new artifacts (command, manifest, schemas) are present.
  3. Run `/cerebro-upgrade <latest-tag> --dry-run` — expect a non-empty change report (or zero-change if identical) and no file writes (`git status --porcelain` unchanged after the run).
  4. Run `/cerebro-upgrade <latest-tag>` — expect template files updated or no-op, merge-owned files gate-firing only where both sides changed, and `.cerebro/upgrade-state.json` written.
  5. Re-run `/cerebro-upgrade <latest-tag>` — expect a zero-change report.
**TDD:** Not applicable: end-to-end behavioral verification.
**Verify:** `TASK_RESULT` envelope includes the change reports from steps 3, 4, 5. Steps 3 (if already up-to-date) and 5 must show no file writes; step 4 must show the expected writes.
**Risk:** MEDIUM
**Approval Gate:** None

### Task 5: Conflict-path verification

**Owner:** Wolverine
**Files:** None (isolated `/tmp` clone)
**What:** In the same temp dir from Task 4, before the upgrade run: (a) modify `CLAUDE.md` locally and confirm Gate A fires with a unified diff; test all four Gate A resolution choices in separate sub-runs (reset between each). (b) Modify `.claude/agents/wolverine.md` locally and confirm it is silently overwritten in default mode; re-test with `--strict` and confirm Gate C fires. (c) Delete `.claude/agents/beast.md` locally and confirm the upgrade classifies it as `add` and recreates it.
**TDD:** Not applicable: behavioral verification.
**Verify:** `TASK_RESULT` envelope lists each sub-scenario, the gate that fired (or didn't), and the resulting file state. All four Gate A branches, Gate C, and the `add` (absent-local-file) branch must be exercised.
**Risk:** MEDIUM
**Approval Gate:** None

### Task 6: Extend `/cerebro-doctor` to validate the new artifacts

**Owner:** Wolverine
**Files:** `.claude/commands/cerebro-doctor.md` (modify)
**What:** Add a new numbered section 14 ("Upgrade Manifest and State") with these checks:
  - `test -f .cerebro/upgrade-manifest.json`: if absent, print "no manifest present (informational)" and continue — exit zero, not a blocking failure.
  - If present: `python3 -m json.tool .cerebro/upgrade-manifest.json > /dev/null`
  - `test -f .cerebro/schemas/upgrade-manifest.schema.json && python3 -m json.tool .cerebro/schemas/upgrade-manifest.schema.json > /dev/null`
  - `test -f .cerebro/schemas/upgrade-state.schema.json && python3 -m json.tool .cerebro/schemas/upgrade-state.schema.json > /dev/null`
  - Inline Python validator confirming manifest entries have required keys and valid ownership enum (same pattern as section 3).
  - If `.cerebro/upgrade-state.json` exists, validate required fields against the schema.
  Also add `cerebro-upgrade.md` to the required-commands list in section 1.
**TDD:** Run `/cerebro-doctor` before this task lands and confirm section 14 does not exist. After the change, confirm it does.
**Verify:** `rg -n 'cerebro-upgrade.md' .claude/commands/cerebro-doctor.md && rg -n 'upgrade-manifest|upgrade-state' .claude/commands/cerebro-doctor.md`
**Risk:** LOW
**Approval Gate:** None

### Task 7: Update `CLAUDE.md` and docs

**Owner:** Wolverine
**Files:** `CLAUDE.md` (modify Commands section), `.cerebro/docs/cerebro-workflow.md` (modify or create upgrade section), `README.md` (modify command summary if it carries one)
**What:** Add `/cerebro-upgrade <ref> [--dry-run] [--strict] [--only <glob>]` to the Commands list in `CLAUDE.md`. Add an "Upgrading from upstream" section to `.cerebro/docs/cerebro-workflow.md` covering the flow, four gates, manifest/state files, and v1 known gaps (symlinks/mode bits, no auto-rollback). Update `README.md` if it carries a command summary table.
**TDD:** Not applicable: docs-only.
**Verify:** `rg -n 'cerebro-upgrade' CLAUDE.md README.md .cerebro/docs/`
**Risk:** LOW
**Approval Gate:** None

### Task 8: Final integration check

**Owner:** Wolverine (runs doctor and reports; no code changes)
**Files:** None
**What:** Run `/cerebro-doctor` end to end against the repo with all above changes applied. Confirm every numbered section passes, including section 14. Confirm `git status` is clean (apart from intentional new/modified files from this plan) and that no user-owned paths were touched.
**TDD:** Not applicable.
**Verify:** Doctor output captured in `TASK_RESULT` envelope. Every section labelled PASS.
**Risk:** LOW
**Approval Gate:** None

## Rollback / Recovery

- Gate D forces a clean working tree before any write, so rollback after a failed or undesired upgrade is: `git restore .` to undo all file writes, plus `rm -rf .cerebro/upgrade-cache/<ref>/` to drop the cache dir. If `--force-dirty` was passed, the user acknowledged mixed local + upstream content and rollback is their responsibility (Cerebro warns at Gate D).
- `.cerebro/upgrade-state.json` is written atomically via tempfile+rename. A crash mid-write leaves the previous state intact.
- If `.cerebro/upgrade-cache/` grows too large, deleting it entirely is safe; the next upgrade re-clones.
- The cache directory must be in `.gitignore` — Task 2 adds it and Task 2's verify command confirms it.
- If the upstream manifest at a future ref renames or removes a path the user has customized, the `user` ownership default (anything not in the manifest is user-owned) protects unlisted files. Risk is concentrated in `merge`-owned files — Gate A's "merge manually" option leaves `.rej`-style markers for post-upgrade audit.
