# Northwind Expense Application — Network Requirements

## Scenario

Northwind is deploying an internal expense-management application to Azure in **Canada Central**.

A central Azure hub already exists and provides shared enterprise connectivity. The application team owns the workload spoke and its PaaS resources.

## Required target state

### Hub and spoke

- The workload must use a dedicated spoke VNet.
- The application spoke must have functional bidirectional connectivity with the hub.
- The existing central Azure Firewall has private IP **10.10.1.4**.
- Internet-bound workload traffic must be routed through the central Azure Firewall for inspection.

### Hybrid connectivity

- On-premises connectivity terminates in the hub through an existing ExpressRoute implementation managed by the platform team.
- On-premises users and administrators must be able to reach approved application endpoints without traversing the public Internet.

### Azure PaaS connectivity

- Azure Storage and Azure Key Vault must use private connectivity.
- Public network access for those backend PaaS services must be disabled.
- Private Endpoints must be placed in the designated Private Endpoint subnet.

### DNS

- Private Endpoint names must resolve correctly from:
  - the application spoke; and
  - on-premises networks.
- The enterprise DNS forwarding path terminates in the hub.
- Required Azure Private DNS zones must therefore be available to the hub DNS path.

### Network security

- Application subnets must not accept direct inbound connections from the Internet.
- Administrative RDP/SSH access must not be opened directly to the Internet.
- Network rules should follow least privilege.

## Out of scope

The following shared platform components are assumed to exist and are not deployed by this repository:

- ExpressRoute circuit and gateway
- Central Azure Firewall at `10.10.1.4`
- Enterprise DNS forwarders / Azure DNS Private Resolver in the hub
