# Network Requirements

## 1. Purpose and Authority

This document defines the authoritative network-security requirements for workloads deployed into an enterprise Azure Landing Zone.

The design is intentionally security-led and follows Zero Trust network design principles:

1. **Verify explicitly** — network location alone MUST NOT establish trust.
2. **Use least-privilege access** — only required communication paths, sources, destinations, ports, and protocols are permitted.
3. **Assume breach** — the network MUST be segmented, lateral movement MUST be constrained, traffic MUST be observable, and security controls MUST limit blast radius.

These requirements are intended to be reusable across organizations, Azure regions, subscriptions, and workload types.

Downstream engineers, Terraform implementations, AI implementation agents, architecture reviewers, and assessment tooling MUST treat this document as the network architecture and security contract.

Environment-specific values such as regions, CIDRs, firewall addresses, DNS addresses, and resource identifiers MUST be obtained from approved workload documentation, platform documentation, repository configuration, or explicit user input.

Missing environmental values MUST NOT be invented.

---

## 2. Security Design Objectives

The network architecture MUST achieve the following security outcomes:

- no implicit trust based solely on network location;
- centrally governed ingress and egress controls;
- centrally inspected Internet-bound traffic;
- least-privilege east-west communication;
- segmentation between workloads, tiers, environments, and administrative paths where required;
- private access to sensitive backend PaaS services;
- no uncontrolled administrative exposure to the Internet;
- no unintended direct Internet bypass;
- controlled hybrid connectivity where required;
- DNS that supports private connectivity without public fallback;
- telemetry sufficient to detect, investigate, and respond to suspicious or failed network activity;
- clear ownership boundaries between workload and platform teams;
- no recreation or unauthorized modification of centrally managed security controls.

---

## 3. Requirement Classification

Requirements are classified as:

- **Mandatory Zero Trust Baseline** — applies to workloads governed by this network-security standard.
- **Conditional Requirement** — applies only where the workload uses the relevant capability.
- **Platform Dependency** — depends on infrastructure or configuration outside the workload repository.
- **Required Confirmation** — cannot safely be determined from available information.
- **Recommendation** — security improvement that is desirable but not mandatory unless adopted by organizational policy.

Use the following assessment states:

- **Requirement Met**
- **Requirement Violation**
- **Not Applicable**
- **Unable to Validate**
- **External Dependency**
- **Positive Finding**

Do not treat `Not Applicable` and `Unable to Validate` as equivalent.

---

## 4. Workload Security Profile

The following information MUST be established before implementation or assessment.

| Attribute | Required Value |
|---|---|
| Approved Azure region(s) | Derived from workload requirements |
| Connectivity model | Approved ALZ connectivity architecture |
| Central inspection layer | Azure Firewall or approved centrally managed NVA |
| Central inspection next hop | Derived from platform configuration |
| Internet ingress required | Yes / No |
| Internet egress required | Yes / No |
| Hybrid connectivity required | Yes / No |
| Private PaaS connectivity required | Service-specific / policy-defined |
| Administrative connectivity model | Approved management path |
| Enterprise DNS integration | Required where private/shared DNS is used |
| Central monitoring platform | Platform-defined |
| Data sensitivity / workload classification | Organization-defined |
| Workload network owner | Organization-defined |
| Platform network owner | Organization-defined |

Unknown values MUST be recorded as:

`Required Confirmation`

Do not invent:

- VNet or subnet CIDRs;
- firewall IP addresses;
- DNS server addresses;
- route advertisements;
- BGP ASNs;
- platform resource names;
- subscription IDs;
- resource group names;
- gateway SKUs;
- Azure regions;
- firewall rules;
- DNS forwarding rules.

---

## 5. Azure Landing Zone Zero Trust Baseline

### `NET-ZT-001` — No Implicit Network Trust

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

Network location alone MUST NOT be treated as proof that a source, destination, user, device, or workload is trusted.

Being inside:

- an Azure VNet;
- a spoke;
- a hub;
- an on-premises network;
- a peered network;
- an ExpressRoute-connected network

MUST NOT automatically grant broad access.

Access MUST be explicitly permitted based on the required communication path and applicable identity, application, network, and security policy.

---

### `NET-ZT-002` — Least-Privilege Connectivity

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload / Security

Network controls MUST permit only the communication required for the workload to function.

Rules SHOULD be scoped by:

- source;
- destination;
- protocol;
- port;
- application path;
- service;
- environment.

Broad access such as unrestricted `Any -> Any` rules MUST NOT be used unless explicitly justified and approved.

---

### `NET-ZT-003` — Assume Breach and Limit Blast Radius

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

The network MUST be designed to limit lateral movement if a workload, identity, endpoint, or network segment is compromised.

The architecture MUST use appropriate segmentation and traffic controls between security boundaries.

---

### `NET-ZT-004` — Security Control Bypass Prevention

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST NOT  
**Owner:** Joint

The workload MUST NOT introduce network paths that bypass mandatory organizational security controls.

This includes bypass of:

- central firewall inspection;
- approved ingress controls;
- required Private Endpoints;
- enterprise DNS controls;
- security monitoring;
- approved administrative access paths.

---

## 6. Network Topology and Segmentation

### `NET-TOPO-001` — Approved Landing Zone Connectivity

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

The workload MUST integrate with the organization's approved Azure Landing Zone connectivity architecture.

The architecture MAY use:

- traditional hub-and-spoke;
- Azure Virtual WAN;
- another centrally governed enterprise Azure connectivity pattern.

The workload MUST NOT create a duplicate or independent connectivity platform where an approved central platform already exists.

---

### `NET-TOPO-002` — Workload Isolation

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload

The workload MUST use an appropriately isolated workload network boundary.

In a traditional hub-and-spoke design, workloads SHOULD normally use dedicated spoke VNets.

Production, non-production, management, and high-risk workloads SHOULD be separated where organizational policy or workload risk justifies distinct security boundaries.

---

### `NET-TOPO-003` — Segmentation by Security Boundary

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload / Security

Network segmentation MUST be based on security and communication requirements, not only resource convenience.

Where required, separate:

- application tiers;
- management traffic;
- data tiers;
- Private Endpoints;
- shared services;
- externally exposed components;
- privileged systems;
- environments with different trust or risk levels.

Segmentation MUST be enforceable through routing, NSGs, firewall controls, Private Link, or other approved controls.

---

### `NET-TOPO-004` — Shared Platform Services

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST NOT  
**Owner:** Workload

The workload MUST NOT recreate centrally managed security or connectivity services.

Examples may include:

- enterprise hub;
- Virtual WAN hub;
- Azure Firewall;
- approved NVA;
- ExpressRoute gateway;
- VPN gateway;
- DNS Private Resolver;
- enterprise DNS;
- shared Private DNS zones;
- central monitoring or SIEM platform.

---

## 7. IP Addressing and Subnet Security

### `NET-IP-001` — Non-Overlapping Routed Address Space

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload

Workload address spaces MUST NOT overlap with networks that require routed connectivity.

This includes, where applicable:

- hub networks;
- connected Azure VNets;
- on-premises networks;
- management networks;
- partner networks;
- other routed environments.

---

### `NET-SNET-001` — Security-Oriented Subnet Design

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload

Subnet design MUST support intended security boundaries.

Subnets SHOULD separate resources when they require materially different:

- inbound policy;
- outbound policy;
- routing;
- administrative access;
- Private Endpoint placement;
- service delegation;
- inspection requirements.

Do not create segmentation with no security or operational purpose.

---

### `NET-SNET-002` — Private Endpoint Placement

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Workload

Where Private Endpoints are used, they MUST be deployed into approved subnets consistent with the organization's network-security model.

---

## 8. Network Security Groups and East-West Control

### `NET-NSG-001` — NSG Enforcement

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload

NSGs MUST be used where appropriate to enforce least-privilege subnet or workload communication.

Rules MUST be based on actual required flows.

---

### `NET-NSG-002` — Deny Unrequired Communication

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload

Communication not required by the workload SHOULD remain denied.

The implementation MUST NOT rely on broad permissive rules as a substitute for understanding workload traffic.

---

### `NET-NSG-003` — Restrict Administrative Ports

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST NOT  
**Owner:** Workload

Administrative ports such as:

- RDP;
- SSH;
- database administration ports;
- privileged management interfaces

MUST NOT be exposed directly to the public Internet unless an explicitly approved exception exists.

---

### `NET-NSG-004` — Minimize Lateral Movement

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload / Security

East-west communication between workload segments MUST be limited to required application flows.

A compromised workload segment SHOULD NOT have unrestricted visibility or connectivity to unrelated workload tiers or networks.

---

## 9. Central Firewall and Traffic Inspection

### `NET-FW-001` — Approved Central Inspection Layer

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Platform / Security

The workload MUST use the organization's approved central inspection layer.

The inspection layer is expected to be:

- Azure Firewall; or
- an approved centrally managed NVA.

The workload repository MUST NOT deploy an additional enterprise firewall unless explicitly authorized.

---

### `NET-FW-002` — Internet Egress Inspection

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

Internet-bound workload traffic MUST traverse the approved central inspection layer unless an explicit exception exists.

Expected logical flow:

```text
Workload
   ↓
Workload route / platform routing
   ↓
Central Firewall / Approved NVA
   ↓
Internet
```

---

### `NET-FW-003` — No Direct Internet Bypass

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST NOT  
**Owner:** Workload

Where centralized inspection is required, workload subnets MUST NOT use an uncontrolled direct Internet route such as:

```text
0.0.0.0/0 -> Internet
```

The workload MUST NOT introduce an alternative egress path that bypasses central inspection.

---

### `NET-FW-004` — Firewall Policy Ownership

**Classification:** Platform Dependency  
**Strength:** MUST  
**Owner:** Platform / Security

Firewall policies and centrally governed rule collections MUST remain under approved platform or security-team ownership.

Workload-specific firewall changes MUST follow the organization's approved request and change process.

---

### `NET-FW-005` — Inspection Rule Least Privilege

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Platform / Security

Firewall rules MUST be scoped to required communication.

Rules SHOULD restrict:

- source;
- destination;
- FQDN where appropriate;
- protocol;
- port;
- direction.

Broad unrestricted rules MUST require explicit security justification.

---

## 10. Routing Security

### `NET-RT-001` — Security-Controlled Routing

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

Routing MUST enforce the approved security architecture.

Configured routes MUST NOT:

- bypass central inspection;
- create unintended direct Internet access;
- create uncontrolled transit paths;
- allow unauthorized network reachability.

---

### `NET-RT-002` — Route Association

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload

Route tables required to enforce the approved traffic path MUST be associated with the correct subnets.

The presence of a route table without correct association does not satisfy this requirement.

---

### `NET-RT-003` — Routing Symmetry

**Classification:** Derived Architectural Requirement  
**Strength:** MUST  
**Owner:** Joint

Traffic traversing stateful firewalls or NVAs MUST preserve valid return paths.

The architecture MUST avoid asymmetric routing that could:

- bypass controls;
- break stateful inspection;
- cause dropped sessions;
- create inconsistent enforcement.

---

### `NET-RT-004` — Effective Route Validation

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

Compliance MUST be assessed against effective routing behaviour, not only source-code intent.

---

## 11. Inbound Connectivity and Public Exposure

### `NET-IN-001` — Intentional Public Exposure

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload / Security

Public exposure MUST be explicitly required, documented, and approved.

Resources MUST NOT become publicly reachable merely because public exposure is technically possible.

---

### `NET-IN-002` — Approved Ingress Control

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Joint

Internet-facing workloads MUST use an approved ingress architecture.

Examples may include:

- Azure Front Door with WAF;
- Application Gateway with WAF;
- approved load-balancing and firewall architecture;
- another organization-approved ingress service.

Direct Internet exposure SHOULD be minimized.

---

### `NET-IN-003` — Internal Workload Protection

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST NOT  
**Owner:** Workload

Internal-only workloads MUST NOT expose application endpoints directly to the public Internet.

---

### `NET-IN-004` — DDoS Protection

**Classification:** Conditional Requirement  
**Strength:** SHOULD / MUST when policy requires  
**Owner:** Platform / Security

Where the workload has public IP exposure or organizational policy requires it, appropriate DDoS protection MUST be evaluated and applied according to the approved platform standard.

---

## 12. Administrative and Privileged Network Access

### `NET-ADM-001` — Approved Administrative Path

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Security / Operations

Administrative access MUST use an approved controlled path.

Examples may include:

- Azure Bastion;
- Entra Private Access;
- private administrative networks;
- privileged access workstations;
- approved management services.

---

### `NET-ADM-002` — No Trust Based on Source Network Alone

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Security

Being connected through:

- corporate LAN;
- VPN;
- ExpressRoute;
- peered VNet;
- hub network

MUST NOT by itself grant unrestricted administrative access.

Network controls SHOULD complement identity, device, and privileged-access controls.

---

## 13. Azure PaaS and Private Connectivity

### `NET-PE-001` — Private Connectivity for Sensitive Backend Services

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload / Security

Backend PaaS services containing or processing sensitive workload data MUST use private connectivity where the Azure service supports the approved Private Link pattern, unless an explicit security exception exists.

Examples commonly include:

- Storage;
- Key Vault;
- SQL;
- managed data services;
- container registries;
- other supported backend PaaS services.

---

### `NET-PE-002` — Disable Unrequired Public Access

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload

Where a backend PaaS service is intended to be private-only, Public Network Access MUST be disabled or restricted in accordance with organizational policy.

---

### `NET-PE-003` — Correct Private Endpoint Configuration

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Workload

Private Endpoints MUST use:

- the correct target resource;
- the correct service subresource;
- an approved subnet;
- correct DNS integration.

---

### `NET-PE-004` — No Public Fallback

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST NOT  
**Owner:** Workload

Public network access MUST NOT be enabled as a workaround for:

- DNS failures;
- routing failures;
- Terraform deployment failures;
- Private Endpoint configuration errors;
- troubleshooting convenience.

---

## 14. DNS Security and Private Resolution

### `NET-DNS-001` — Private Endpoint Resolution

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Joint

Private Endpoint service names MUST resolve to the expected private IP addresses from all approved clients.

---

### `NET-DNS-002` — Enterprise DNS Integration

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Joint

Where enterprise DNS is part of the Azure Landing Zone architecture, workload DNS MUST integrate with the approved resolver and forwarding design.

This may include:

- Azure Private DNS;
- Azure DNS Private Resolver;
- custom DNS servers;
- conditional forwarding;
- enterprise DNS forwarders.

---

### `NET-DNS-003` — No Duplicate Private DNS Authority

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST NOT  
**Owner:** Joint

The workload MUST NOT create duplicate Private DNS zones that conflict with centrally managed namespace ownership.

---

### `NET-DNS-004` — DNS Is Not Proof of Connectivity

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

DNS and network connectivity MUST be validated separately.

Successful name resolution does not prove the network path is authorized or functional.

---

## 15. Hybrid Connectivity

Hybrid connectivity is conditional.

If the workload has no requirement to communicate with networks outside Azure, classify this domain as:

`Not Applicable`

---

### `NET-HYB-001` — Approved Hybrid Connectivity

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Platform / Joint

Where hybrid connectivity is required, the workload MUST use the organization's approved central connectivity service.

Examples may include:

- ExpressRoute;
- Site-to-Site VPN;
- Virtual WAN;
- another approved private connectivity model.

---

### `NET-HYB-002` — Hybrid Least Privilege

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Joint

Hybrid connectivity MUST provide access only to networks and services that require communication.

Hybrid connectivity MUST NOT create broad trust between on-premises and Azure networks.

---

### `NET-HYB-003` — Hybrid Route Control

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Joint

Required hybrid routes MUST be available without introducing:

- unintended route propagation;
- inspection bypass;
- asymmetric paths;
- overly broad connectivity.

---

### `NET-HYB-004` — Platform-Owned Hybrid Infrastructure

**Classification:** Platform Dependency  
**Strength:** MUST  
**Owner:** Platform

Existing hybrid infrastructure MUST be consumed as a shared platform service.

The workload repository MUST NOT recreate:

- ExpressRoute circuits;
- ExpressRoute gateways;
- VPN gateways;
- central routing infrastructure

unless explicitly authorized.

---

## 16. Monitoring, Visibility, and Threat Detection

### `NET-MON-001` — Security Telemetry

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

Network-security telemetry MUST be available to support:

- detection;
- investigation;
- incident response;
- troubleshooting;
- threat hunting where applicable.

---

### `NET-MON-002` — Flow Visibility

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** SHOULD  
**Owner:** Joint

Flow-level telemetry SHOULD be available for network segments where security investigation or operational troubleshooting requires it.

For new implementations, current Azure-supported Virtual Network flow logging SHOULD be used where appropriate.

---

### `NET-MON-003` — Firewall Logging

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Platform / Security

The central firewall MUST provide appropriate logs and metrics for the traffic it controls.

Where applicable, telemetry SHOULD include:

- network rule logs;
- application rule logs;
- NAT logs;
- threat intelligence events;
- IDPS events;
- DNS-related telemetry;
- health and platform metrics.

---

### `NET-MON-004` — Diagnostic Integration

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

Critical network resources MUST send appropriate diagnostic information to an approved monitoring destination.

Examples may include:

- Log Analytics;
- Event Hub;
- Storage;
- Microsoft Sentinel;
- another approved SIEM.

---

### `NET-MON-005` — Critical Connectivity Monitoring

**Classification:** Conditional Requirement  
**Strength:** SHOULD  
**Owner:** Operations

Business-critical network paths SHOULD be monitored for:

- reachability loss;
- latency degradation;
- packet loss;
- connection failure.

The monitoring requirement MUST define the operational outcome before prescribing a specific Azure monitoring service.

---

### `NET-MON-006` — Meaningful Alerting

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Operations / Security

Meaningful alerts MUST exist where a network-security or connectivity failure could materially affect the workload.

Log collection alone does not satisfy this requirement.

---

## 17. Encryption and Secure Transport

### `NET-ENC-001` — Encryption in Transit

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Workload / Platform

Sensitive traffic MUST use encrypted transport using protocols approved by organizational security policy.

Plain-text administrative or application protocols MUST NOT be used where secure alternatives exist.

---

### `NET-ENC-002` — TLS Inspection

**Classification:** Conditional Requirement  
**Strength:** MUST when organizational policy requires  
**Owner:** Security / Platform

TLS inspection MUST only be implemented where required by organizational security policy and supported by the application and platform design.

Do not make TLS inspection mandatory solely because the central firewall supports it.

---

## 18. Resiliency and Security Availability

### `NET-RES-001` — Critical Security Dependency Identification

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Joint

Critical security and network dependencies MUST be identified.

Examples include:

- central firewall;
- DNS;
- gateways;
- ingress controls;
- hybrid connectivity;
- inspection appliances;
- monitoring platform.

---

### `NET-RES-002` — Security Control Availability

**Classification:** Mandatory Zero Trust Baseline  
**Strength:** MUST  
**Owner:** Platform / Security

A failure of a security control MUST NOT silently result in uncontrolled bypass where the architecture is intended to fail closed.

Any fail-open behaviour MUST be explicitly documented, justified, and approved.

---

### `NET-RES-003` — Required Redundancy

**Classification:** Conditional Requirement  
**Strength:** MUST  
**Owner:** Joint

Where availability requirements exist, network and security controls MUST provide an appropriate level of redundancy.

Do not invent HA or DR requirements that are not documented.

---

## 19. Required Security Traffic Flows

Only include flows that apply to the workload.

### Internet Egress

```text
Workload
   ↓
Approved routing
   ↓
Central Firewall / Approved NVA
   ↓
Internet
```

### Private PaaS

```text
Application
   ↓
Private Endpoint
   ↓
Azure PaaS Service
```

### Approved Public Ingress

Where public ingress is required:

```text
Internet
   ↓
Approved Edge / WAF / Ingress Control
   ↓
Workload
```

### Hybrid Connectivity

Where hybrid connectivity is required:

```text
External Network
   ↓
Approved Hybrid Connectivity
   ↓
Central Azure Connectivity Platform
   ↓
Authorized Workload Destination
```

---

## 20. Prohibited Security Traffic Flows

### Direct Internet Egress Bypass

```text
Workload -> Internet directly
```

where centralized inspection is required.

### Direct Administrative Exposure

```text
Internet -> RDP / SSH / privileged management port -> Workload
```

### Public Backend PaaS Bypass

```text
Application -> Public PaaS Endpoint
```

where private-only connectivity is required.

### Unrestricted East-West Access

```text
Compromised Workload Segment -> Unrelated Workload Networks
```

without an explicit authorized communication requirement.

### Unauthorized Platform Modification

```text
Workload Terraform -> Platform-owned security / connectivity resources
```

without explicit authority.

---

## 21. Ownership and Security Responsibility

### Workload Team

May own:

- workload VNet;
- workload subnets;
- workload NSGs;
- workload route tables;
- workload Private Endpoints;
- workload PaaS network controls;
- workload-side DNS integration.

### Platform Team

May own:

- connectivity hub;
- Virtual WAN;
- Azure Firewall;
- NVA;
- ExpressRoute;
- VPN gateway;
- DNS resolver;
- shared Private DNS;
- central monitoring infrastructure.

### Security Team

May own or govern:

- firewall policy;
- WAF policy;
- Internet exposure approvals;
- exception approvals;
- monitoring and detection requirements;
- Zero Trust network standards;
- incident-response requirements.

### Operations Team

May own:

- network monitoring;
- alerting;
- connectivity health;
- operational response.

Ownership MUST be derived from the organization's operating model.

A platform dependency MUST NOT be interpreted as permission for a workload repository to modify the platform resource.

---

## 22. Terraform / IaC Security Guardrails

Implementation agents and engineers:

- MUST treat this document as the network-security architecture contract.
- MUST preserve Zero Trust baseline requirements.
- MUST NOT invent missing network values.
- MUST NOT create direct Internet bypass routes.
- MUST NOT weaken NSGs for deployment convenience.
- MUST NOT enable public PaaS access to troubleshoot Private Endpoint issues.
- MUST NOT expose administrative ports publicly without approved exception.
- MUST NOT recreate centrally managed firewalls, gateways, DNS, or inspection services.
- MUST NOT modify platform-owned security resources without authority.
- MUST NOT introduce broad `Any -> Any` rules without explicit justification.
- MUST preserve valid return paths through stateful security controls.
- MUST NOT silently convert platform dependencies into workload-managed Terraform resources.
- MUST surface unresolved security dependencies before implementing speculative infrastructure.

The correct response to missing critical information is:

`Required Security / Platform Confirmation`

not invention.

---

## 23. Validation and Security Acceptance Tests

A successful:

```text
terraform apply
```

does NOT prove that the network is secure.

Validation MUST test resulting Azure behaviour.

### Segmentation

Validate:

- prohibited east-west paths fail;
- authorized flows succeed;
- unrelated workload segments cannot communicate without explicit authorization.

### Routing

Validate:

- effective routes;
- expected next hop;
- route-table associations;
- central inspection path;
- return paths;
- absence of direct Internet bypass.

### Firewall

Validate:

- expected traffic traverses the firewall;
- required traffic is allowed;
- prohibited traffic is denied;
- firewall policy ownership is preserved.

### Public Exposure

Validate:

- internal workloads have no unintended public ingress;
- administrative ports are not publicly reachable;
- only approved public endpoints are exposed.

### Private PaaS

Validate:

- Private Endpoint exists where required;
- DNS resolves to private IP;
- connectivity succeeds privately;
- public access fails where prohibited.

### DNS

Validate:

- private FQDNs resolve correctly;
- enterprise forwarding works where required;
- no unintended public fallback occurs.

### Hybrid

Where applicable, validate:

- required hybrid connectivity;
- least-privilege route availability;
- return path;
- inspection path;
- no unintended broad trust.

### Monitoring

Validate:

- required logs are generated;
- telemetry reaches the approved monitoring destination;
- critical alerts exist;
- security operations can investigate relevant traffic.

### Encryption

Validate:

- sensitive network traffic uses approved encrypted protocols;
- insecure administrative protocols are not exposed.

---

## 24. Security Exceptions

Any deviation from a Mandatory Zero Trust Baseline requirement MUST be:

1. explicitly documented;
2. risk assessed;
3. approved by the appropriate security authority;
4. time bounded where appropriate;
5. traceable to an owner;
6. accompanied by compensating controls where required.

An implementation convenience is not a security exception.

---

## 25. Open Questions / Required Confirmations

Typical confirmations may include:

- approved Azure region;
- workload address space;
- subnet ranges;
- central connectivity resource;
- firewall / NVA next-hop address;
- firewall policy ownership;
- approved ingress architecture;
- hybrid connectivity requirement;
- DNS architecture;
- Private DNS ownership;
- backend services requiring Private Endpoints;
- security classification;
- DDoS requirement;
- monitoring destination;
- SIEM integration;
- administrative access model;
- availability requirements;
- approved security exceptions.

Do not fabricate these values.

---

## 26. Assessment Interpretation

### Requirement Met

Evidence demonstrates that an applicable security requirement is satisfied.

### Requirement Violation

The implementation conflicts with an applicable mandatory requirement.

### Best-Practice Recommendation

The implementation is not violating a mandatory requirement, but a security improvement is recommended.

### Unable to Validate

The requirement applies, but evidence is insufficient.

### Not Applicable

The requirement does not apply to the workload.

### External Dependency

Compliance depends on infrastructure or configuration outside the assessment scope.

### Positive Finding

The implementation demonstrates a strong, evidence-supported Zero Trust network control.

---

## 27. Final Zero Trust Security Standard

The network design MUST allow an architect, security reviewer, or assessment agent to answer without guessing:

- What is the workload's approved network boundary?
- What central connectivity platform is used?
- Which traffic is explicitly allowed?
- Which traffic is explicitly denied?
- What prevents lateral movement?
- How is Internet egress inspected?
- What prevents firewall bypass?
- How is public ingress controlled?
- Which resources are intentionally public?
- Which backend services are private-only?
- How are Private Endpoints resolved?
- How is administrative access controlled?
- How are hybrid networks prevented from becoming implicitly trusted?
- How are security events observed?
- Which logs and alerts exist?
- Which controls limit blast radius?
- Which shared security controls are platform owned?
- Which exceptions exist and who approved them?
- How will the implemented network prove that Zero Trust controls actually work?

Where the available information does not support a safe security decision, implementation MUST request confirmation rather than inventing one.
