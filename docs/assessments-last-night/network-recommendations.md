# Azure Networking Assessment

> [!WARNING]
> **Overall Status: Action Required**
>
> 0 Critical · 5 High · 2 Medium · 0 Low

## Assessment Context

| Attribute | Value |
|---|---|
| Scope | Repository IaC assessment of infra/ |
| Environment | Test |
| Region | Canada Central (Terraform default) |
| Assessment Date | 2026-10-06 |
| Live Azure Validation | No |

## Executive Summary

The Terraform defines useful workload subnet separation and a correctly targeted Storage blob Private Endpoint, but the intended traffic paths do not meet the documented Zero Trust baseline. The application subnet explicitly routes Internet traffic directly to the Internet, the management NSG authorizes Internet-sourced RDP, and backend PaaS services retain unrestricted public access. Private DNS integration is incomplete, the repository creates its own hub instead of consuming a validated platform hub, and no network telemetry or alerting is defined. Remediation should first remove direct egress and administrative exposure, then establish private-only PaaS connectivity through the approved shared platform.

## Severity Overview

| Critical | High | Medium | Low |
|---:|---:|---:|---:|
| 0 | 5 | 2 | 0 |

## Assessment Scorecard

| Area | Status | Summary |
|---|---|---|
| Network Topology | Action Required | The workload creates a local hub and only one peering direction; approved platform connectivity is not established. |
| Routing & Egress | Action Required | The application subnet default route bypasses central inspection and uses the Internet next hop. |
| Network Security | Action Required | Internet-sourced RDP is authorized and east-west controls do not demonstrate least privilege. |
| Private Connectivity | Action Required | Storage and Key Vault retain public access; Key Vault has no Private Endpoint. |
| DNS | Action Required | The Storage private zone has no VNet link or Private DNS zone group. |
| Monitoring & Observability | Action Required | No flow logs, diagnostic settings, connectivity monitors, or alerts are declared. |

## Top Priority Actions

| Priority | Finding | Action |
|---|---|---|
| P1 | NET-001 — Application egress bypasses central inspection | Obtain the approved platform firewall or NVA next-hop configuration, replace the Internet default route with the approved VirtualAppliance path, and validate effective and return routes before deployment. |
| P1 | NET-002 — Management subnet authorizes Internet-sourced RDP | Remove the Internet-to-RDP rule and permit administration only through the approved Bastion, private management, or Entra Private Access path, scoped to required sources and destinations. |
| P1 | NET-003 — Backend PaaS services retain unrestricted public access | Set Storage public access to disabled after validating private access, add an approved Key Vault Private Endpoint and DNS integration, disable Key Vault public access, and add only explicitly approved exceptions if required. |

## Architecture Overview

The repository deploys separate hub and application VNets in one resource group. The application VNet contains application, Private Endpoint, and management subnets, with only application-to-hub peering. The application subnet has an NSG and a route table; management has an NSG; Storage has a blob Private Endpoint; Key Vault remains public.

**Key components:**

- Repository-managed hub VNet
- Application spoke VNet
- Application subnet
- Private Endpoint subnet
- Management subnet
- Storage account and blob Private Endpoint
- Key Vault
- Application route table
- Application and management NSGs

### Material Traffic Flows

- **Internet egress**: Application subnet → 0.0.0.0/0 route → Internet — **Non-compliant**
- **Hub connectivity**: Application VNet → One-way peering → Repository-managed hub VNet — **Incomplete**
- **Storage blob access**: Approved client → Storage blob Private Endpoint → Storage account — **DNS integration incomplete; public fallback enabled**

## Findings

<details>
<summary><strong>High · NET-001 — Application egress bypasses central inspection</strong></summary>

**Area:** Routing & Egress  
**Requirement:** `NET-FW-002`  
**Priority:** P1  

**Evidence**

- `infra/routing.tf` — The application route table defines 0.0.0.0/0 with next_hop_type set to Internet and associates it with the application subnet.

**Observed State**  
Internet-bound application traffic is intentionally routed directly to the Internet; no approved firewall or NVA next hop is referenced.

**Expected State**  
Internet egress must traverse the approved central inspection layer, and workload routes must not introduce a direct Internet bypass.

**Risk**  
Workload egress can avoid centrally governed filtering, threat detection, logging, and destination controls.

**Recommendation**  
Obtain the approved platform firewall or NVA next-hop configuration, replace the Internet default route with the approved VirtualAppliance path, and validate effective and return routes before deployment.

**Dependencies / Considerations**

- Platform-provided central inspection next-hop address and routing design

</details>

<details>
<summary><strong>High · NET-002 — Management subnet authorizes Internet-sourced RDP</strong></summary>

**Area:** Network Security  
**Requirement:** `NET-NSG-003`  
**Priority:** P1  

**Evidence**

- `infra/security.tf` — The management NSG allows TCP/3389 from the Internet service tag to any destination in the subnet.
- `infra/network.tf` — The management NSG is associated with the dedicated management subnet.

**Observed State**  
The subnet policy permits direct RDP from the Internet if a routable public ingress path exists. No public IP resource was found in this repository, so deployed reachability was not validated.

**Expected State**  
Administrative access must use an approved controlled path and administrative ports must not be authorized directly from the public Internet without an approved exception.

**Risk**  
A present or future public ingress path could expose privileged administration to password attacks and remote exploitation.

**Recommendation**  
Remove the Internet-to-RDP rule and permit administration only through the approved Bastion, private management, or Entra Private Access path, scoped to required sources and destinations.

**Dependencies / Considerations**

- Confirmation of the organization-approved administrative access path

</details>

<details>
<summary><strong>High · NET-003 — Backend PaaS services retain unrestricted public access</strong></summary>

**Area:** Private Connectivity  
**Requirement:** `NET-PE-002`  
**Priority:** P1  

**Evidence**

- `infra/storage.tf` — Storage public network access is enabled and network_rules.default_action is Allow despite the blob Private Endpoint.
- `infra/keyvault.tf` — Key Vault public network access is enabled and no Key Vault Private Endpoint is declared.

**Observed State**  
Storage can be accessed through its public endpoint from unrestricted networks, and Key Vault is public-only in the declared implementation.

**Expected State**  
Sensitive backend PaaS services must use approved private connectivity and disable or restrict unrequired public access without public fallback.

**Risk**  
Public data-plane endpoints expand the attack surface and allow clients to bypass workload routing, segmentation, and private DNS controls.

**Recommendation**  
Set Storage public access to disabled after validating private access, add an approved Key Vault Private Endpoint and DNS integration, disable Key Vault public access, and add only explicitly approved exceptions if required.

**Dependencies / Considerations**

- Confirmation of workload data sensitivity and approved PaaS access sources

</details>

<details>
<summary><strong>High · NET-004 — Storage Private Endpoint DNS integration is incomplete</strong></summary>

**Area:** DNS  
**Requirement:** `NET-DNS-001`  
**Priority:** P2  

**Evidence**

- `infra/storage.tf` — A privatelink.blob.core.windows.net zone is created, but the Private Endpoint has no private_dns_zone_group.
- `infra/` — No azurerm_private_dns_zone_virtual_network_link resource is declared.

**Observed State**  
The private zone is neither attached to the Private Endpoint for record registration nor linked to a VNet for resolution.

**Expected State**  
Approved clients must resolve the Storage service name to the Private Endpoint address through the enterprise DNS design, without creating conflicting DNS authority.

**Risk**  
Clients can resolve the public Storage endpoint instead of the private address, fail private connectivity, or depend on the currently enabled public fallback.

**Recommendation**  
Confirm whether the private zone is platform-owned. Reference the approved shared zone when available, add the Private DNS zone group, and implement the required VNet link or enterprise DNS forwarding path.

**Dependencies / Considerations**

- Platform confirmation of Private DNS zone ownership and resolver integration

</details>

<details>
<summary><strong>High · NET-005 — Workload repository creates an incomplete local hub</strong></summary>

**Area:** Network Topology  
**Requirement:** `NET-TOPO-001`  
**Priority:** P2  

**Evidence**

- `infra/network.tf` — The workload declares both hub and application VNets and only an application-to-hub peering.
- `infra/outputs.tf` — The locally created hub VNet is exposed as a workload output rather than referenced as an existing platform service.
- `docs/platform-context.md` — Workloads are expected to consume centrally managed connectivity capabilities instead of recreating them.

**Observed State**  
The repository creates a nominal hub with no central firewall, DNS, gateway, or reverse peering, rather than integrating with validated platform connectivity.

**Expected State**  
The workload must consume the approved Azure Landing Zone connectivity platform and must not recreate an enterprise hub or other shared connectivity service.

**Risk**  
The spoke can be isolated from shared services or connected through an ungoverned topology that lacks inspection, return connectivity, DNS, and hybrid routes.

**Recommendation**  
Remove the workload-owned hub after obtaining the approved platform VNet or Virtual WAN identifiers, establish all platform-owned and workload-owned directional connections with the required forwarded-traffic settings, and validate effective routes.

**Dependencies / Considerations**

- Platform hub or Virtual WAN identifiers and peering ownership model

</details>

<details>
<summary><strong>Medium · NET-006 — East-west least-privilege controls are not established</strong></summary>

**Area:** Network Security  
**Requirement:** `NET-NSG-004`  
**Priority:** P2  

**Evidence**

- `infra/security.tf` — Only application and management subnets have NSG associations; no explicit required east-west flows or deny controls are defined.
- `infra/network.tf` — The Private Endpoint subnet has no NSG association, and all three subnets share one VNet.
- `infra/security.tf` — The application inbound HTTPS rule uses Internet as source and any subnet destination rather than a named approved ingress path.

**Observed State**  
Default Azure VNet rules remain the principal east-west policy, and the implementation does not encode required flows among application, management, and Private Endpoint boundaries.

**Expected State**  
Network controls must allow only documented workload flows and limit lateral movement between materially different security boundaries.

**Risk**  
A compromised resource may have broader connectivity to management or backend endpoints than the application requires.

**Recommendation**  
Document required flows, associate an approved NSG policy with each applicable subnet, replace broad sources and destinations with approved ingress and workload prefixes or service tags, and add explicit higher-priority denies where needed.

**Dependencies / Considerations**

- Required application, management, and Private Endpoint traffic-flow matrix

</details>

<details>
<summary><strong>Medium · NET-007 — Network security telemetry and alerting are absent</strong></summary>

**Area:** Monitoring & Observability  
**Requirement:** `NET-MON-001`  
**Priority:** P3  

**Evidence**

- `infra/` — No diagnostic settings, Virtual Network flow logs, Connection Monitor resources, metric alerts, or Log Analytics integration are declared.

**Observed State**  
The workload IaC does not provide flow visibility, network diagnostic integration, critical-path monitoring, or meaningful network alerts.

**Expected State**  
Network-security telemetry must support detection and investigation, critical resources must integrate with approved monitoring, and material failures must produce meaningful alerts.

**Risk**  
Operators may be unable to detect bypass, investigate denied or allowed flows, or identify connectivity degradation promptly.

**Recommendation**  
Integrate applicable network resources with the approved central monitoring destination, enable supported VNet flow visibility where operationally justified, and define alerts or connectivity tests for material workload paths.

**Dependencies / Considerations**

- Platform monitoring workspace or SIEM destination
- Operational definition of business-critical connectivity paths

</details>

## Requirements Compliance

| Requirement | Status | Evidence | Notes |
|---|---|---|---|
| `NET-TOPO-001` | Not Met | infra/network.tf | A local hub is created and approved platform connectivity is not referenced. |
| `NET-TOPO-002` | Met | infra/network.tf | The workload uses a dedicated application VNet. |
| `NET-TOPO-003` | Partially Met | infra/network.tf; infra/security.tf | Subnets are separated by purpose, but enforceable least-privilege controls are incomplete. |
| `NET-TOPO-004` | Not Met | infra/network.tf; docs/platform-context.md | The workload recreates a hub instead of consuming confirmed shared connectivity. |
| `NET-IP-001` | Unable to Validate | infra/network.tf | The declared hub and application ranges do not overlap each other, but connected platform and on-premises ranges are unavailable. |
| `NET-SNET-001` | Partially Met | infra/network.tf; infra/security.tf | Application, management, and Private Endpoint subnets are separate, but their boundaries are not fully enforced. |
| `NET-SNET-002` | Partially Met | infra/storage.tf | The Storage endpoint uses a dedicated subnet; platform approval of that subnet model is unavailable. |
| `NET-NSG-001` | Partially Met | infra/security.tf | NSGs exist for two subnets, but the rules do not demonstrate least privilege. |
| `NET-NSG-003` | Not Met | infra/security.tf | The management NSG authorizes Internet-sourced RDP. |
| `NET-NSG-004` | Not Met | infra/security.tf | Required east-west flows and restrictive segmentation rules are not encoded. |
| `NET-FW-001` | Not Met | infra/network.tf; infra/routing.tf | No approved central inspection layer is consumed by the workload. |
| `NET-FW-002` | Not Met | infra/routing.tf | The application default route uses the Internet next hop. |
| `NET-FW-003` | Not Met | infra/routing.tf | A direct 0.0.0.0/0 to Internet bypass is explicitly declared. |
| `NET-FW-004` | External Dependency | docs/platform-context.md | No platform firewall policy or ownership evidence is available. |
| `NET-RT-001` | Not Met | infra/routing.tf | The configured route bypasses the required central inspection path. |
| `NET-RT-002` | Partially Met | infra/routing.tf | The route table is associated with the application subnet, but it enforces a non-compliant path. |
| `NET-RT-003` | Unable to Validate | infra/network.tf; infra/routing.tf | No complete stateful inspection or return-route design is available. |
| `NET-RT-004` | Unable to Validate | Repository-only assessment | Effective routes were not queried from live Azure. |
| `NET-IN-001` | Unable to Validate | infra/security.tf | Internet-sourced HTTPS is allowed, but public ingress need and approval are undocumented and no public ingress resource is declared. |
| `NET-IN-002` | Unable to Validate | infra/ | No approved ingress component is declared; whether Internet ingress is required is unknown. |
| `NET-ADM-001` | Not Met | infra/security.tf | The only explicit administrative policy is an Internet-sourced RDP allow rule. |
| `NET-PE-001` | Partially Met | infra/storage.tf; infra/keyvault.tf | Storage has a blob Private Endpoint, but Key Vault does not. |
| `NET-PE-002` | Not Met | infra/storage.tf; infra/keyvault.tf | Both backend services have public network access enabled; Storage permits all networks. |
| `NET-PE-003` | Partially Met | infra/storage.tf | The target, blob subresource, and dedicated subnet are correct, but DNS integration is missing. |
| `NET-PE-004` | Not Met | infra/storage.tf | The Storage public endpoint remains an unrestricted fallback. |
| `NET-DNS-001` | Not Met | infra/storage.tf | No zone group or VNet link establishes private endpoint name resolution. |
| `NET-DNS-002` | External Dependency | docs/platform-context.md | The enterprise resolver and forwarding design is not provided. |
| `NET-DNS-003` | Unable to Validate | infra/storage.tf | A workload private zone is created, but central namespace ownership is unknown. |
| `NET-MON-001` | Not Met | infra/ | No workload network-security telemetry is declared or externally evidenced. |
| `NET-MON-002` | Not Met | infra/ | No Virtual Network flow logging is declared. |
| `NET-MON-003` | External Dependency | docs/platform-context.md | Central firewall telemetry cannot be validated without platform evidence. |
| `NET-MON-004` | Not Met | infra/ | No diagnostic settings or approved monitoring destination are declared. |
| `NET-MON-005` | Unable to Validate | infra/ | Business-critical paths and any externally managed connectivity monitoring are not identified. |
| `NET-MON-006` | Not Met | infra/ | No network-security or connectivity alerts are declared. |
| `NET-ENC-001` | Partially Met | infra/storage.tf; infra/security.tf | Storage requires TLS 1.2 and application ingress uses HTTPS, but RDP exposure remains an administrative transport concern. |
| `NET-RES-001` | Not Met | infra/; docs/platform-context.md | Critical firewall, DNS, ingress, and monitoring dependencies are not concretely identified. |
| `NET-RES-002` | Not Met | infra/routing.tf; infra/storage.tf | Direct Internet routing and public Storage access provide bypass paths rather than failing closed. |

## What Is Working Well

- **Purpose-specific subnet separation** — infra/network.tf separates application, management, and Private Endpoint address ranges.
- **Correct Storage Private Endpoint target** — infra/storage.tf targets the Storage account blob subresource from the dedicated Private Endpoint subnet.
- **Storage transport baseline** — infra/storage.tf requires TLS 1.2 and disables anonymous nested-item publication.
- **Explicit route and NSG associations** — infra/routing.tf and infra/security.tf associate declared controls with their intended application and management subnets.

## Assumptions & Validation Required

| ID | Topic | Assumption / Dependency | Validation Required |
|---|---|---|---|
| ASM-001 | Live Azure state | The assessment is based on repository intent only; deployed reachability, effective routes, effective NSG rules, and configuration drift were not inspected. | Perform targeted read-only Azure validation before security acceptance. |
| ASM-002 | Shared connectivity platform | Platform hub, firewall, DNS, hybrid connectivity, and monitoring identifiers and configurations were not available. | Obtain authoritative platform outputs and ownership details from the platform team. |
| ASM-003 | Workload security profile | Required public ingress, egress destinations, hybrid access, administrative model, data sensitivity, and critical paths are not documented. | Complete the workload security profile and required-flow matrix. |
| ASM-004 | Address-space uniqueness | The declared VNets do not overlap each other, but no connected Azure or on-premises address inventory was available. | Validate 10.10.0.0/16 and 10.20.0.0/16 against the enterprise IP address plan. |

---

Generated from `network-assessment.json` by the repository assessment renderer.
