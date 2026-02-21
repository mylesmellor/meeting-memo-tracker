import json
import re
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.ai_output import AIOutput, AIAction

SYSTEM_PROMPT = """You are a professional meeting notes assistant. Extract structured information from the transcript below.
Return ONLY valid JSON matching this exact schema — no prose, no markdown fences:
{"title_suggestion": str, "management_summary": [str], "decisions": [str],
 "actions": [{"description": str, "owner_text": str|null, "due_date": "YYYY-MM-DD"|null, "priority": "low|medium|high"}],
 "risks_issues": [str], "next_agenda": [str],
 "followup_email": {"subject": str, "body_bullets": [str]}|null}
Rules: UK English. Concise bullet points. No filler. Dates as YYYY-MM-DD. Deduplicate actions."""


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate(self, transcript_text: str, redact: bool = False) -> tuple[dict, str]:
        """Two-pass generation: JSON extraction then validate + render markdown."""
        # Pass 1 — JSON extraction
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Meeting transcript:\n\n{transcript_text}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        raw_json = response.choices[0].message.content
        raw_dict = json.loads(raw_json)

        # Pass 2 — Validate with Pydantic + render markdown
        output = AIOutput.model_validate(raw_dict)
        markdown = self.render_markdown(output)

        if redact:
            markdown = self.apply_redaction(markdown)

        return raw_dict, markdown

    def render_markdown(self, output: AIOutput) -> str:
        lines = []
        lines.append(f"# {output.title_suggestion}\n")

        lines.append("## Summary\n")
        for item in output.management_summary:
            lines.append(f"- {item}")
        lines.append("")

        if output.decisions:
            lines.append("## Decisions\n")
            for item in output.decisions:
                lines.append(f"- {item}")
            lines.append("")

        if output.actions:
            lines.append("## Action Items\n")
            lines.append("| # | Description | Owner | Due Date | Priority |")
            lines.append("|---|-------------|-------|----------|----------|")
            for i, action in enumerate(output.actions, 1):
                owner = action.owner_text or "—"
                due = action.due_date or "—"
                priority = action.priority.capitalize()
                lines.append(f"| {i} | {action.description} | {owner} | {due} | {priority} |")
            lines.append("")

        if output.risks_issues:
            lines.append("## Risks & Issues\n")
            for item in output.risks_issues:
                lines.append(f"- {item}")
            lines.append("")

        if output.next_agenda:
            lines.append("## Next Agenda\n")
            for item in output.next_agenda:
                lines.append(f"- {item}")
            lines.append("")

        if output.followup_email:
            lines.append("## Follow-up Email\n")
            lines.append(f"**Subject:** {output.followup_email.subject}\n")
            for bullet in output.followup_email.body_bullets:
                lines.append(f"- {bullet}")
            lines.append("")

        return "\n".join(lines)

    def apply_redaction(self, text: str) -> str:
        # Strip emails
        text = re.sub(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", "[REDACTED EMAIL]", text)
        # Strip UK phone numbers (various formats)
        text = re.sub(r"(?:(?:\+44|0044|0)[\s\-]?(?:\d[\s\-]?){9,10})", "[REDACTED PHONE]", text)
        return text


ai_service = AIService()
