import json
import re
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from understance.adapters.template_narrator import TemplateNarrator
from understance.domain.answer import Narration
from understance.domain.finding import Finding
from understance.ports.interfaces import Narrator

DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_RETRIES = 1
DEFAULT_MODEL = "meterless/auto"
MAX_TOKENS = 160
MAX_SUMMARY_CHARS = 500
APP_NAME = "understance"
DOTTED_NAME = re.compile(r"\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+\b")
FILE_LIKE = re.compile(r"/|\.py\b")
INSTRUCTIONS = (
    "You explain the impact of a code change to a product owner. "
    "Below are import links that were verified in the code. "
    "In one or two plain sentences, say what they mean together. "
    "Use only these links. Never mention file names, folders, line numbers "
    "or any number, and never name a module that is not listed."
)


class NightshiftUnavailable(RuntimeError):
    """Nightshift could not be reached, or did not answer in time."""


class NightshiftError(RuntimeError):
    """Nightshift answered, but refused the request or broke the expected shape."""


@dataclass(frozen=True)
class NightshiftReply:
    """The model's text and the Meterless receipt fields Understance logs."""

    text: str
    receipt_id: str | None
    routed_model: str | None
    route_kind: str | None
    latency_ms: int | None
    privacy_path: str | None
    egress: str | None
    cross_check: str | None
    cross_check_blocking: bool

    def receipt_line(self) -> str:
        return (
            f"receipt {self.receipt_id}, {self.routed_model} ({self.route_kind}), "
            f"{self.latency_ms} ms, privacy {self.privacy_path}, "
            f"egress {self.egress}, cross-check {self.cross_check}"
        )


class NightshiftClient:
    """Send one chat request to the Meterless runtime in Nightshift."""

    def __init__(
        self,
        base_url: str,
        token: str,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        retries: int = DEFAULT_RETRIES,
        opener: Callable = urllib.request.urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._token = token
        self.model = model
        self._timeout = timeout
        self._retries = retries
        self._open = opener
        self._sleep = sleep

    @classmethod
    def from_env(cls, env: Mapping[str, str], **options) -> "NightshiftClient":
        missing = [
            name
            for name in ("METERLESS_BASE_URL", "METERLESS_RUNTIME_TOKEN")
            if not env.get(name)
        ]
        if missing:
            raise ValueError(f"Nightshift settings missing: {', '.join(missing)}")
        return cls(
            env["METERLESS_BASE_URL"],
            env["METERLESS_RUNTIME_TOKEN"],
            env.get("METERLESS_MODEL") or DEFAULT_MODEL,
            **options,
        )

    def complete(self, messages: list[dict]) -> NightshiftReply:
        body = {"model": self.model, "messages": messages, "max_tokens": MAX_TOKENS}
        return _reply(self._post(body))

    def _post(self, body: dict) -> dict:
        problem = ""
        for attempt in range(self._retries + 1):
            if attempt:
                self._sleep(2**attempt)
            try:
                with self._open(self._request(body), timeout=self._timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    raise NightshiftError(f"HTTP {e.code}") from None
                problem = f"HTTP {e.code}"
            except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
                if _timed_out(e):
                    raise NightshiftUnavailable(
                        f"Nightshift did not answer within {self._timeout} seconds"
                    ) from None
                problem = type(e).__name__
            except json.JSONDecodeError:
                raise NightshiftError(
                    "Nightshift answered with text that is not JSON"
                ) from None
        tries = self._retries + 1
        raise NightshiftUnavailable(
            f"Nightshift did not answer ({problem}, {tries} tries)"
        )

    def _request(self, body: dict):
        return urllib.request.Request(
            self._url,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._token}",
                "meterless-app": APP_NAME,
                "meterless-scope": "user",
                "Content-Type": "application/json",
            },
            method="POST",
        )


class NightshiftNarrator(Narrator):
    """Ask the model for a short summary; the proof lines stay deterministic."""

    def __init__(
        self,
        client: NightshiftClient,
        proof: Narrator | None = None,
        log: Callable[[dict], None] = lambda event: None,
    ):
        self._client = client
        self._proof = proof or TemplateNarrator()
        self._log = log

    def narrate(self, findings: tuple[Finding, ...]) -> Narration:
        proof = self._proof.narrate(findings)
        if not findings:
            return proof
        links = [f.summary for f in findings]
        asked = f"{len(links)} verified links, summaries only"
        try:
            reply = self._client.complete(_messages(links))
        except (NightshiftUnavailable, NightshiftError) as e:
            self._event(asked, f"{e}; using the template", None, "fallback")
            return proof
        reason = blocked_reason(reply, _names_in(links))
        if reason is not None:
            summary = f"model claim blocked ({reason}); {reply.receipt_line()}"
            self._event(asked, summary, reply.routed_model, "blocked")
            return proof
        self._event(asked, reply.receipt_line(), reply.routed_model, "ok")
        return Narration(f"{reply.text}\n{proof.text}", reply.routed_model)

    def _event(self, asked: str, summary: str, model: str | None, status: str):
        self._log(
            {
                "agent_name": "NightshiftNarrator",
                "action": "narrate",
                "input_summary": asked,
                "output_summary": summary,
                "model": model,
                "status": status,
            }
        )


def blocked_reason(reply: NightshiftReply, allowed: set[str]) -> str | None:
    """Return why the model's text must not be shown, or None when it may be."""
    text = reply.text
    if reply.cross_check_blocking or reply.cross_check == "failed":
        return "the Meterless cross-check flagged it"
    if not text:
        return "empty text"
    if len(text) > MAX_SUMMARY_CHARS:
        return "longer than a short summary"
    if FILE_LIKE.search(text):
        return "it states a file path"
    if any(ch.isdigit() for ch in text):
        return "it states a number, such as a line"
    unknown = sorted(set(DOTTED_NAME.findall(text)) - allowed)
    if unknown:
        return f"it names modules outside the verified links: {', '.join(unknown)}"
    return None


def _timed_out(error: Exception) -> bool:
    """A slow model is not retried: a second wait would only double the delay."""
    return isinstance(error, TimeoutError) or isinstance(
        getattr(error, "reason", None), TimeoutError
    )


def _messages(links: list[str]) -> list[dict]:
    return [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": "\n".join(f"- {link}" for link in links)},
    ]


def _names_in(links: list[str]) -> set[str]:
    return {name for link in links for name in DOTTED_NAME.findall(link)}


def _reply(body: dict) -> NightshiftReply:
    try:
        text = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise NightshiftError(
            "Nightshift answer lacks choices[0].message.content"
        ) from None
    receipt = body.get("meterless") or {}
    check = body.get("meterless_cross_check") or {}
    return NightshiftReply(
        text=(text or "").strip(),
        receipt_id=receipt.get("receipt_id"),
        routed_model=receipt.get("routed_model") or body.get("model"),
        route_kind=(receipt.get("winning_route") or {}).get("kind"),
        latency_ms=(receipt.get("usage") or {}).get("latency_ms"),
        privacy_path=(receipt.get("privacy") or {}).get("path"),
        egress=(receipt.get("egress") or {}).get("destination"),
        cross_check=check.get("status"),
        cross_check_blocking=bool(check.get("blocking")),
    )
