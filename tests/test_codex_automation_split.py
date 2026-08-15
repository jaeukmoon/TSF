import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CodexAutomationSplitTests(unittest.TestCase):
    def test_weekly_workflow_is_deterministic_ingestion_only(self):
        workflow = (ROOT / ".github" / "workflows" / "weekly.yml").read_text(encoding="utf-8")
        self.assertNotIn("pip install anthropic", workflow)
        self.assertNotIn("ANTHROPIC_API_KEY", workflow)
        self.assertNotIn("max_cards", workflow)
        self.assertIn("deterministic leaderboard ingestion", workflow.lower())

    def test_tracker_contains_no_anthropic_runtime(self):
        tracker_text = "\n".join(
            path.read_text(encoding="utf-8") for path in (ROOT / "tracker").glob("*.py")
        ).lower()
        self.assertNotIn("import anthropic", tracker_text)
        self.assertNotIn("anthropic_api_key", tracker_text)
        self.assertNotIn("claude-sonnet", tracker_text)

    def test_codex_project_skill_adapts_the_canonical_tsf_skill(self):
        adapter = ROOT / ".agents" / "skills" / "tsf-cards" / "SKILL.md"
        text = adapter.read_text(encoding="utf-8")
        self.assertIn(".claude/skills/tsf-cards/SKILL.md", text)
        self.assertIn("Read", text)
        self.assertIn("completely", text)


if __name__ == "__main__":
    unittest.main()
