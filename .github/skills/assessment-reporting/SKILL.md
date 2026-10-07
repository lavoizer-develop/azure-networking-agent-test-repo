---
name: assessment-reporting
description: Produces a compact structured assessment JSON that is rendered deterministically into professional Markdown and HTML reports. Use only after technical findings are finalized.
---

# Assessment Reporting Skill

Use this skill only after the technical assessment and findings are finalized.

The agent must create one structured source of truth:

`docs/assessments/network-assessment.json`

Do not independently write the Markdown or HTML assessment.

The repository renderer converts the JSON into:

- `docs/assessments/network-recommendations.md`
- `docs/assessments/network-recommendations.html`

This avoids duplicated model output and guarantees report consistency.

# Reporting Principles

The structured assessment must be:

- concise
- evidence based
- deduplicated
- implementation oriented
- suitable for engineering review
- suitable for executive dashboard rendering

Do not repeat the same finding in multiple fields.

Do not copy full Terraform blocks or large source excerpts.

Use short evidence descriptions with precise file references.

# Required JSON Shape

Create valid JSON using this structure:

```json
{
  "schema_version": "1.0",
  "assessment": {
    "title": "Azure Networking Assessment",
    "overall_status": "Action Required",
    "scope": "Repository IaC assessment",
    "environment": "Unknown",
    "region": "Unknown",
    "assessment_date": "YYYY-MM-DD",
    "live_azure_validation": false,
    "executive_summary": "Concise 3-5 sentence summary."
  },
  "scorecard": [
    {
      "area": "Routing & Egress",
      "status": "Action Required",
      "summary": "Short status explanation."
    }
  ],
  "architecture": {
    "summary": "Short architecture summary.",
    "components": [
      "Workload VNet",
      "Central inspection layer"
    ],
    "flows": [
      {
        "name": "Internet egress",
        "path": [
          "Workload",
          "Central Firewall",
          "Internet"
        ],
        "status": "Expected"
      }
    ]
  },
  "findings": [
    {
      "id": "NET-001",
      "requirement_id": "NET-FW-002",
      "severity": "High",
      "area": "Routing & Egress",
      "title": "Short finding title",
      "priority": "P1",
      "evidence": [
        {
          "source": "infra/routing.tf",
          "detail": "Concise evidence statement."
        }
      ],
      "observed_state": "What was observed.",
      "expected_state": "What the requirement expects.",
      "risk": "Why this matters.",
      "recommendation": "Specific remediation.",
      "dependencies": []
    }
  ],
  "requirement_compliance": [
    {
      "requirement_id": "NET-FW-002",
      "status": "Not Met",
      "evidence": "infra/routing.tf",
      "notes": "Short compliance note."
    }
  ],
  "positive_findings": [
    {
      "title": "Positive control",
      "evidence": "Concise supporting evidence."
    }
  ],
  "assumptions": [
    {
      "id": "ASM-001",
      "topic": "External firewall policy",
      "detail": "Policy is platform managed and not present in this repository.",
      "validation_required": "Confirm required rules with the platform team."
    }
  ]
}
```

# Field Rules

## `assessment`

Required.

`overall_status` should normally be one of:

- Healthy
- Improvement Recommended
- Action Required
- Critical Action Required

`environment` and `region` should be `Unknown` when they cannot be established safely.

Do not invent them.

`live_azure_validation` must be `true` only when live Azure state was actually queried successfully.

## `scorecard`

Keep this compact.

Use only relevant assessment domains.

Typical Azure Networking domains include:

- Network Topology
- Routing & Egress
- Network Security
- Private Connectivity
- DNS
- Hybrid Connectivity
- Monitoring & Observability
- Resiliency

Do not create scorecard rows for obviously irrelevant domains.

## `architecture`

Keep this high level.

`components` should list important architecture components, not every resource.

`flows` should describe only material paths such as:

- Internet egress
- public ingress
- hybrid connectivity
- Private Endpoint access
- shared-service connectivity

Do not invent components or flows.

If architecture cannot be determined reliably, use an empty component or flow list and explain the limitation in `summary`.

## `findings`

Findings are the primary technical output.

Allowed severity values:

- Critical
- High
- Medium
- Low

Each finding must represent a distinct root cause.

Do not create separate findings merely to repeat the same issue across multiple report sections.

`requirement_id` should reference the applicable target-state requirement whenever possible.

`priority` should normally be:

- P1
- P2
- P3
- P4

Use P1 only for the most urgent remediation.

Evidence must be concise.

Example:

```json
{
  "source": "infra/routing.tf",
  "detail": "The default route uses Internet as the next hop instead of the required central inspection layer."
}
```

Do not paste full source blocks.

## `requirement_compliance`

Include applicable requirements that materially help the assessment.

Allowed status values:

- Met
- Partially Met
- Not Met
- Unable to Validate
- Not Applicable
- External Dependency

Do not duplicate the complete requirement text.

Reference the requirement ID and provide a short compliance note.

## `positive_findings`

Include only evidence-backed strengths.

Keep each item concise.

## `assumptions`

Use assumptions only where evidence is insufficient.

Do not present assumptions as confirmed facts.

# Derived Information

Do NOT manually add severity counts.

The renderer derives:

- Critical count
- High count
- Medium count
- Low count

Do NOT duplicate a separate remediation plan unless a remediation cannot be represented by the corresponding finding.

The renderer derives the prioritized remediation view from finding priorities and recommendations.

Do NOT create separate top-priority fields.

The renderer derives the top actions from P1/P2/P3 findings.

# Token Efficiency

Use short, factual strings.

Prefer:

`"evidence": "infra/routing.tf"`

over repeating file contents.

Prefer one root-cause finding with several concise evidence entries over several repetitive findings.

Do not repeat:

- severity counts
- complete requirement text
- identical recommendations
- the executive summary inside individual findings
- the same evidence in several sections

The JSON is an assessment data model, not prose documentation.

# Validation Before Rendering

Before running the renderer, verify:

1. JSON syntax is valid.
2. `schema_version` is `1.0`.
3. Every finding has a unique ID.
4. Every finding has a valid severity.
5. Requirement IDs are correct when supplied.
6. Finding evidence is present.
7. Recommendations are actionable.
8. Confirmed findings are separated from assumptions.
9. Live Azure validation is not claimed unless it actually occurred.
10. No secrets, credentials, tokens, or unnecessary sensitive identifiers are included.

After validation, run the repository renderer.

Do not manually edit the generated Markdown or HTML.
