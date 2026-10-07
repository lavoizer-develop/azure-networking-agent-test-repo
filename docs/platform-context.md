# Platform Context

This file provides optional human-readable context about shared Azure Landing Zone services that are outside the workload repository.

The workload is expected to consume centrally managed platform capabilities rather than recreate them.

Examples may include:

- central Azure connectivity platform
- Azure Firewall or another approved central inspection layer
- enterprise DNS services
- hybrid connectivity services where applicable
- central monitoring and security services
- shared Private DNS zones
- shared ingress or connectivity services

This file is not the only permitted source of platform context.

Platform information may also be discovered from:

- Terraform variables or tfvars
- Terraform data sources
- Terraform remote-state outputs
- environment-specific configuration
- deployment pipeline inputs
- another platform repository
- approved architecture documentation
- authenticated live Azure discovery

When multiple sources exist, prefer authoritative machine-readable or live configuration for current environmental values while preserving documented ownership and architectural intent.

If required platform information cannot be validated, classify it as:

`External Dependency — validation required`

or:

`Unable to Validate`

Do not invent missing platform values.
