"""First line of every message the bot sends on its own or for its Claude session: the owner's chat also gets
messages from other agents and services through this bot, and the line tells them apart.
The shared humanizer keeps this line unchanged."""

BOT_SESSION = "Telegram botu (Claude oturumu):"
BOT_SERVICE = "Telegram botu (otomatik):"
TUNNEL = "Telegram tüneli (otomatik):"


def labelled(text: str, head: str, html: bool = False) -> str:
    """*text* headed by *head*, bold when the message goes as HTML (Hakan's rule); already headed: unchanged."""
    body = text or ""
    line = f"<b>{head}</b>" if html else head
    if body == line or body.startswith(line + "\n"):
        return body
    return f"{line}\n{body}"
