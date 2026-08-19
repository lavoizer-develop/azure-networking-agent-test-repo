---
agent: 'azure-networking'
description: 'Review the current Azure network architecture and identify risks and recommended improvements'
---

Review the Azure network architecture and Terraform configuration in this repository.

Read `docs/network-requirements.md` first and use it as the intended target state.

Focus on:

- network topology and segmentation
- VNet peering
- routing
- outbound traffic
- Network Security Groups
- Private Endpoints
- Private DNS
- public network exposure
- hybrid connectivity
- resiliency

Provide the result using:

## Current Architecture
Summarize what is implemented.

## Findings
For each issue provide severity, evidence, risk, and affected files/resources.

## Recommendations
Provide practical recommended changes in priority order.

## Assumptions
Identify anything that cannot be confirmed from the repository.

Do not change infrastructure as part of this review.
