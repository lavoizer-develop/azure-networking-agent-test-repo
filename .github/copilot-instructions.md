# Repository Instructions

This repository contains Azure infrastructure and documentation used for architecture and engineering assessment.

## Repository Structure

- Architecture, requirements, and design documentation should be stored under `docs/`.
- Infrastructure as Code is stored under `infra/`.
- Generated assessment reports should be stored under `docs/assessments/`.
- Reusable Copilot agents are stored under `.github/agents/`.
- Reusable Copilot skills are stored under `.github/skills/`.
- Reusable prompt files are stored under `.github/prompts/`.

## Azure Conventions

- Use Canada Central as the default Azure region unless another region is explicitly required.
- Use Terraform for Infrastructure as Code unless the repository explicitly defines another standard.
- Prefer managed identities over stored credentials or access keys where supported.
- Do not place secrets, credentials, tokens, or connection strings in source control.
- Follow least-privilege principles for RBAC and network access.
- Prefer private connectivity when required by the documented architecture or security requirements.

## Assessment Guidance

When assessing the repository:

- Read documented requirements before recommending architectural changes.
- Validate documentation against the actual implementation.
- Distinguish confirmed facts from assumptions.
- Identify external/shared platform dependencies clearly.
- Do not invent resources, requirements, or architecture that are not supported by repository evidence.
- Preserve existing implementation unless the user explicitly asks for remediation changes.
