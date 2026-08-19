---
name: azure-networking
description: Azure networking design and review guidance. Use when assessing Azure VNets, peering, routing, firewalls, private connectivity, hybrid connectivity, or DNS.
---

# Azure Networking Review Guidance

## Addressing

- Check for overlapping address spaces.
- Confirm subnet sizing allows for expected growth.
- Identify address ranges that could create hybrid connectivity conflicts.

## Peering and topology

- Confirm required VNet peering exists in both directions.
- Review forwarded traffic and gateway transit requirements when relevant.
- Identify missing connectivity between hub and workload networks.

## Routing

- Review User Defined Routes and route propagation.
- Identify asymmetric routing risks.
- Confirm the intended path for inbound and outbound traffic.
- If centralized inspection is required, verify routes actually direct traffic to the intended security appliance.

## Private connectivity

- Evaluate whether Azure PaaS services require Private Endpoints.
- When Private Endpoints are used, review the related DNS requirements.
- Confirm public network access aligns with the intended security model.

## DNS

- Identify the authoritative DNS and forwarding path.
- Review Private DNS zone creation and Virtual Network links.
- Review Private DNS zone groups associated with Private Endpoints.
- Consider hybrid name-resolution requirements.

## Security

- Review NSG scope and overly broad rules.
- Identify direct Internet exposure that conflicts with architecture requirements.
- Review centralized firewall placement and intended traffic paths.
- Prefer least-privilege network access.

## Output

For each finding provide:

1. Severity
2. Finding
3. Evidence
4. Risk
5. Recommendation
6. Assumptions or dependencies
