# Azure Networking Assessment

> [!WARNING]
> **Overall Status: Action Required**
>
> 0 Critical · 5 High · 1 Medium · 0 Low

## Assessment Context

| Attribute | Value |
|---|---|
| Scope | Repository IaC assessment of infra/ |
| Environment | test |
| Region | Canada Central |
| Assessment Date | 2026-10-06 |
| Live Azure Validation | No |

## Executive Summary

The Terraform establishes separate application, management, and Private Endpoint subnets, but it does not conform to the required Azure Landing Zone security model. Direct Internet routing bypasses central inspection, RDP is allowed from the Internet, and the workload creates its own hub with incomplete peering instead of consuming a validated platform hub. Storage and Key Vault retain public network access, while Private Endpoint DNS integration is incomplete. Platform-owned firewall, DNS, monitoring, address allocation, and deployed effective-state controls require external validation.

## Severity Overview

| Critical | High | Medium | Low |
|---:|---:|---:|---:|
| 0 | 5 | 1 | 0 |

## Assessment Scorecard

| Area | Status | Summary |
|---|---|---|
| Network Topology | Action Required | A workload-managed hub and one-way peering do not establish approved Landing Zone connectivity. |
| Routing & Egress | Action Required | The application subnet has an explicit default route directly to the Internet. |
| Network Security | Action Required | Internet-sourced RDP and broad intra-VNet defaults conflict with least-privilege controls. |
| Private Connectivity | Action Required | Storage has a Private Endpoint, but Storage and Key Vault remain publicly accessible. |
| DNS | Action Required | The Private DNS zone is not linked or associated with the Storage Private Endpoint. |
| Monitoring & Observability | External Validation Required | No workload diagnostic, flow-log, connectivity-monitoring, or alert resources are declared. |

## Top Priority Actions

| Priority | Finding | Action |
|---|---|---|
| P1 | NET-001 — Application egress bypasses central inspection | Obtain the approved platform firewall or NVA next-hop details, replace the Internet default route with a VirtualAppliance route, and validate effective routes and return-path symmetry for every workload subnet requiring egress. |
| P1 | NET-002 — Management subnet permits Internet-sourced RDP | Remove the Internet-sourced RDP rule and implement the approved administrative path, such as Azure Bastion, Entra Private Access, or a restricted private management network with identity-based privileged access controls. |
| P1 | NET-003 — Workload recreates an incomplete connectivity hub | Remove workload ownership of the hub, obtain the approved hub VNet through platform outputs or explicit inputs, retain only the workload-owned peering side, and coordinate the reciprocal platform-owned peering with required forwarded-traffic and gateway settings. |

## Architecture Overview

Terraform declares workload-managed hub and application VNets, three application-side subnets, one-way spoke-to-hub peering, NSGs on application and management subnets, direct Internet egress from the application subnet, and a Storage blob Private Endpoint without complete DNS integration.

**Key components:**

- Workload-managed hub VNet
- Application VNet
- Application subnet
- Management subnet
- Private Endpoint subnet
- Storage blob Private Endpoint
- Workload-managed Private DNS zone

### Material Traffic Flows

- **Application Internet egress**: Application subnet → 0.0.0.0/0 route → Internet — **Non-compliant**
- **Spoke-to-hub connectivity**: Application VNet → One-way peering → Workload-managed hub VNet — **Incomplete**
- **Storage blob access**: Application VNet → Storage Private Endpoint → Storage blob service — **DNS integration incomplete; public fallback enabled**

## Findings

<details>
<summary><strong>High · NET-001 — Application egress bypasses central inspection</strong></summary>

**Area:** Routing & Egress  
**Requirement:** `NET-FW-002`  
**Priority:** P1  

**Evidence**

- `infra/routing.tf` — The application route table sends 0.0.0.0/0 to next hop type Internet.
- `infra/routing.tf` — The bypass route table is associated with the application subnet.

**Observed State**  
Application traffic is explicitly routed directly to the Internet, and no central firewall or approved NVA next hop is referenced.

**Expected State**  
Internet-bound workload traffic must traverse the approved central inspection layer without a direct Internet bypass.

**Risk**  
Outbound traffic can evade centrally governed filtering, threat detection, and egress policy.

**Recommendation**  
Obtain the approved platform firewall or NVA next-hop details, replace the Internet default route with a VirtualAppliance route, and validate effective routes and return-path symmetry for every workload subnet requiring egress.

**Dependencies / Considerations**

- Platform-provided central inspection next-hop address and routing design

</details>

<details>
<summary><strong>High · NET-002 — Management subnet permits Internet-sourced RDP</strong></summary>

**Area:** Network Security  
**Requirement:** `NET-NSG-003`  
**Priority:** P1  

**Evidence**

- `infra/security.tf` — The management NSG allows TCP 3389 from the Internet service tag to any destination.

**Observed State**  
An inbound NSG rule authorizes RDP from the public Internet across the management subnet.

**Expected State**  
Administrative access must use an approved controlled path and administrative ports must not be authorized directly from the Internet without an approved exception.

**Risk**  
Any resource later given a viable public ingress path could expose RDP to Internet scanning, credential attacks, and remote compromise.

**Recommendation**  
Remove the Internet-sourced RDP rule and implement the approved administrative path, such as Azure Bastion, Entra Private Access, or a restricted private management network with identity-based privileged access controls.

**Dependencies / Considerations**

- Security-approved administrative access architecture

</details>

<details>
<summary><strong>High · NET-003 — Workload recreates an incomplete connectivity hub</strong></summary>

**Area:** Network Topology  
**Requirement:** `NET-TOPO-001`  
**Priority:** P1  

**Evidence**

- `infra/network.tf` — The workload declares and owns a hub VNet rather than referencing an approved platform connectivity resource.
- `infra/network.tf` — Only application-to-hub peering is declared; no reciprocal hub-to-application peering exists.

**Observed State**  
The repository builds a standalone hub and a single directional peering with no firewall, gateway, DNS, or shared platform integration.

**Expected State**  
The workload must consume the approved centrally managed Landing Zone connectivity platform and establish both directional sides of required VNet peering under the correct ownership model.

**Risk**  
The resulting topology can be isolated from enterprise controls and shared services, while incomplete peering can prevent expected hub-initiated or return connectivity.

**Recommendation**  
Remove workload ownership of the hub, obtain the approved hub VNet through platform outputs or explicit inputs, retain only the workload-owned peering side, and coordinate the reciprocal platform-owned peering with required forwarded-traffic and gateway settings.

**Dependencies / Considerations**

- Approved platform hub resource ID
- Platform-owned reciprocal peering configuration

</details>

<details>
<summary><strong>High · NET-004 — Backend PaaS services retain public network paths</strong></summary>

**Area:** Private Connectivity  
**Requirement:** `NET-PE-001`  
**Priority:** P1  

**Evidence**

- `infra/storage.tf` — Storage public network access is enabled and network rules use default action Allow.
- `infra/keyvault.tf` — Key Vault public network access is enabled and no Key Vault Private Endpoint is declared.

**Observed State**  
Storage remains open to public network traffic despite a blob Private Endpoint, and Key Vault has only a public network path.

**Expected State**  
Sensitive backend PaaS services must use approved private connectivity and disable or restrict unrequired public access.

**Risk**  
Clients can bypass the intended private path, increasing exposure and weakening network-based data-access controls.

**Recommendation**  
Complete and validate private connectivity for required Storage subresources and Key Vault, then disable public network access or apply the explicitly approved restricted-access policy without using public access as a fallback.

**Dependencies / Considerations**

- Service-specific private connectivity requirements
- Approved enterprise Private DNS integration

</details>

<details>
<summary><strong>High · NET-005 — Storage Private Endpoint lacks usable DNS integration</strong></summary>

**Area:** DNS  
**Requirement:** `NET-PE-003`  
**Priority:** P2  

**Evidence**

- `infra/storage.tf` — A privatelink.blob.core.windows.net zone is created, but no Private DNS zone group or VNet link is declared.

**Observed State**  
The Storage blob Private Endpoint targets the correct subresource and subnet, but Terraform does not register its address in the zone or make the zone resolvable from the application VNet.

**Expected State**  
Private Endpoint names must resolve to the expected private IP through the approved enterprise DNS design, without duplicating centrally owned DNS authority.

**Risk**  
Clients can resolve the public endpoint or fail resolution, encouraging continued public access and preventing reliable private connectivity.

**Recommendation**  
Confirm Private DNS zone ownership with the platform team; use the shared zone when centrally managed, add the required zone group and approved VNet/DNS resolver integration, and test name resolution separately from TCP connectivity.

**Dependencies / Considerations**

- Enterprise Private DNS zone ownership and resolver design

</details>

<details>
<summary><strong>Medium · NET-006 — Subnet segmentation does not constrain lateral movement</strong></summary>

**Area:** Network Security  
**Requirement:** `NET-NSG-004`  
**Priority:** P2  

**Evidence**

- `infra/security.tf` — Application and management NSGs define no explicit least-privilege east-west rules or denials, leaving default VirtualNetwork access effective.
- `infra/network.tf` — The Private Endpoint subnet has no NSG association.

**Observed State**  
Subnets are separated by purpose, but their controls do not define or enforce required communication paths between security boundaries.

**Expected State**  
East-west access must be limited to documented application flows and unrelated segments must not receive broad connectivity by default.

**Risk**  
Compromise of one segment can enable discovery or access across application, management, and private service boundaries.

**Recommendation**  
Document required east-west flows, add least-privilege NSG rules and explicit denials at suitable priorities, associate controls with relevant subnets, and verify both allowed and prohibited paths.

**Dependencies / Considerations**

- Approved workload communication matrix

</details>

## Requirements Compliance

| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| `NET-ZT-002` | Not Met | infra/security.tf | Internet-sourced and default intra-VNet access are not scoped to documented workload flows. |
| `NET-ZT-004` | Not Met | infra/routing.tf; infra/storage.tf; infra/keyvault.tf | Direct Internet egress and public PaaS paths bypass required central and private controls. |
| `NET-TOPO-001` | Not Met | infra/network.tf | The workload creates an independent hub and only one peering direction. |
| `NET-TOPO-002` | Met | infra/network.tf | The workload uses a distinct application VNet. |
| `NET-TOPO-003` | Partially Met | infra/network.tf; infra/security.tf | Purpose-specific subnets exist, but east-west enforcement is incomplete. |
| `NET-TOPO-004` | Not Met | infra/network.tf; infra/storage.tf | The workload recreates hub connectivity and a Private DNS zone without validated platform ownership. |
| `NET-IP-001` | Unable to Validate | infra/network.tf | CIDRs are declared, but enterprise and on-premises address allocations are unavailable. |
| `NET-SNET-001` | Partially Met | infra/network.tf; infra/security.tf | Subnets are separated by purpose, but security enforcement is incomplete. |
| `NET-SNET-002` | Unable to Validate | infra/network.tf; infra/storage.tf | A dedicated subnet is used, but approval against the enterprise model is unavailable. |
| `NET-NSG-001` | Partially Met | infra/security.tf | NSGs are associated to application and management subnets but rules are not least privilege. |
| `NET-NSG-003` | Not Met | infra/security.tf | RDP is authorized from the Internet. |
| `NET-NSG-004` | Not Met | infra/security.tf | No explicit east-west restrictions are defined. |
| `NET-FW-001` | External Dependency | docs/platform-context.md | The approved central inspection service and ownership are not identified. |
| `NET-FW-002` | Not Met | infra/routing.tf | Application egress routes directly to the Internet. |
| `NET-FW-004` | External Dependency | docs/platform-context.md | Platform firewall policy and change ownership cannot be validated. |
| `NET-FW-005` | External Dependency | docs/platform-context.md | No central firewall policy evidence is available. |
| `NET-RT-001` | Not Met | infra/routing.tf | The configured default route bypasses central inspection. |
| `NET-RT-002` | Partially Met | infra/routing.tf | A route table is associated to the application subnet, but other workload subnets lack validated controlled routing. |
| `NET-RT-003` | Unable to Validate | Repository IaC only | No approved stateful inspection path or live effective routes are available. |
| `NET-RT-004` | Unable to Validate | Live Azure validation not performed | Effective routes and deployed next hops were not queried. |
| `NET-IN-001` | Unable to Validate | infra/security.tf | Internet-sourced NSG rules exist, but no approved exposure requirement or deployed public ingress path was provided. |
| `NET-ADM-001` | Not Met | infra/security.tf | The only declared administrative path is an Internet-sourced RDP rule. |
| `NET-PE-001` | Not Met | infra/storage.tf; infra/keyvault.tf | Storage private connectivity is incomplete and Key Vault has no Private Endpoint. |
| `NET-PE-002` | Not Met | infra/storage.tf; infra/keyvault.tf | Public network access is enabled on both backend services. |
| `NET-PE-003` | Partially Met | infra/storage.tf | The Storage target and blob subresource are correct, but DNS integration is absent. |
| `NET-PE-004` | Not Met | infra/storage.tf; infra/keyvault.tf | Public paths remain enabled alongside incomplete or absent private connectivity. |
| `NET-DNS-001` | Not Met | infra/storage.tf | No zone group or VNet link enables private endpoint resolution. |
| `NET-DNS-002` | External Dependency | docs/platform-context.md | Enterprise resolver and forwarding design are not available. |
| `NET-DNS-003` | Unable to Validate | infra/storage.tf | The workload creates a Private DNS zone, but central namespace ownership is not identified. |
| `NET-MON-001` | External Dependency | No monitoring resources in infra/ | No repository telemetry is declared and the central monitoring platform is unspecified. |
| `NET-MON-002` | Unable to Validate | No flow-log resources in infra/ | Flow visibility may be platform managed but no evidence is available. |
| `NET-MON-003` | External Dependency | docs/platform-context.md | Central firewall telemetry cannot be validated. |
| `NET-MON-004` | External Dependency | No diagnostic settings in infra/ | No workload diagnostic integration or authoritative platform configuration is available. |
| `NET-MON-006` | External Dependency | No alert resources in infra/ | Meaningful network alerting cannot be validated. |
| `NET-RES-001` | Not Met | docs/platform-context.md; infra/ | Critical firewall, DNS, ingress, and monitoring dependencies are not concretely identified. |
| `NET-RES-002` | Unable to Validate | Repository IaC only | No central security-control failure behavior is documented or observable. |

## What Is Working Well

- **Purpose-specific subnet separation** — infra/network.tf separates application, management, and Private Endpoint address ranges.
- **Correct Storage Private Endpoint target** — infra/storage.tf targets the Storage account blob subresource from the dedicated Private Endpoint subnet.
- **Application route table association is explicit** — infra/routing.tf associates the declared route table with the application subnet.
- **PaaS transport baseline is partially hardened** — infra/storage.tf enforces TLS 1.2 and disables anonymous nested-item public access.

## Assumptions & Validation Required

| ID | Topic | Assumption / Dependency | Validation Required |
|---|---|---|---|
| ASM-001 | Approved Landing Zone connectivity | The platform context states that centrally managed connectivity should be consumed, but no concrete hub, firewall, peering, or routing outputs are available. | Obtain authoritative platform resource IDs, ownership boundaries, next hops, and peering settings. |
| ASM-002 | Address-space allocation | The 10.10.0.0/16 and 10.20.0.0/16 ranges cannot be compared with enterprise or hybrid networks. | Confirm both CIDRs against the authoritative IP address management allocation. |
| ASM-003 | Enterprise DNS ownership | Private DNS zones and resolver integration may be centrally managed, but no authoritative source identifies ownership. | Confirm zone ownership, VNet links, resolver paths, and hybrid forwarding with the platform team. |
| ASM-004 | Central monitoring | The repository contains no diagnostics, flow logs, connectivity monitors, or alert rules; these controls may exist outside the workload repository. | Verify deployed diagnostic settings, telemetry destinations, retention, critical-path monitoring, and actionable alerts. |
| ASM-005 | Live Azure state | No authenticated Azure discovery was performed. | Validate effective routes, peering state, public endpoints, Private Endpoint approval and DNS, NSG effective rules, and possible configuration drift. |

---

Generated from `network-assessment.json` by the repository assessment renderer.
