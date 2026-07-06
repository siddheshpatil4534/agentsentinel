"""Connection checks for GitHub, Supabase, and Slack integrations."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger("integration_status")


def supabase_connected() -> bool:
    try:
        from app.services.supabase_client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            return False
        client.table("audit_logs").select("*").limit(1).execute()
        return True
    except Exception as exc:
        logger.warning("Supabase check failed: %s", exc)
        return False


def github_connected() -> bool:
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    if not (token and owner and repo):
        return False
    try:
        from github import Github

        Github(token).get_repo(f"{owner}/{repo}")
        return True
    except Exception as exc:
        logger.warning("GitHub check failed: %s", exc)
        return False


def slack_connected() -> bool:
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    if not (bot_token and channel_id):
        return False
    try:
        from slack_sdk import WebClient

        WebClient(token=bot_token).auth_test()
        return True
    except Exception as exc:
        logger.warning("Slack check failed: %s", exc)
        return False


def get_all_statuses() -> dict[str, bool]:
    return {
        "github": github_connected(),
        "supabase": supabase_connected(),
        "slack": slack_connected(),
    }