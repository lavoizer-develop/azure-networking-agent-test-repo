---
name: assessment-reporting
description: Creates concise dashboard-style Markdown assessment reports with executive summaries, scorecards, prioritized findings, compliance matrices, remediation plans, architecture diagrams, positive findings, and assumptions. Use when an agent must produce a formal technical assessment artifact.
---

# Assessment Reporting Skill

Use this skill when creating a persistent technical assessment or recommendation report.

The report should be easy to review directly in GitHub or VS Code Markdown Preview.

The specialist agent or specialist skill determines the technical findings. This skill determines how those findings are organized and presented.

# Reporting Principles

1. Keep the report concise and evidence-based.
2. Put the most important information near the top.
3. Use tables for scorecards, compliance, and remediation planning.
4. Use detailed prose only where it improves understanding.
5. Distinguish confirmed findings from assumptions.
6. Include positive findings as well as deficiencies.
7. Keep severity counts internally consistent.
8. Make recommendations actionable.
9. Do not use decorative formatting that reduces readability.
10. Do not duplicate the same finding in multiple severity sections.

# Required Report Structure

## 1. Assessment Header

Start with a clear title appropriate to the assessment.

For Azure networking use:

# Azure Networking Assessment Dashboard

Then include:

> **Assessment Status:** <Critical / Action Required / Improvements Recommended / Healthy>  
> **Environment:** <environment if known, otherwise Unknown>  
> **Azure Region:** <region if known, otherwise Unknown>  
> **Assessment Scope:** <scope>  
> **Last Assessment:** <current date>

## 2. Executive Summary

Provide a concise 3–5 sentence summary covering:

- overall posture
- most important risks
- alignment with documented requirements
- highest-priority remediation theme

Do not repeat every detailed finding.

## 3. Assessment Overview

Use a simple summary table.

For example:

| Metric | Result |
|---|---:|
| Critical Findings | <count> |
| High Findings | <count> |
| Medium Findings | <count> |
| Low Findings | <count> |
| Requirements Met | <count> |
| Requirements Partially Met | <count> |
| Requirements Not Met | <count> |

Only include requirement metrics when documented requirements exist.

## 4. Assessment Scorecard

Create a scorecard using categories relevant to the specialist assessment.

For an Azure networking assessment, use:

| Area | Status | Critical | High | Medium | Low |
|---|---|---:|---:|---:|---:|
| Network Topology | ✅ / ⚠️ / ❌ | 0 | 0 | 0 | 0 |
| Routing & Egress | ✅ / ⚠️ / ❌ | 0 | 0 | 0 | 0 |
| Network Security | ✅ / ⚠️ / ❌ | 0 | 0 | 0 | 0 |
| Private Connectivity | ✅ / ⚠️ / ❌ | 0 | 0 | 0 | 0 |
| DNS | ✅ / ⚠️ / ❌ | 0 | 0 | 0 | 0 |
| Hybrid Connectivity | ✅ / ⚠️ / ❌ | 0 | 0 | 0 | 0 |
| Resiliency | ✅ / ⚠️ / ❌ | 0 | 0 | 0 | 0 |

Use:

- ✅ Healthy / aligned
- ⚠️ Improvement required
- ❌ Significant issue

Ensure the counts match the detailed findings.

# Priority Findings

Order findings by:

1. severity
2. technical/business impact
3. remediation dependency

Use a short domain prefix for finding IDs.

For Azure networking use:

- `NET-001`
- `NET-002`
- `NET-003`

Organize findings under:

## 🔴 Critical Findings
## 🟠 High Findings
## 🟡 Medium Findings
## 🔵 Low Findings

If a severity has no findings, explicitly state that no findings were identified at that severity.

For each finding use:

### NET-XXX — <Finding Title>

**Area:**  
<assessment area>

**Evidence:**  
`<file path>` — `<resource, setting, or documented requirement>`

**Observed State:**  
<what repository evidence shows>

**Expected State:**  
<what documented requirements or architecture expect>

**Risk:**  
<technical or business impact>

**Recommendation:**  
<specific remediation guidance>

**Dependencies / Considerations:**  
<validation or coordination needed before remediation>

# Architecture Observations

Summarize the architecture discovered from repository evidence.

Clearly distinguish:

**Observed in repository**

from:

**Assumed external/shared platform dependency**

Do not present assumptions as confirmed architecture.

# Architecture Diagram

When the architecture can be reliably determined, create a Mermaid diagram representing the actual discovered environment.

Only include resources and connections supported by:

- repository evidence
- architecture documentation
- clearly labeled assumptions

Do not invent architecture components or connectivity paths.

Keep the Mermaid diagram simple enough to render reliably in GitHub and VS Code.

# Requirements Compliance

When documented requirements exist, create a compliance matrix.

Use:

| ID | Requirement | Status | Evidence | Notes |
|---|---|---|---|---|
| REQ-001 | <requirement> | ✅ Met / ⚠️ Partial / ❌ Not Met / ❓ Unable to Validate | `<file/resource>` | <notes> |

If the source requirements do not have IDs, assign sequential IDs only for reporting purposes.

Use:

- ✅ Met
- ⚠️ Partially Met
- ❌ Not Met
- ❓ Unable to Validate

Do not mark a requirement as met without evidence.

# Recommended Remediation Plan

Create an actionable backlog.

Use:

| Priority | Finding | Recommendation | Area | Effort | Impact |
|---|---|---|---|---|---|
| P1 | NET-XXX | <action> | <area> | Low / Medium / High | High |
| P2 | NET-XXX | <action> | <area> | Low / Medium / High | High |
| P3 | NET-XXX | <action> | <area> | Low / Medium / High | Medium |

Prioritize based on:

1. security exposure
2. broken mandatory functionality
3. documented requirement violations
4. dependency order
5. operational impact
6. implementation effort

Do not prioritize solely by ease of implementation.

# Positive Findings

Include correctly implemented architecture or controls when supported by evidence.

This ensures the assessment describes the overall posture rather than only failures.

# Assumptions & Validation Required

For anything that cannot be conclusively validated, use:

### ASSUMPTION-XXX — <Title>

**Reason:**  
<why available evidence is insufficient>

**Validation Required:**  
<what should be checked and where>

Never present assumptions as confirmed facts.

# Assessment Summary

Finish with:

**Overall Status:** <status>

**Findings**

- Critical: <count>
- High: <count>
- Medium: <count>
- Low: <count>

**Top Three Priority Actions**

1. <action>
2. <action>
3. <action>

**Next Step**

Provide one concise recommended next action.

# Quality Checks

Before completing the report, verify:

1. The complete assessment has been written to the requested file.
2. Every confirmed finding has evidence.
3. Assumptions are labeled as assumptions.
4. Finding counts are internally consistent.
5. Severity classifications are reasonable.
6. Compliance status agrees with the detailed findings.
7. Recommendations are actionable.
8. Markdown tables are valid.
9. Mermaid syntax is valid when a diagram is included.
10. Sensitive values are not copied unnecessarily into the report.
11. Positive findings are included where appropriate.
12. The report is readable in GitHub and VS Code Markdown Preview.
