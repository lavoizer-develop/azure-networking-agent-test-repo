---
name: azure-networking
description: Azure networking architecture, security, connectivity, routing, Private Link, DNS, hybrid connectivity, resiliency, monitoring, and observability review guidance. Use for Azure network design, assessment, troubleshooting, or infrastructure reviews.
---

# Azure Networking Review Skill

Use this skill when evaluating Azure networking architecture or implementation.

The purpose of this skill is technical analysis. Reporting layout and dashboard formatting are handled separately.

## Review Principles

1. Establish the documented target state before identifying gaps.
2. Validate documentation against the actual infrastructure implementation.
3. Base findings on available evidence, prioritizing repository Infrastructure as Code and authenticated live Azure state where appropriate.
4. Clearly separate:
   - observed facts
   - documented requirements
   - assumptions
   - external/shared platform dependencies
5. Do not classify something as incorrect merely because another architecture could also work.
6. Respect documented architecture decisions unless they:
   - violate a documented requirement
   - create a clear security or connectivity risk
   - prevent the required solution from functioning
7. Identify positive implementation decisions as well as deficiencies.
8. Recommend practical remediation rather than generic best-practice statements.
9. Assess operational visibility separately from architecture correctness.

A network may be correctly designed but still create operational risk if failures, traffic patterns, routing issues, security events, or connectivity degradation cannot be detected and investigated.

Do not treat the existence of Azure Monitor, Network Watcher, or Log Analytics alone as sufficient monitoring. Validate that relevant telemetry is actually collected, centralized, queryable, and, where required, alerted on.

## Evidence Sources

Use the following evidence sources according to their purpose.

### Target-State Evidence

Use:

- `docs/network-requirements.md`
- approved architecture documentation
- security standards
- explicit user-supplied requirements

Target-state evidence defines what SHOULD exist.

### Implementation Evidence

Use:

- Terraform
- Bicep
- ARM templates
- variables and tfvars
- outputs
- data sources
- remote-state references
- deployment configuration

Implementation evidence defines what the repository INTENDS to deploy.

### Live Azure Evidence

When authenticated Azure discovery is available, use it to validate what ACTUALLY exists.

Relevant live evidence may include:

- VNets
- subnets
- peerings
- route tables
- routes
- firewall resources
- Private Endpoints
- Private DNS
- public IPs
- ingress components
- hybrid connectivity resources
- diagnostic settings
- monitoring configuration

Do not treat live Azure state as the target-state authority.

If live Azure differs from Infrastructure as Code, record possible configuration drift and assess the difference against the documented target state.

### Platform Context

Shared platform facts may come from:

- `docs/platform-context.md`
- another platform repository
- platform outputs
- Terraform data sources
- remote state
- live Azure discovery
- approved platform documentation

Do not require a specific `platform-context.md` file.

If platform information remains unavailable, classify it as:

`External Dependency — validation required`

or:

`Unable to Validate`

Do not invent missing platform state.

## Live Azure Discovery Guidance

When live Azure discovery tools are available:

1. Inspect the repository first.
2. Identify the specific deployed-state or platform question requiring validation.
3. Query only the relevant Azure scope and resource types.
4. Correlate discovered resources with repository configuration.
5. Record the evidence used.
6. Detect configuration drift where repository intent and deployed state differ.

Prefer targeted discovery over broad subscription- or tenant-wide enumeration.

Live discovery is read-only assessment evidence.

Do not create, modify, or delete Azure resources as part of a normal assessment.

# Technical Review Areas

## 1. Network Topology

Review:

- hub-and-spoke design
- Azure Virtual WAN where present
- VNet relationships
- workload isolation
- shared-services placement
- connectivity between platform and workload networks
- whether references point to the intended existing platform resources

Check for:

- missing connectivity
- accidental duplicate platform resources
- unintended standalone VNets
- incorrect peering targets
- unsupported transitive-routing assumptions

## 2. IP Addressing and Subnets

Review:

- VNet address spaces
- subnet address ranges
- overlapping CIDRs
- subnet purpose
- future growth
- hybrid connectivity conflicts
- appropriate separation of workloads, management, and Private Endpoints

Do not recommend CIDR changes without evidence that addressing is problematic.

## 3. VNet Peering

Review:

- required peering in both directions
- `allow_virtual_network_access`
- forwarded traffic requirements
- gateway transit
- remote gateway usage
- cross-subscription or cross-resource-group dependencies
- relationships with hub firewall, DNS, VPN, or ExpressRoute components

Remember that peering configuration is directional.

## 4. Routing and Egress

Review:

- route tables
- User Defined Routes
- default routes
- next-hop type
- next-hop IP
- route-table associations
- route propagation
- forced tunneling
- return-path requirements
- asymmetric-routing risks

Where centralized inspection is required, confirm that traffic is actually routed through the required Azure Firewall, NVA, or other inspection layer.

Do not assume that the existence of a firewall means workloads are using it.

## 5. Azure Firewall

When Azure Firewall is present or documented as an external dependency, assess:

- intended placement
- routing to the firewall
- return path
- forwarded traffic
- required policies
- DNS dependencies where relevant
- whether the firewall is repository-managed or externally managed

Treat externally managed firewall configuration as an assumption unless its configuration is available in the repository.

## 6. Network Security Groups

Review:

- Internet-sourced inbound rules
- broad source prefixes
- broad destination prefixes
- exposed management ports
- RDP and SSH
- required application ingress
- subnet-level segmentation
- least-privilege intent

Do not claim that an NSG rule alone makes a resource publicly reachable if no public ingress path exists.

Instead, describe the exposure risk accurately.

## 7. Private Endpoints

Review:

- whether Private Endpoints are required by documented architecture
- correct target resource
- correct subresource
- correct subnet placement
- public network access state
- associated DNS configuration
- connectivity from workload networks
- connectivity from hybrid/on-premises networks where required

A Private Endpoint does not automatically guarantee private-only access if the service's public endpoint remains enabled.

## 8. Private DNS

Review:

- required Private DNS zones
- Private DNS zone groups
- VNet links
- hub DNS integration
- spoke DNS integration
- hybrid name resolution
- conditional forwarding requirements
- Azure DNS Private Resolver dependencies
- externally managed DNS forwarders

For Private Endpoint scenarios, validate both:

1. private IP connectivity
2. name resolution to the private IP

Treat these as separate requirements.

## 9. Hybrid Connectivity

Review:

- ExpressRoute dependencies
- VPN dependencies
- gateway transit
- route propagation
- hub connectivity
- DNS forwarding
- access from on-premises networks
- access to Private Endpoints
- return paths

When ExpressRoute, VPN gateways, or enterprise DNS are managed outside the repository, record them as external dependencies rather than assuming their configuration.

## 10. Public Network Exposure

Review public-network settings for Azure PaaS resources relevant to the network architecture.

Examples include:

- Storage Accounts
- Key Vault
- SQL
- App Service
- Functions
- Container registries
- other Private Link-capable PaaS services

Compare the public-network state against documented requirements.

Do not apply a blanket "public access must always be disabled" rule unless the architecture or security requirements call for it.

## 11. Inbound Connectivity

Review:

- public IP exposure
- load balancers
- Application Gateway
- Front Door
- reverse proxies
- Private Link
- NSGs
- firewall rules
- approved source networks

Confirm that inbound paths align with documented architecture.

## 12. Outbound Connectivity

Review:

- Azure Firewall
- NAT Gateway
- direct Internet egress
- platform SNAT
- route tables
- forced tunneling
- inspection requirements
- service endpoints or Private Endpoints where relevant

Confirm that the actual egress path matches the intended design.

## 13. Resiliency

Assess networking resiliency when evidence is available.

Consider:

- zone-redundant services
- redundant gateways
- firewall architecture
- dependency on a single network appliance
- DNS resiliency
- hybrid connectivity redundancy
- route failover
- critical shared-service dependencies

Do not invent resiliency requirements that are not documented.

## 14. Monitoring and Observability

Assess whether the network provides sufficient visibility for operations, troubleshooting, security investigation, performance analysis, and incident response.

Monitoring should be evaluated against the architecture and the importance of the network path. Do not require every possible diagnostic setting when there is no documented operational need.

### Network Flow Visibility

Review:

- Virtual Network flow logs
- Traffic Analytics where appropriate
- storage and retention of flow telemetry
- visibility into allowed and denied traffic
- visibility across important workload networks
- whether flow-log configuration covers networks that require investigation
- whether flow telemetry is centralized or accessible to the operational team

Prefer Virtual Network flow logs for new implementations.

Do not recommend creation of new NSG flow logs.

If existing NSG flow logs are discovered, identify migration to Virtual Network flow logs as an operational consideration.

### Azure Firewall Monitoring

When Azure Firewall is present, review:

- diagnostic settings
- Log Analytics integration
- network rule logs
- application rule logs
- NAT rule logs where applicable
- threat intelligence logs
- IDPS logs where applicable
- DNS proxy/query logs where relevant
- firewall platform metrics
- alerting for meaningful health or operational conditions

Where Log Analytics is used, prefer resource-specific Azure Firewall tables when appropriate rather than relying only on the legacy `AzureDiagnostics` table.

Do not assume Azure Firewall logging is enabled simply because the firewall exists.

### Connectivity Monitoring

For important connectivity paths, assess whether continuous or periodic reachability monitoring is appropriate.

Examples include:

- spoke-to-hub connectivity
- workload-to-shared-services connectivity
- workload-to-Private-Endpoint connectivity
- Azure-to-on-premises connectivity
- on-premises-to-Azure connectivity
- connectivity through Azure Firewall or an NVA
- connectivity to critical application endpoints

Where appropriate, consider Azure Network Watcher Connection Monitor or an equivalent monitoring mechanism.

Review whether monitoring can detect:

- loss of reachability
- increased latency
- packet loss
- degradation of important network paths

Do not require Connection Monitor for every network path.

Prioritize business-critical and operationally important connectivity.

### Hybrid Connectivity Monitoring

Where ExpressRoute or VPN is used, review monitoring for:

- connection health
- gateway health
- tunnel state
- BGP/session health where observable
- traffic levels
- connectivity degradation
- redundancy/failover paths
- loss of hybrid reachability

If hybrid connectivity is externally managed, identify monitoring responsibility as an external dependency when its configuration cannot be validated.

### DNS Monitoring

Where DNS is a critical dependency, review operational visibility for:

- DNS resolution failures
- Private DNS integration
- DNS forwarding failures
- Azure DNS Private Resolver where present
- enterprise DNS dependencies
- DNS query logging where supported and operationally required

Do not assume that successful Private Endpoint creation proves DNS is operating correctly.

### Platform Diagnostic Settings

Review diagnostic settings for network resources where operational visibility is required.

Examples may include:

- Azure Firewall
- Application Gateway
- VPN Gateway
- ExpressRoute Gateway
- NAT Gateway
- Azure DNS Private Resolver
- Front Door
- Load Balancer
- network security and connectivity services

Determine whether logs and metrics are sent to an appropriate destination such as:

- Log Analytics
- Storage
- Event Hub
- an approved SIEM or monitoring platform

Do not require every diagnostic category by default.

The selected telemetry should support the documented operational, security, troubleshooting, and retention requirements.

### Metrics and Alerting

Assess whether meaningful network conditions have monitoring and alerting.

Examples include:

- connectivity loss
- gateway or tunnel health degradation
- firewall health
- unusual traffic patterns
- packet loss
- latency degradation
- capacity or throughput concerns
- resource health events
- failure of important network dependencies

Distinguish between:

1. telemetry being collected
2. telemetry being queried
3. meaningful alerting being configured

The existence of logs does not mean the environment is actively monitored.

### Centralized Monitoring

Where a centralized operational model is expected, review:

- Log Analytics workspace integration
- central monitoring architecture
- cross-subscription visibility
- retention requirements
- access to monitoring data
- SIEM integration where relevant
- separation of platform and workload monitoring responsibilities

If the monitoring platform is managed outside the repository, record it as an external dependency rather than marking monitoring as absent without evidence.

### Network Troubleshooting Capability

Assess whether operators have sufficient capability to diagnose incidents.

Consider:

- Network Watcher
- Connection Monitor
- IP flow verification
- next-hop validation
- effective routes
- effective NSG rules
- packet capture where appropriate
- VPN troubleshooting
- flow logs
- Traffic Analytics

These capabilities do not all need to be permanently configured.

Differentiate between:

- continuous monitoring controls
- diagnostic capabilities used during troubleshooting

### Monitoring Evidence

Monitoring findings should reference evidence such as:

- diagnostic setting resources
- Terraform diagnostic-setting configuration
- flow-log resources
- Log Analytics workspace references
- Azure Monitor alert rules
- Connection Monitor resources
- monitoring requirements in documentation
- missing monitoring configuration confirmed by repository search

If monitoring may be implemented outside the repository, classify it as `Unable to Validate` or as an external dependency rather than a confirmed defect.

# Finding Evidence

Every finding should include evidence such as:

- requirement ID
- file path
- Terraform/Bicep resource
- relevant property
- documented requirement
- missing configuration confirmed by repository search
- live Azure resource or property when authenticated discovery was performed
- difference between repository intent and deployed Azure state where drift was detected

If evidence is unavailable, classify the item as an assumption or validation requirement rather than a confirmed defect.

# Configuration Drift

When authenticated live Azure discovery is available, compare deployed state with repository Infrastructure as Code.

Examples of potential drift include:

- deployed route differs from Terraform
- missing or additional peering
- public network access differs from declared configuration
- Private Endpoint exists in only one evidence source
- DNS links differ from repository intent
- diagnostic settings differ from IaC
- network-security configuration changed outside the repository

Configuration drift is not automatically a defect.

Assess the deployed difference against the target-state requirements.

If repository intent is compliant but deployed state is not, report the deployed drift as a finding.

If deployed state is compliant but repository intent is not, report the repository inconsistency because a future deployment could reintroduce the non-compliant state.

# Severity Guidance

## Critical

Use only for immediate or severe issues such as:

- major unintended Internet exposure
- severe network security exposure
- architecture fundamentally preventing required connectivity
- critical production connectivity failure
- major mandatory requirement violation with significant impact

## High

Use for issues that:

- materially weaken network security
- break an important connectivity requirement
- bypass required traffic inspection
- prevent required private connectivity
- prevent required hybrid connectivity
- create significant DNS or routing failure
- leave critical network paths without required operational visibility when this creates significant incident-response risk

## Medium

Use for issues that:

- create operational risk
- leave network controls incomplete
- create resiliency concerns
- partially violate requirements
- leave important monitoring, diagnostic, or alerting controls incomplete
- should be remediated but do not create immediate severe impact

## Low

Use for:

- maintainability improvements
- consistency improvements
- documentation gaps
- low-impact best-practice improvements
- non-critical monitoring improvements

Do not inflate severity.

# Positive Findings

Capture correctly implemented decisions when supported by evidence, such as:

- sensible address planning
- appropriate subnet separation
- correctly configured Private Endpoints
- correct private DNS integration
- appropriate routing
- appropriate firewall integration
- least-privilege network rules
- correct public-network restrictions
- clear separation of platform and workload responsibilities
- appropriate Virtual Network flow logging
- centralized diagnostic logging
- appropriate Azure Firewall telemetry
- meaningful network health alerts
- monitoring of critical connectivity paths
- appropriate hybrid connectivity monitoring
- suitable telemetry retention
- clear separation of monitoring responsibilities
- repository and deployed Azure network state are aligned
- shared platform dependencies are positively validated through live Azure evidence where available
