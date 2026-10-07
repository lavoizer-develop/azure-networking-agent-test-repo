#!/usr/bin/env python3
"""
Render a structured Azure networking assessment into deterministic Markdown and HTML.

Usage:
    python3 scripts/render-assessment.py docs/assessments/network-assessment.json

Outputs are written next to the JSON source:
    network-recommendations.md
    network-recommendations.html

Standard-library only. No network access or external dependencies required.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


SEVERITIES = ("Critical", "High", "Medium", "Low")
SEVERITY_RANK = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
VALID_OVERALL = {
    "Healthy",
    "Improvement Recommended",
    "Action Required",
    "Critical Action Required",
}
VALID_COMPLIANCE = {
    "Met",
    "Partially Met",
    "Not Met",
    "Unable to Validate",
    "Not Applicable",
    "External Dependency",
}
VALID_SCHEMA = "1.0"


class AssessmentError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise AssessmentError(f"Assessment JSON not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssessmentError(
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise AssessmentError("Top-level JSON value must be an object.")

    return data


def require_object(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise AssessmentError(f"`{key}` must be an object.")
    return value


def require_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise AssessmentError(f"`{key}` must be an array.")
    return value


def clean_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip()


def validate(data: dict[str, Any]) -> None:
    if clean_text(data.get("schema_version")) != VALID_SCHEMA:
        raise AssessmentError(
            f"`schema_version` must be `{VALID_SCHEMA}`."
        )

    assessment = require_object(data, "assessment")
    for key in ("title", "overall_status", "executive_summary"):
        if not clean_text(assessment.get(key)):
            raise AssessmentError(f"`assessment.{key}` is required.")

    overall = clean_text(assessment.get("overall_status"))
    if overall not in VALID_OVERALL:
        raise AssessmentError(
            "`assessment.overall_status` must be one of: "
            + ", ".join(sorted(VALID_OVERALL))
        )

    if not isinstance(assessment.get("live_azure_validation", False), bool):
        raise AssessmentError(
            "`assessment.live_azure_validation` must be true or false."
        )

    findings = require_list(data, "findings")
    ids: set[str] = set()

    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            raise AssessmentError(f"`findings[{index - 1}]` must be an object.")

        for key in (
            "id",
            "severity",
            "area",
            "title",
            "observed_state",
            "expected_state",
            "risk",
            "recommendation",
        ):
            if not clean_text(finding.get(key)):
                raise AssessmentError(
                    f"`findings[{index - 1}].{key}` is required."
                )

        finding_id = clean_text(finding["id"])
        if finding_id in ids:
            raise AssessmentError(f"Duplicate finding ID: {finding_id}")
        ids.add(finding_id)

        severity = clean_text(finding["severity"])
        if severity not in SEVERITIES:
            raise AssessmentError(
                f"Finding {finding_id} has invalid severity `{severity}`."
            )

        evidence = finding.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            raise AssessmentError(
                f"Finding {finding_id} must contain at least one evidence item."
            )

        for e_index, evidence_item in enumerate(evidence, start=1):
            if not isinstance(evidence_item, dict):
                raise AssessmentError(
                    f"Finding {finding_id} evidence item {e_index} must be an object."
                )
            if not clean_text(evidence_item.get("source")):
                raise AssessmentError(
                    f"Finding {finding_id} evidence item {e_index} requires `source`."
                )
            if not clean_text(evidence_item.get("detail")):
                raise AssessmentError(
                    f"Finding {finding_id} evidence item {e_index} requires `detail`."
                )

    for item in require_list(data, "requirement_compliance"):
        if not isinstance(item, dict):
            raise AssessmentError(
                "`requirement_compliance` entries must be objects."
            )
        status = clean_text(item.get("status"))
        if status and status not in VALID_COMPLIANCE:
            raise AssessmentError(
                f"Invalid requirement compliance status `{status}`."
            )


def severity_counts(findings: list[dict[str, Any]]) -> Counter:
    counts = Counter(clean_text(item.get("severity")) for item in findings)
    for severity in SEVERITIES:
        counts.setdefault(severity, 0)
    return counts


def priority_number(value: Any) -> int:
    text = clean_text(value).upper()
    match = re.fullmatch(r"P(\d+)", text)
    if not match:
        return 999
    return int(match.group(1))


def sorted_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        findings,
        key=lambda item: (
            priority_number(item.get("priority")),
            SEVERITY_RANK.get(clean_text(item.get("severity")), 99),
            clean_text(item.get("id")),
        ),
    )


def top_priorities(findings: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    return sorted_findings(findings)[:limit]


def md_escape(value: Any) -> str:
    text = clean_text(value)
    return text.replace("|", r"\|").replace("\n", " ")


def h(value: Any) -> str:
    return html.escape(clean_text(value))


def slug(value: Any) -> str:
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "unknown"


def render_markdown(data: dict[str, Any]) -> str:
    assessment = data["assessment"]
    findings = [item for item in data.get("findings", []) if isinstance(item, dict)]
    counts = severity_counts(findings)
    scorecard = data.get("scorecard", [])
    architecture = data.get("architecture", {})
    compliance = data.get("requirement_compliance", [])
    positives = data.get("positive_findings", [])
    assumptions = data.get("assumptions", [])
    priorities = top_priorities(findings)

    lines: list[str] = []

    lines.append(f"# {clean_text(assessment.get('title'), 'Azure Networking Assessment')}")
    lines.append("")
    lines.append("> [!WARNING]" if findings else "> [!NOTE]")
    lines.append(f"> **Overall Status: {clean_text(assessment.get('overall_status'))}**")
    lines.append(">")
    lines.append(
        f"> {counts['Critical']} Critical · {counts['High']} High · "
        f"{counts['Medium']} Medium · {counts['Low']} Low"
    )
    lines.append("")

    lines.append("## Assessment Context")
    lines.append("")
    lines.append("| Attribute | Value |")
    lines.append("|---|---|")
    for label, key in (
        ("Scope", "scope"),
        ("Environment", "environment"),
        ("Region", "region"),
        ("Assessment Date", "assessment_date"),
        ("Live Azure Validation", "live_azure_validation"),
    ):
        value = assessment.get(key, "Unknown")
        if key == "live_azure_validation":
            value = "Yes" if bool(value) else "No"
        lines.append(f"| {label} | {md_escape(value or 'Unknown')} |")
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(clean_text(assessment.get("executive_summary")))
    lines.append("")

    lines.append("## Severity Overview")
    lines.append("")
    lines.append("| Critical | High | Medium | Low |")
    lines.append("|---:|---:|---:|---:|")
    lines.append(
        f"| {counts['Critical']} | {counts['High']} | "
        f"{counts['Medium']} | {counts['Low']} |"
    )
    lines.append("")

    if scorecard:
        lines.append("## Assessment Scorecard")
        lines.append("")
        lines.append("| Area | Status | Summary |")
        lines.append("|---|---|---|")
        for row in scorecard:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"| {md_escape(row.get('area'))} | "
                f"{md_escape(row.get('status'))} | "
                f"{md_escape(row.get('summary'))} |"
            )
        lines.append("")

    if priorities:
        lines.append("## Top Priority Actions")
        lines.append("")
        lines.append("| Priority | Finding | Action |")
        lines.append("|---|---|---|")
        for item in priorities:
            lines.append(
                f"| {md_escape(item.get('priority', ''))} | "
                f"{md_escape(item.get('id'))} — {md_escape(item.get('title'))} | "
                f"{md_escape(item.get('recommendation'))} |"
            )
        lines.append("")

    if isinstance(architecture, dict) and (
        clean_text(architecture.get("summary"))
        or architecture.get("components")
        or architecture.get("flows")
    ):
        lines.append("## Architecture Overview")
        lines.append("")
        if clean_text(architecture.get("summary")):
            lines.append(clean_text(architecture.get("summary")))
            lines.append("")

        components = architecture.get("components", [])
        if isinstance(components, list) and components:
            lines.append("**Key components:**")
            lines.append("")
            for component in components:
                lines.append(f"- {clean_text(component)}")
            lines.append("")

        flows = architecture.get("flows", [])
        if isinstance(flows, list) and flows:
            lines.append("### Material Traffic Flows")
            lines.append("")
            for flow in flows:
                if not isinstance(flow, dict):
                    continue
                path = flow.get("path", [])
                if not isinstance(path, list):
                    path = []
                path_text = " → ".join(clean_text(part) for part in path if clean_text(part))
                status = clean_text(flow.get("status"))
                suffix = f" — **{status}**" if status else ""
                lines.append(
                    f"- **{clean_text(flow.get('name'), 'Flow')}**: "
                    f"{path_text}{suffix}"
                )
            lines.append("")

    lines.append("## Findings")
    lines.append("")
    if not findings:
        lines.append("No findings were identified.")
        lines.append("")
    else:
        for item in sorted_findings(findings):
            finding_id = clean_text(item.get("id"))
            severity = clean_text(item.get("severity"))
            title = clean_text(item.get("title"))
            area = clean_text(item.get("area"))
            requirement_id = clean_text(item.get("requirement_id"))
            priority = clean_text(item.get("priority"))

            lines.append("<details>")
            lines.append(
                f"<summary><strong>{severity} · {finding_id} — "
                f"{html.escape(title)}</strong></summary>"
            )
            lines.append("")
            lines.append(f"**Area:** {area}  ")
            if requirement_id:
                lines.append(f"**Requirement:** `{requirement_id}`  ")
            if priority:
                lines.append(f"**Priority:** {priority}  ")
            lines.append("")
            lines.append("**Evidence**")
            lines.append("")
            for evidence in item.get("evidence", []):
                if not isinstance(evidence, dict):
                    continue
                lines.append(
                    f"- `{clean_text(evidence.get('source'))}` — "
                    f"{clean_text(evidence.get('detail'))}"
                )
            lines.append("")
            lines.append(f"**Observed State**  \n{clean_text(item.get('observed_state'))}")
            lines.append("")
            lines.append(f"**Expected State**  \n{clean_text(item.get('expected_state'))}")
            lines.append("")
            lines.append(f"**Risk**  \n{clean_text(item.get('risk'))}")
            lines.append("")
            lines.append(f"**Recommendation**  \n{clean_text(item.get('recommendation'))}")

            dependencies = item.get("dependencies", [])
            if isinstance(dependencies, list) and dependencies:
                lines.append("")
                lines.append("**Dependencies / Considerations**")
                lines.append("")
                for dependency in dependencies:
                    lines.append(f"- {clean_text(dependency)}")

            lines.append("")
            lines.append("</details>")
            lines.append("")

    if compliance:
        lines.append("## Requirements Compliance")
        lines.append("")
        lines.append("| Requirement | Status | Evidence | Notes |")
        lines.append("|---|---|---|---|")
        for row in compliance:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"| `{md_escape(row.get('requirement_id'))}` | "
                f"{md_escape(row.get('status'))} | "
                f"{md_escape(row.get('evidence'))} | "
                f"{md_escape(row.get('notes'))} |"
            )
        lines.append("")

    if positives:
        lines.append("## What Is Working Well")
        lines.append("")
        for item in positives:
            if isinstance(item, dict):
                title = clean_text(item.get("title"))
                evidence = clean_text(item.get("evidence"))
                suffix = f" — {evidence}" if evidence else ""
                lines.append(f"- **{title}**{suffix}")
            else:
                lines.append(f"- {clean_text(item)}")
        lines.append("")

    if assumptions:
        lines.append("## Assumptions & Validation Required")
        lines.append("")
        lines.append("| ID | Topic | Assumption / Dependency | Validation Required |")
        lines.append("|---|---|---|---|")
        for item in assumptions:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"| {md_escape(item.get('id'))} | "
                f"{md_escape(item.get('topic'))} | "
                f"{md_escape(item.get('detail'))} | "
                f"{md_escape(item.get('validation_required'))} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "Generated from `network-assessment.json` by the repository assessment renderer."
    )
    lines.append("")

    return "\n".join(lines)


def status_class(status: str) -> str:
    s = status.lower()
    if any(term in s for term in ("critical", "not met", "action required")):
        return "danger"
    if any(term in s for term in ("partial", "improvement", "warning")):
        return "warning"
    if any(term in s for term in ("met", "healthy", "expected")):
        return "success"
    if any(term in s for term in ("external", "validate", "unknown", "not applicable")):
        return "neutral"
    return "info"


def render_html(data: dict[str, Any]) -> str:
    assessment = data["assessment"]
    findings = [item for item in data.get("findings", []) if isinstance(item, dict)]
    counts = severity_counts(findings)
    scorecard = data.get("scorecard", [])
    architecture = data.get("architecture", {})
    compliance = data.get("requirement_compliance", [])
    positives = data.get("positive_findings", [])
    assumptions = data.get("assumptions", [])
    priorities = top_priorities(findings)

    title = clean_text(assessment.get("title"), "Azure Networking Assessment")
    overall = clean_text(assessment.get("overall_status"))
    overall_class = status_class(overall)

    def metric_card(severity: str) -> str:
        cls = severity.lower()
        return f"""
        <article class="metric-card {cls}">
          <div class="metric-label">{h(severity)}</div>
          <div class="metric-value">{counts[severity]}</div>
          <div class="metric-caption">findings</div>
        </article>
        """

    scorecard_html = ""
    if scorecard:
        rows = []
        for row in scorecard:
            if not isinstance(row, dict):
                continue
            status = clean_text(row.get("status"))
            rows.append(
                "<tr>"
                f"<td>{h(row.get('area'))}</td>"
                f"<td><span class='pill {status_class(status)}'>{h(status)}</span></td>"
                f"<td>{h(row.get('summary'))}</td>"
                "</tr>"
            )
        scorecard_html = f"""
        <section class="section">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Assessment</span>
              <h2>Scorecard</h2>
            </div>
          </div>
          <div class="card table-wrap">
            <table>
              <thead><tr><th>Area</th><th>Status</th><th>Summary</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
          </div>
        </section>
        """

    priorities_html = ""
    if priorities:
        cards = []
        for item in priorities:
            cards.append(
                f"""
                <article class="priority-card">
                  <div class="priority-number">{h(item.get('priority', ''))}</div>
                  <div>
                    <div class="priority-meta">{h(item.get('id'))} · {h(item.get('area'))}</div>
                    <h3>{h(item.get('title'))}</h3>
                    <p>{h(item.get('recommendation'))}</p>
                  </div>
                </article>
                """
            )
        priorities_html = f"""
        <section class="section">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Remediation</span>
              <h2>Top Priority Actions</h2>
            </div>
          </div>
          <div class="priority-grid">{''.join(cards)}</div>
        </section>
        """

    architecture_html = ""
    if isinstance(architecture, dict) and (
        clean_text(architecture.get("summary"))
        or architecture.get("components")
        or architecture.get("flows")
    ):
        components = architecture.get("components", [])
        component_html = ""
        if isinstance(components, list) and components:
            component_html = (
                "<div class='component-grid'>"
                + "".join(f"<div class='component-chip'>{h(c)}</div>" for c in components)
                + "</div>"
            )

        flows = architecture.get("flows", [])
        flow_html = ""
        if isinstance(flows, list) and flows:
            rendered_flows = []
            for flow in flows:
                if not isinstance(flow, dict):
                    continue
                path = flow.get("path", [])
                if not isinstance(path, list):
                    path = []
                path_parts = []
                for index, part in enumerate(path):
                    if index:
                        path_parts.append("<span class='flow-arrow'>→</span>")
                    path_parts.append(f"<span class='flow-node'>{h(part)}</span>")
                flow_status = clean_text(flow.get("status"))
                rendered_flows.append(
                    f"""
                    <div class="flow-row">
                      <div class="flow-head">
                        <strong>{h(flow.get('name'),)}</strong>
                        <span class="pill {status_class(flow_status)}">{h(flow_status)}</span>
                      </div>
                      <div class="flow-path">{''.join(path_parts)}</div>
                    </div>
                    """
                )
            flow_html = "<div class='flow-list'>" + "".join(rendered_flows) + "</div>"

        architecture_html = f"""
        <section class="section">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Design</span>
              <h2>Architecture Overview</h2>
            </div>
          </div>
          <div class="card architecture-card">
            <p class="lead-small">{h(architecture.get('summary'))}</p>
            {component_html}
            {flow_html}
          </div>
        </section>
        """

    finding_cards = []
    for item in sorted_findings(findings):
        severity = clean_text(item.get("severity"))
        evidence_items = []
        for evidence in item.get("evidence", []):
            if not isinstance(evidence, dict):
                continue
            evidence_items.append(
                f"<li><code>{h(evidence.get('source'))}</code><span>{h(evidence.get('detail'))}</span></li>"
            )

        dependencies = item.get("dependencies", [])
        dependency_html = ""
        if isinstance(dependencies, list) and dependencies:
            dependency_html = (
                "<div class='detail-block'><h4>Dependencies / Considerations</h4><ul>"
                + "".join(f"<li>{h(dep)}</li>" for dep in dependencies)
                + "</ul></div>"
            )

        requirement = clean_text(item.get("requirement_id"))
        requirement_html = (
            f"<span class='meta-chip'>{h(requirement)}</span>" if requirement else ""
        )

        finding_cards.append(
            f"""
            <details class="finding-card severity-{severity.lower()}">
              <summary>
                <div class="finding-summary-left">
                  <span class="severity-badge {severity.lower()}">{h(severity)}</span>
                  <div>
                    <div class="finding-kicker">{h(item.get('id'))} · {h(item.get('area'))}</div>
                    <div class="finding-title">{h(item.get('title'))}</div>
                  </div>
                </div>
                <div class="finding-summary-right">
                  {requirement_html}
                  <span class="meta-chip">{h(item.get('priority'))}</span>
                </div>
              </summary>
              <div class="finding-body">
                <div class="detail-grid">
                  <div class="detail-block">
                    <h4>Observed State</h4>
                    <p>{h(item.get('observed_state'))}</p>
                  </div>
                  <div class="detail-block">
                    <h4>Expected State</h4>
                    <p>{h(item.get('expected_state'))}</p>
                  </div>
                  <div class="detail-block">
                    <h4>Risk</h4>
                    <p>{h(item.get('risk'))}</p>
                  </div>
                  <div class="detail-block">
                    <h4>Recommendation</h4>
                    <p>{h(item.get('recommendation'))}</p>
                  </div>
                </div>
                <div class="detail-block evidence-block">
                  <h4>Evidence</h4>
                  <ul class="evidence-list">{''.join(evidence_items)}</ul>
                </div>
                {dependency_html}
              </div>
            </details>
            """
        )

    findings_html = (
        "".join(finding_cards)
        if finding_cards
        else "<div class='card empty-state'>No findings were identified.</div>"
    )

    compliance_html = ""
    if compliance:
        rows = []
        for row in compliance:
            if not isinstance(row, dict):
                continue
            status = clean_text(row.get("status"))
            rows.append(
                "<tr>"
                f"<td><code>{h(row.get('requirement_id'))}</code></td>"
                f"<td><span class='pill {status_class(status)}'>{h(status)}</span></td>"
                f"<td>{h(row.get('evidence'))}</td>"
                f"<td>{h(row.get('notes'))}</td>"
                "</tr>"
            )
        compliance_html = f"""
        <section class="section">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Controls</span>
              <h2>Requirements Compliance</h2>
            </div>
          </div>
          <div class="card table-wrap">
            <table>
              <thead><tr><th>Requirement</th><th>Status</th><th>Evidence</th><th>Notes</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
          </div>
        </section>
        """

    positives_html = ""
    if positives:
        cards = []
        for item in positives:
            if isinstance(item, dict):
                cards.append(
                    f"""
                    <div class="positive-item">
                      <div class="checkmark">✓</div>
                      <div><strong>{h(item.get('title'))}</strong><p>{h(item.get('evidence'))}</p></div>
                    </div>
                    """
                )
            else:
                cards.append(
                    f"<div class='positive-item'><div class='checkmark'>✓</div><div>{h(item)}</div></div>"
                )
        positives_html = f"""
        <section class="section">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Strengths</span>
              <h2>What Is Working Well</h2>
            </div>
          </div>
          <div class="card positive-card">{''.join(cards)}</div>
        </section>
        """

    assumptions_html = ""
    if assumptions:
        rows = []
        for item in assumptions:
            if not isinstance(item, dict):
                continue
            rows.append(
                "<tr>"
                f"<td>{h(item.get('id'))}</td>"
                f"<td>{h(item.get('topic'))}</td>"
                f"<td>{h(item.get('detail'))}</td>"
                f"<td>{h(item.get('validation_required'))}</td>"
                "</tr>"
            )
        assumptions_html = f"""
        <section class="section">
          <div class="section-heading">
            <div>
              <span class="eyebrow">Validation</span>
              <h2>Assumptions &amp; Validation Required</h2>
            </div>
          </div>
          <div class="card table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Topic</th><th>Assumption / Dependency</th><th>Validation Required</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
          </div>
        </section>
        """

    generated_date = clean_text(assessment.get("assessment_date")) or date.today().isoformat()
    live_validation = "Yes" if assessment.get("live_azure_validation", False) else "No"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(title)}</title>
  <style>
    :root {{
      --page-bg: #f4f7fb;
      --surface: #ffffff;
      --surface-alt: #f8fafc;
      --border: #e2e8f0;
      --text-primary: #0f172a;
      --text-secondary: #475569;
      --text-muted: #64748b;
      --navy: #0b1f33;
      --navy-soft: #12314f;
      --azure: #0078d4;
      --azure-dark: #005a9e;
      --azure-soft: #e8f3fc;
      --critical: #b42318;
      --critical-bg: #fef3f2;
      --high: #d92d20;
      --high-bg: #fef3f2;
      --medium: #b54708;
      --medium-bg: #fffaeb;
      --low: #175cd3;
      --low-bg: #eff8ff;
      --healthy: #067647;
      --healthy-bg: #ecfdf3;
      --neutral: #475467;
      --neutral-bg: #f2f4f7;
      --shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--page-bg);
      color: var(--text-primary);
      font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
      line-height: 1.55;
    }}

    .report-header {{
      background: var(--navy);
      color: #fff;
      border-bottom: 4px solid var(--azure);
    }}

    .header-inner {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 30px 24px 26px;
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: flex-start;
    }}

    .header-kicker {{
      color: #9fc9eb;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .09em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}

    h1 {{
      margin: 0;
      font-size: 32px;
      line-height: 1.15;
      letter-spacing: -.02em;
    }}

    .header-subtitle {{
      margin: 9px 0 0;
      color: #d6e4f0;
      max-width: 760px;
      font-size: 15px;
    }}

    .header-meta {{
      display: grid;
      grid-template-columns: repeat(4, minmax(110px, 1fr));
      gap: 12px;
      margin-top: 24px;
    }}

    .header-meta-item {{
      border-top: 1px solid rgba(255,255,255,.16);
      padding-top: 10px;
    }}

    .header-meta-label {{
      color: #9fb4c7;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .06em;
      font-weight: 700;
    }}

    .header-meta-value {{
      margin-top: 3px;
      color: #fff;
      font-size: 14px;
      font-weight: 600;
    }}

    .dashboard-shell {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 28px 24px 56px;
    }}

    .status-banner {{
      display: flex;
      gap: 18px;
      align-items: flex-start;
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 5px solid var(--azure);
      border-radius: 12px;
      padding: 20px 22px;
      box-shadow: var(--shadow);
    }}

    .status-banner.danger {{ border-left-color: var(--high); }}
    .status-banner.warning {{ border-left-color: var(--medium); }}
    .status-banner.success {{ border-left-color: var(--healthy); }}

    .status-label {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .status-copy h2 {{
      margin: 0 0 6px;
      font-size: 18px;
    }}

    .status-copy p {{
      margin: 0;
      color: var(--text-secondary);
      font-size: 14px;
    }}

    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}

    .metric-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-top: 4px solid var(--neutral);
      border-radius: 12px;
      padding: 16px 18px;
      box-shadow: var(--shadow);
    }}

    .metric-card.critical {{ border-top-color: var(--critical); }}
    .metric-card.high {{ border-top-color: var(--high); }}
    .metric-card.medium {{ border-top-color: var(--medium); }}
    .metric-card.low {{ border-top-color: var(--low); }}

    .metric-label {{
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 650;
    }}

    .metric-value {{
      font-size: 32px;
      line-height: 1.1;
      font-weight: 750;
      margin-top: 5px;
    }}

    .metric-card.critical .metric-value {{ color: var(--critical); }}
    .metric-card.high .metric-value {{ color: var(--high); }}
    .metric-card.medium .metric-value {{ color: var(--medium); }}
    .metric-card.low .metric-value {{ color: var(--low); }}

    .metric-caption {{
      color: var(--text-muted);
      font-size: 12px;
      margin-top: 2px;
    }}

    .section {{ margin-top: 28px; }}

    .section-heading {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      margin-bottom: 12px;
    }}

    .eyebrow {{
      display: block;
      color: var(--azure-dark);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
      margin-bottom: 3px;
    }}

    h2 {{
      margin: 0;
      font-size: 21px;
      letter-spacing: -.01em;
    }}

    h3 {{ margin: 0 0 6px; font-size: 16px; }}
    h4 {{ margin: 0 0 6px; font-size: 13px; }}

    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: var(--shadow);
    }}

    .executive-card {{ padding: 22px; }}
    .executive-card p {{ margin: 0; color: var(--text-secondary); }}

    .priority-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }}

    .priority-card {{
      display: flex;
      gap: 14px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
      box-shadow: var(--shadow);
    }}

    .priority-number {{
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 42px;
      height: 42px;
      border-radius: 10px;
      background: var(--azure-soft);
      color: var(--azure-dark);
      font-weight: 800;
    }}

    .priority-meta {{
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 4px;
    }}

    .priority-card p {{
      margin: 0;
      color: var(--text-secondary);
      font-size: 13px;
    }}

    .architecture-card {{ padding: 20px; }}
    .lead-small {{ margin: 0 0 16px; color: var(--text-secondary); }}

    .component-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 14px 0 18px;
    }}

    .component-chip {{
      background: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 8px 11px;
      font-size: 13px;
      font-weight: 650;
    }}

    .flow-list {{
      border-top: 1px solid var(--border);
      margin-top: 12px;
      padding-top: 12px;
    }}

    .flow-row {{
      padding: 12px 0;
      border-bottom: 1px solid var(--border);
    }}

    .flow-row:last-child {{ border-bottom: 0; }}

    .flow-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 9px;
    }}

    .flow-path {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .flow-node {{
      background: var(--azure-soft);
      color: var(--azure-dark);
      border: 1px solid #cce5f7;
      border-radius: 8px;
      padding: 6px 9px;
      font-size: 12px;
      font-weight: 650;
    }}

    .flow-arrow {{ color: var(--text-muted); font-weight: 700; }}

    .findings-list {{
      display: grid;
      gap: 10px;
    }}

    details.finding-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-left: 4px solid var(--neutral);
      border-radius: 11px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }}

    details.severity-critical {{ border-left-color: var(--critical); }}
    details.severity-high {{ border-left-color: var(--high); }}
    details.severity-medium {{ border-left-color: var(--medium); }}
    details.severity-low {{ border-left-color: var(--low); }}

    summary {{
      list-style: none;
      cursor: pointer;
      padding: 15px 17px;
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: center;
    }}

    summary::-webkit-details-marker {{ display: none; }}

    summary:focus-visible {{
      outline: 3px solid rgba(0,120,212,.28);
      outline-offset: -3px;
    }}

    .finding-summary-left {{
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }}

    .finding-summary-right {{
      display: flex;
      gap: 7px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}

    .finding-kicker {{
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}

    .finding-title {{ font-size: 14px; font-weight: 700; }}

    .severity-badge,
    .pill,
    .meta-chip {{
      display: inline-flex;
      align-items: center;
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 750;
      white-space: nowrap;
    }}

    .severity-badge.critical {{ color: var(--critical); background: var(--critical-bg); }}
    .severity-badge.high {{ color: var(--high); background: var(--high-bg); }}
    .severity-badge.medium {{ color: var(--medium); background: var(--medium-bg); }}
    .severity-badge.low {{ color: var(--low); background: var(--low-bg); }}

    .pill.danger {{ color: var(--high); background: var(--high-bg); }}
    .pill.warning {{ color: var(--medium); background: var(--medium-bg); }}
    .pill.success {{ color: var(--healthy); background: var(--healthy-bg); }}
    .pill.neutral {{ color: var(--neutral); background: var(--neutral-bg); }}
    .pill.info {{ color: var(--low); background: var(--low-bg); }}

    .meta-chip {{
      color: var(--text-secondary);
      background: var(--surface-alt);
      border: 1px solid var(--border);
    }}

    .finding-body {{
      border-top: 1px solid var(--border);
      padding: 18px;
      background: #fcfdff;
    }}

    .detail-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0,1fr));
      gap: 12px;
    }}

    .detail-block {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 13px;
    }}

    .detail-block p {{
      margin: 0;
      color: var(--text-secondary);
      font-size: 13px;
    }}

    .evidence-block {{ margin-top: 12px; }}

    .evidence-list {{
      margin: 0;
      padding-left: 18px;
    }}

    .evidence-list li {{
      margin: 7px 0;
      color: var(--text-secondary);
      font-size: 13px;
    }}

    .evidence-list code {{
      display: inline-block;
      margin-right: 7px;
    }}

    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: .92em;
      background: #eef2f7;
      border: 1px solid #e2e8f0;
      border-radius: 5px;
      padding: 1px 5px;
    }}

    .table-wrap {{ overflow-x: auto; }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}

    th {{
      text-align: left;
      background: var(--surface-alt);
      color: var(--text-secondary);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .04em;
      padding: 11px 13px;
      border-bottom: 1px solid var(--border);
    }}

    td {{
      padding: 11px 13px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
      color: var(--text-secondary);
    }}

    tr:last-child td {{ border-bottom: 0; }}

    .positive-card {{ padding: 8px 18px; }}

    .positive-item {{
      display: flex;
      gap: 11px;
      align-items: flex-start;
      padding: 12px 0;
      border-bottom: 1px solid var(--border);
    }}

    .positive-item:last-child {{ border-bottom: 0; }}

    .positive-item p {{
      margin: 3px 0 0;
      color: var(--text-secondary);
      font-size: 13px;
    }}

    .checkmark {{
      min-width: 25px;
      height: 25px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: var(--healthy-bg);
      color: var(--healthy);
      font-weight: 800;
    }}

    .empty-state {{
      padding: 20px;
      color: var(--text-secondary);
    }}

    footer {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 24px 34px;
      color: var(--text-muted);
      font-size: 12px;
    }}

    @media (max-width: 900px) {{
      .metric-grid {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
      .priority-grid {{ grid-template-columns: 1fr; }}
      .header-meta {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
    }}

    @media (max-width: 640px) {{
      .header-inner, .dashboard-shell, footer {{ padding-left: 16px; padding-right: 16px; }}
      .header-top {{ flex-direction: column; }}
      h1 {{ font-size: 27px; }}
      .metric-grid {{ grid-template-columns: 1fr; }}
      .detail-grid {{ grid-template-columns: 1fr; }}
      summary {{ align-items: flex-start; flex-direction: column; }}
      .finding-summary-right {{ justify-content: flex-start; }}
      .header-meta {{ grid-template-columns: 1fr 1fr; }}
    }}

    @media print {{
      body {{ background: #fff; }}
      .report-header {{ background: #fff; color: #000; border-bottom: 2px solid #000; }}
      .header-subtitle, .header-meta-label {{ color: #444; }}
      .header-meta-value, .header-kicker {{ color: #000; }}
      .dashboard-shell {{ max-width: none; padding: 20px 0; }}
      .card, .metric-card, .priority-card, details.finding-card {{ box-shadow: none; }}
      details {{ break-inside: avoid; }}
      details > * {{ display: block; }}
      footer {{ max-width: none; padding: 0; }}
    }}
  </style>
</head>
<body>
  <header class="report-header">
    <div class="header-inner">
      <div class="header-top">
        <div>
          <div class="header-kicker">Azure Networking · Zero Trust Assessment</div>
          <h1>{h(title)}</h1>
          <p class="header-subtitle">{h(assessment.get('scope', 'Repository assessment'))}</p>
        </div>
      </div>
      <div class="header-meta">
        <div class="header-meta-item">
          <div class="header-meta-label">Environment</div>
          <div class="header-meta-value">{h(assessment.get('environment', 'Unknown') or 'Unknown')}</div>
        </div>
        <div class="header-meta-item">
          <div class="header-meta-label">Region</div>
          <div class="header-meta-value">{h(assessment.get('region', 'Unknown') or 'Unknown')}</div>
        </div>
        <div class="header-meta-item">
          <div class="header-meta-label">Assessment Date</div>
          <div class="header-meta-value">{h(generated_date)}</div>
        </div>
        <div class="header-meta-item">
          <div class="header-meta-label">Live Azure Validation</div>
          <div class="header-meta-value">{h(live_validation)}</div>
        </div>
      </div>
    </div>
  </header>

  <main class="dashboard-shell">
    <section class="status-banner {overall_class}">
      <span class="status-label pill {overall_class}">{h(overall)}</span>
      <div class="status-copy">
        <h2>Overall Assessment</h2>
        <p>{h(assessment.get('executive_summary'))}</p>
      </div>
    </section>

    <section class="metric-grid" aria-label="Severity summary">
      {''.join(metric_card(s) for s in SEVERITIES)}
    </section>

    <section class="section">
      <div class="section-heading">
        <div>
          <span class="eyebrow">Summary</span>
          <h2>Executive Summary</h2>
        </div>
      </div>
      <div class="card executive-card">
        <p>{h(assessment.get('executive_summary'))}</p>
      </div>
    </section>

    {scorecard_html}
    {priorities_html}
    {architecture_html}

    <section class="section">
      <div class="section-heading">
        <div>
          <span class="eyebrow">Evidence</span>
          <h2>Detailed Findings</h2>
        </div>
      </div>
      <div class="findings-list">
        {findings_html}
      </div>
    </section>

    {compliance_html}
    {positives_html}
    {assumptions_html}
  </main>

  <footer>
    Generated from <code>network-assessment.json</code> by the repository assessment renderer.
  </footer>
</body>
</html>
"""


def write_outputs(source: Path, data: dict[str, Any]) -> tuple[Path, Path]:
    output_dir = source.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = output_dir / "network-recommendations.md"
    html_path = output_dir / "network-recommendations.html"

    markdown_path.write_text(render_markdown(data), encoding="utf-8")
    html_path.write_text(render_html(data), encoding="utf-8")

    return markdown_path, html_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render an Azure networking assessment JSON into Markdown and HTML."
    )
    parser.add_argument(
        "assessment_json",
        type=Path,
        help="Path to network-assessment.json",
    )
    args = parser.parse_args()

    source = args.assessment_json.resolve()

    try:
        data = load_json(source)
        validate(data)
        markdown_path, html_path = write_outputs(source, data)
    except AssessmentError as exc:
        print(f"Assessment render failed: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Assessment render failed: {exc}", file=sys.stderr)
        return 1

    findings = [item for item in data.get("findings", []) if isinstance(item, dict)]
    counts = severity_counts(findings)

    print("Assessment rendered successfully.")
    print(
        f"Findings: Critical={counts['Critical']} High={counts['High']} "
        f"Medium={counts['Medium']} Low={counts['Low']}"
    )
    print(f"Markdown: {markdown_path}")
    print(f"HTML: {html_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
