# Current Architecture

The repository currently defines:

- Hub VNet: `10.10.0.0/16`
- Application spoke VNet: `10.20.0.0/16`
- Application subnet: `10.20.1.0/24`
- Private Endpoint subnet: `10.20.2.0/24`
- Management subnet: `10.20.3.0/24`
- Storage Account
- Storage Blob Private Endpoint
- Azure Key Vault
- NSGs
- Route table
- Private DNS zone for Azure Blob Storage

The hub's shared Azure Firewall, ExpressRoute, and enterprise DNS components are managed by another platform team and are therefore not created by this Terraform.

Use `network-requirements.md` as the intended target state when reviewing the implementation.
