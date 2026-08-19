---
name: azure-networking
description: Azure networking architecture, security, connectivity, routing, Private Link, DNS, hybrid connectivity, and resiliency review guidance. Use for Azure network design, assessment, troubleshooting, or infrastructure reviews.
---

# Azure Networking Review Skill

Use this skill when evaluating Azure networking architecture or implementation.

The purpose of this skill is technical analysis. Reporting layout and dashboard formatting are handled separately.

## Review Principles

1. Establish the documented target state before identifying gaps.
2. Validate documentation against the actual infrastructure implementation.
3. Base findings on repository evidence whenever possible.
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

# Finding Evidence

Every finding should include evidence such as:

- file path
- Terraform/Bicep resource
- relevant property
- documented requirement
- missing configuration confirmed by repository search

If evidence is unavailable, classify the item as an assumption or validation requirement rather than a confirmed defect.

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

## Medium

Use for issues that:

- create operational risk
- leave network controls incomplete
- create resiliency concerns
- partially violate requirements
- should be remediated but do not create immediate severe impact

## Low

Use for:

- maintainability improvements
- consistency improvements
- documentation gaps
- low-impact best-practice improvements

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
