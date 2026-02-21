"""
Tests for AIService.

render_markdown() and apply_redaction() are pure functions — tested directly.
generate() is tested with a mocked AsyncOpenAI client.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.ai_output import AIAction, AIFollowupEmail, AIOutput
from app.services.ai_service import AIService


@pytest.fixture
def service() -> AIService:
    return AIService()


@pytest.fixture
def sample_output() -> AIOutput:
    return AIOutput(
        title_suggestion="Q4 Planning Meeting",
        management_summary=["Budget approved for next quarter", "Timeline agreed by all teams"],
        decisions=["Use React for the new frontend", "Migrate DB by end of month"],
        actions=[
            AIAction(
                description="Set up CI/CD pipeline",
                owner_text="Alice",
                due_date="2025-03-01",
                priority="high",
            ),
            AIAction(
                description="Write unit tests",
                owner_text=None,
                due_date=None,
                priority="medium",
            ),
        ],
        risks_issues=["Timeline is very tight", "Two team members on leave"],
        next_agenda=["Review sprint velocity", "Demo new features"],
        followup_email=AIFollowupEmail(
            subject="Q4 Planning — action items",
            body_bullets=["CI/CD assigned to Alice", "Tests to be completed by EOW"],
        ),
    )


# ── render_markdown ─────────────────────────────────────────────────────────


def test_render_markdown_contains_h1_title(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "# Q4 Planning Meeting" in md


def test_render_markdown_contains_summary_section(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "## Summary" in md
    assert "Budget approved for next quarter" in md


def test_render_markdown_contains_decisions_section(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "## Decisions" in md
    assert "Use React for the new frontend" in md


def test_render_markdown_contains_action_items_table(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "## Action Items" in md
    assert "| # | Description |" in md
    assert "Set up CI/CD pipeline" in md


def test_render_markdown_action_table_owner_and_date(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "Alice" in md
    assert "2025-03-01" in md


def test_render_markdown_action_null_fields_rendered_as_dash(service, sample_output):
    md = service.render_markdown(sample_output)
    # The second action has no owner/due_date — should show "—"
    assert "—" in md


def test_render_markdown_contains_risks_section(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "## Risks & Issues" in md
    assert "Timeline is very tight" in md


def test_render_markdown_contains_next_agenda(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "## Next Agenda" in md


def test_render_markdown_contains_followup_email(service, sample_output):
    md = service.render_markdown(sample_output)
    assert "## Follow-up Email" in md
    assert "Q4 Planning — action items" in md


def test_render_markdown_no_followup_email_when_none(service):
    output = AIOutput(
        title_suggestion="Simple Meeting",
        management_summary=["One point"],
        decisions=[],
        actions=[],
        risks_issues=[],
        next_agenda=[],
        followup_email=None,
    )
    md = service.render_markdown(output)
    assert "Follow-up Email" not in md


# ── apply_redaction ─────────────────────────────────────────────────────────


def test_apply_redaction_strips_email(service):
    text = "Contact john.doe@example.com for details"
    result = service.apply_redaction(text)
    assert "[REDACTED EMAIL]" in result
    assert "john.doe@example.com" not in result


def test_apply_redaction_strips_multiple_emails(service):
    text = "CC: alice@corp.co.uk and bob@example.com"
    result = service.apply_redaction(text)
    assert result.count("[REDACTED EMAIL]") == 2


def test_apply_redaction_strips_uk_phone_plus44(service):
    text = "Call us on +44 7911 123456 today"
    result = service.apply_redaction(text)
    assert "[REDACTED PHONE]" in result
    assert "7911 123456" not in result


def test_apply_redaction_strips_uk_phone_07(service):
    text = "Mobile: 07911 123456"
    result = service.apply_redaction(text)
    assert "[REDACTED PHONE]" in result


def test_apply_redaction_strips_uk_phone_0044(service):
    text = "International: 0044 7911 123456"
    result = service.apply_redaction(text)
    assert "[REDACTED PHONE]" in result


def test_apply_redaction_leaves_normal_text_intact(service):
    text = "The project deadline is Q1 2025 and the budget is £50,000"
    result = service.apply_redaction(text)
    assert result == text


# ── generate (mocked OpenAI) ─────────────────────────────────────────────────


async def test_generate_calls_openai_and_returns_dict_and_markdown(service):
    fake_raw = {
        "title_suggestion": "Mocked Sprint Review",
        "management_summary": ["Sprint completed on time"],
        "decisions": ["Ship feature X"],
        "actions": [],
        "risks_issues": [],
        "next_agenda": ["Plan next sprint"],
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(fake_raw)

    with patch.object(
        service.client.chat.completions,
        "create",
        new=AsyncMock(return_value=mock_response),
    ):
        raw_dict, markdown = await service.generate("Some transcript text")

    assert raw_dict["title_suggestion"] == "Mocked Sprint Review"
    assert "# Mocked Sprint Review" in markdown


async def test_generate_applies_redaction_when_flag_set(service):
    fake_raw = {
        "title_suggestion": "Redacted Meeting",
        "management_summary": ["Contact user@test.com for info"],
        "decisions": [],
        "actions": [],
        "risks_issues": [],
        "next_agenda": [],
    }

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(fake_raw)

    with patch.object(
        service.client.chat.completions,
        "create",
        new=AsyncMock(return_value=mock_response),
    ):
        _, markdown = await service.generate("transcript", redact=True)

    assert "user@test.com" not in markdown
    assert "[REDACTED EMAIL]" in markdown
