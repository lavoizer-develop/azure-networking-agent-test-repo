# Repository Copilot Instructions

## Purpose

This repository demonstrates a security-focused Azure Networking Assessment Agent for Azure Landing Zone and Zero Trust network reviews.

## Repository Structure

- `.github/agents/` — custom Copilot agents
- `.github/skills/` — reusable specialist skills
- `.github/prompts/` — reusable task prompts
- `docs/network-requirements.md` — authoritative network-security target state
- `docs/platform-context.md` — optional shared-platform context
- `docs/assessments/` — generated assessment artifacts
- `infra/` — workload Infrastructure as Code
- `scripts/` — deterministic repository tooling

## Architecture and Security

- Treat `docs/network-requirements.md` as the authoritative target state.
- Follow Zero Trust principles:
  - verify explicitly
  - use least privilege
  - assume breach
- Consume centrally managed platform services rather than recreating them.
- Do not invent missing regions, CIDRs, firewall addresses, DNS addresses, resource IDs, or platform topology.
- When required evidence is unavailable, use `Unable to Validate`, `Required Confirmation`, or `External Dependency` as appropriate.
- Do not assume a fixed Azure region. Use the region defined by the workload or environment.

## Infrastructure as Code

- Terraform is the default IaC format in this repository unless another format is explicitly present.
- Infrastructure as Code is the primary evidence of workload implementation intent.
- Do not modify IaC during an assessment unless the user explicitly requests remediation.
- Prefer managed identities, least privilege, and private connectivity where required by policy or workload architecture.

## Assessment Efficiency

Minimize unnecessary context and repeated work.

- Search before reading entire files.
- Read only files relevant to applicable network requirements.
- Do not inspect unrelated application code.
- Do not repeatedly reopen files after sufficient evidence has been collected.
- Deduplicate findings by root cause.
- Do not use previous generated assessments as evidence.
- Do not read generated Markdown or HTML reports during technical analysis.
- Do not inspect `.git/`, `.terraform/`, `node_modules/`, state files, plan files, binary files, or archived assessments unless explicitly required.

## Assessment Output

The structured source of truth is:

`docs/assessments/network-assessment.json`

The agent must generate this JSON only after technical findings are finalized.

Then use:

`python3 scripts/render-assessment.py docs/assessments/network-assessment.json`

or, if required:

`python scripts/render-assessment.py docs/assessments/network-assessment.json`

to generate:

- `docs/assessments/network-recommendations.md`
- `docs/assessments/network-recommendations.html`

Do not independently author the Markdown and HTML versions.

Do not manually edit rendered reports. Fix the source JSON and rerun the renderer.

## Modification Boundaries

During a normal assessment, only these files may be created or updated:

- `docs/assessments/network-assessment.json`
- `docs/assessments/network-recommendations.md`
- `docs/assessments/network-recommendations.html`

Do not modify:

- workload infrastructure
- platform infrastructure
- requirements documents
- architecture documents
- deployment pipelines
- application code

unless explicitly asked by the user.
