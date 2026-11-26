# AI engineering instructions

Applies to all coding agents (ChatGPT, Codex, Claude and others). Owner-approved operating policy, 2026-11-26.

## Roles and authorization
- The owner is the Product Owner: business rules, priorities, acceptance criteria, UAT and release approval. Agents own technical analysis, implementation, Git, tests, build preparation, troubleshooting and reporting within the granted permissions.
- Use the existing project documentation and inspect the current branch, release target and actual workflows before acting. Preserve established business rules, environment separation, signing identities, versioning and deployment controls. Do not invent business rules or silently weaken tests.
- Routine authorized engineering changes do not require repeated approvals. Obtain explicit approval for production deployment, destructive changes, repository visibility changes, credential changes, spending beyond the approved budget or other material risks. Never deploy or release when the owner requests development only.

## GitHub Actions cost and release discipline
- Use existing GitHub-hosted runners; self-hosted runners are not part of the approved approach. Standard hosted runner compute for public repositories is generally free; private usage, larger runners, storage and other services may still be billed.
- Keep normally private repositories private during development. Bundle requested changes into one iteration; avoid redundant CI, automatic builds and unnecessary rebuilds. Inspect triggers and billing constraints before pushing. Use local/static checks where available, and use [skip ci] for documentation-only commits when appropriate (not to bypass required release checks).
- Prepare code, review, tests and exact release target first. If a paid private build would exceed the allowance or the owner wants to avoid compute charges, stop before triggering it and ask the owner to temporarily change the relevant repository to public. State the exact repository, branch, workflow, intended artifact and scope. The owner performs the visibility change; agents must never change visibility themselves.
- The owner accepts the residual disclosure risk of temporary public visibility, not an exemption from security review. Before exposure, assess source and history for credentials, signing material, customer data, sensitive documents, existing logs/artifacts, workflow permissions and secrets. Clearly report any incomplete checks or blockers; do not recommend public exposure if known sensitive material is present. Never print secrets or commit them. Rotate confirmed exposed credentials through the approved procedure.
- While public, use trusted refs/workflows only; do not run untrusted external contributions with privileged credentials. Do not expose private data, privileged logs, sensitive artifacts or unauthorized production releases. Public forks/downloads may persist after privatization. Do not assume public visibility is equivalent to an open-source license.
- Verify the owner has changed visibility before starting the agreed build, and confirm all relevant jobs have reached a terminal state and required artifacts/releases are actually available (or report failures accurately). Prefer targeted retries of failed jobs rather than rebuilding successful jobs. Tell the owner promptly when it is safe to return the repository to its normal visibility; the owner changes it back. Verify visibility if accessible. Do not claim a build or release succeeded without evidence.
- Report commit/ref, workflow/run, artifact/version, tests, remaining issues, costs or unverified items, and whether owner action is needed. Do not conflate an APK/AAB artifact with store publication or device UAT. No background-work promises.

## OneSpace website
- Normal visibility: public because GitHub Pages hosts onespace.live. Do not change visibility or hosting without explicit approval and a validated continuity plan. The temporary-public procedure does not apply while this repository is intentionally public.
- Keep published content safe for public disclosure; do not add confidential engineering notes, internal operational/security reports, private customer records or credentials. Any relocation of backend-only source or documents is a separate authorized task.
- Follow README generation, localization and route rules; regenerate and validate all five languages, preserve links/SEO and the tagline Two of Us. One Space. No production backend changes or deployment outside authorized scope.

## Project book and development process (owner decision, 26 Nov 2026)
- The single project document is `docs/PROJECT_BOOK.md` in the private repository `BoyofKay/OneSpace` (attach that repository if you work elsewhere). Read its sections 0-5 before acting.
- Follow its SDLC (section 2): work on one branch `iteration/YYYY-MM-DD-topic` created from the latest `main`; merge it back into `main` when the iteration is done. Never branch from another working branch and never continue an old branch (section 7 lists them).
- Do not create new project documents. At the end of every iteration update the book: dated decisions (section 4), current state (section 5) and history (section 6). When a decision replaces an older one, mark the older one "OVERRIDDEN by Dnn (date)" and keep it; never delete a decision.
