# Azure Networking Agent Test Repository

This repository is a deliberately small Azure/Terraform scenario for testing a GitHub Copilot **Azure Networking Agent**.

The environment represents an application landing zone in **Canada Central** connected to a central hub. The Terraform is intentionally not aligned with every requirement in `docs/network-requirements.md`.

## What to do

Open this repository in VS Code and test the custom agent in three ways.

### Test 1 — Architecture review

Select the **Azure Networking** custom agent and ask:

> Review this repository against `docs/network-requirements.md`. Identify networking, security, routing, private connectivity, and DNS gaps. Do not change any files. Rank findings by severity and explain the recommended remediation.

### Test 2 — Terraform-focused review

Ask:

> Review the Terraform under `infra/`. Focus on VNet peering, NSGs, UDRs, Private Endpoints, Private DNS, Storage, and Key Vault. Identify anything that conflicts with the documented target requirements.

### Test 3 — Troubleshooting scenario

Ask:

> Assume the application can reach the Storage Account privately from Azure, but on-premises clients cannot resolve the Storage private endpoint name. Use the repository configuration to explain the likely DNS gap and recommend the required Azure-side changes.

## Repository structure

```text
.github/
├── agents/
│   └── azure-networking.agent.md
├── skills/
│   └── azure-networking/
│       └── SKILL.md
├── prompts/
│   └── review-network.prompt.md
└── copilot-instructions.md

docs/
├── current-architecture.md
└── network-requirements.md

infra/
├── versions.tf
├── variables.tf
├── main.tf
├── network.tf
├── routing.tf
├── security.tf
├── storage.tf
├── keyvault.tf
└── outputs.tf
```

## Important

This repository is a **learning/test scenario**. It is not intended to be deployed to a production subscription without review and remediation.
