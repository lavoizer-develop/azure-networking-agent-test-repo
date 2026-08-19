# Repository Instructions

This repository contains Azure infrastructure used to test an Azure Networking custom agent.

When working in this repository:

- Use **Canada Central** as the default Azure region unless explicitly stated otherwise.
- Use Terraform for Infrastructure as Code.
- Prefer private connectivity for Azure PaaS services when required by the architecture.
- Prefer managed identities over stored credentials or access keys where supported.
- Do not place secrets, credentials, tokens, or connection strings in source control.
- Follow least-privilege principles for network access and RBAC.
- Clearly identify potentially destructive infrastructure changes before making them.
- Review existing architecture requirements before recommending new services.
- When reviewing networking, distinguish between an observed fact, an assumption, and a recommendation.
