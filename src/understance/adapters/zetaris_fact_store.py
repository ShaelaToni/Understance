import contextlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from understance.adapters.csv_fact_store import TABLES, graph_from_tables
from understance.domain.graph import DependencyGraph
from understance.ports.interfaces import DataQualityError, FactStore, FactsUnavailable

DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_RETRIES = 1
PAGE_LIMIT = 100
MAX_ROWS = 10_000
SHOWN_BROKEN_LINKS = 5
TABLE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*")
ENV_NAMES = ("ZETARIS_REST_URL", "ZETARIS_ORG_ID", "ZETARIS_API_KEY")
MODULE_COLUMNS = ("module_name", "file", "last_commit", "last_changed")
LINK_COLUMNS = ("source_module", "target_module", "import_file", "import_line")


class ZetarisUnavailable(FactsUnavailable):
    """Zetaris could not be reached, or did not answer in time."""


class ZetarisQueryError(RuntimeError):
    """Zetaris answered, but refused the query or broke the expected shape."""


class ZetarisClient:
    """Run one SELECT through the Zetaris REST API and return every row."""

    def __init__(
        self,
        base_url: str,
        org_id: str,
        token: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        retries: int = DEFAULT_RETRIES,
        opener: Callable = urllib.request.urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._base = base_url.rstrip("/")
        self._org = str(org_id)
        self._token = token
        self._timeout = timeout
        self._retries = retries
        self._open = opener
        self._sleep = sleep

    @classmethod
    def from_env(cls, env: Mapping[str, str], **options) -> "ZetarisClient":
        missing = [name for name in ENV_NAMES if not env.get(name)]
        if missing:
            raise ValueError(f"Zetaris settings missing: {', '.join(missing)}")
        return cls(
            env["ZETARIS_REST_URL"],
            env["ZETARIS_ORG_ID"],
            env["ZETARIS_API_KEY"],
            **options,
        )

    def select(self, sql: str) -> list[dict]:
        first = self._call(
            "POST", "/query/sql/start", {"select": sql, "pageLimit": PAGE_LIMIT}
        )
        token = urllib.parse.quote(str(_field(first, "queryToken")), safe="")
        try:
            return self._all_pages(first, token)
        finally:
            self._close(token)

    def _all_pages(self, first: dict, token: str) -> list[dict]:
        records = list(first.get("records") or [])
        page, pages = _field(first, "pageNumber"), _field(first, "totalPages")
        for _ in range(int(pages) - 1):
            page += 1
            query = f"queryToken={token}&pageLimit={PAGE_LIMIT}&pageNumber={page}"
            records += (
                self._call("GET", f"/query/sql/page?{query}").get("records") or []
            )
            if len(records) > MAX_ROWS:
                raise ZetarisQueryError(f"more than {MAX_ROWS} rows; refusing to load")
        return records

    def _close(self, token: str) -> None:
        with contextlib.suppress(ZetarisUnavailable, ZetarisQueryError):
            self._call("DELETE", f"/query/sql/close/{token}")

    def _call(self, method: str, path: str, body: dict | None = None) -> dict:
        problem = ""
        for attempt in range(self._retries + 1):
            if attempt:
                self._sleep(2**attempt)
            try:
                with self._open(
                    self._request(method, path, body), timeout=self._timeout
                ) as r:
                    text = r.read().decode("utf-8")
                return json.loads(text) if text.strip() else {}
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    raise ZetarisQueryError(f"HTTP {e.code}: {_message(e)}") from None
                problem = f"HTTP {e.code}"
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                problem = type(e).__name__
            except json.JSONDecodeError:
                raise ZetarisQueryError(
                    "Zetaris answered with text that is not JSON"
                ) from None
        tries = self._retries + 1
        raise ZetarisUnavailable(f"Zetaris did not answer ({problem}, {tries} tries)")

    def _request(self, method: str, path: str, body: dict | None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self._token}",
            "X-Org-ID": self._org,
            "X-Request-ID": str(uuid.uuid4()),
            "Accept": "application/json",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        return urllib.request.Request(
            self._base + path, data=data, headers=headers, method=method
        )


@dataclass(frozen=True)
class ZetarisTables:
    """Where each fact lives in Zetaris: two USL tables and three source tables."""

    module: str = "lightning.metastore.understance.understance_usl.module"
    dependency: str = "lightning.metastore.understance.understance_links.dependency"
    defines: str = "understance_code.defines_csv"
    open_questions: str = "understance_code.open_questions"
    test_map: str = "understance_tests.test_map"

    def __post_init__(self):
        for name in vars(self).values():
            if not TABLE_NAME.fullmatch(name):
                raise ValueError(f"not a plain table name: {name!r}")


class ZetarisFactStore(FactStore):
    """Read the facts through Zetaris, after its data quality rule passes."""

    def __init__(
        self,
        client: ZetarisClient,
        export: FactStore,
        tables: ZetarisTables | None = None,
        log: Callable[[dict], None] = lambda event: None,
    ):
        self._client = client
        self._export = export
        self._t = tables or ZetarisTables()
        self._log = log
        self._snapshot: DependencyGraph | None = None

    def store_graph(self, graph: DependencyGraph) -> None:
        """Write the export Zetaris registers; the files are then uploaded to it."""
        self._export.store_graph(graph)

    def load_graph(self) -> DependencyGraph:
        """Check the rule, then read every fact once; later calls reuse that read."""
        if self._snapshot is None:
            self._check_links()
            self._snapshot = graph_from_tables(self._tables())
        return self._snapshot

    def _check_links(self) -> None:
        sql = (
            "SELECT d.source_module, d.target_module "
            f"FROM {self._t.dependency} d "
            f"LEFT JOIN {self._t.module} s ON s.module_name = d.source_module "
            f"LEFT JOIN {self._t.module} t ON t.module_name = d.target_module "
            "WHERE s.module_name IS NULL OR t.module_name IS NULL"
        )
        broken = _rows(self._client.select(sql), ("source_module", "target_module"))
        if not broken:
            self._event("data_quality", sql, "0 broken links", "passed")
            return
        shown = "; ".join(
            f"{r['source_module']} -> {r['target_module']}"
            for r in broken[:SHOWN_BROKEN_LINKS]
        )
        summary = f"{len(broken)} links point at no module: {shown}"
        self._event("data_quality", sql, summary, "failed")
        raise DataQualityError(summary)

    def _tables(self) -> dict[str, list[dict[str, str]]]:
        modules = self._read(self._t.module, MODULE_COLUMNS)
        links = self._read(self._t.dependency, LINK_COLUMNS)
        tables = {
            "modules.csv": [
                {"module_name": r["module_name"], "file": r["file"]} for r in modules
            ],
            "git_history.csv": [
                {k: r[k] for k in TABLES["git_history.csv"]}
                for r in modules
                if r["last_commit"]
            ],
            "dependencies.csv": [
                {
                    "source": r["source_module"],
                    "target": r["target_module"],
                    "file": r["import_file"],
                    "line": r["import_line"],
                }
                for r in links
            ],
        }
        sources = (
            ("defines.csv", self._t.defines),
            ("open_questions.csv", self._t.open_questions),
            ("test_map.csv", self._t.test_map),
        )
        for name, table in sources:
            tables[name] = self._read(table, TABLES[name])
        return {
            name: sorted(rows, key=lambda r, h=TABLES[name]: [r[k] for k in h])
            for name, rows in tables.items()
        }

    def _read(self, table: str, columns: tuple[str, ...]) -> list[dict[str, str]]:
        sql = f"SELECT {', '.join(columns)} FROM {table}"
        rows = _rows(self._client.select(sql), columns)
        self._event("query", sql, f"{len(rows)} rows", "ok")
        return rows

    def _event(self, action: str, sql: str, summary: str, status: str) -> None:
        self._log(
            {
                "agent_name": "ZetarisFactStore",
                "action": action,
                "input_summary": sql,
                "output_summary": summary,
                "status": status,
            }
        )


def _rows(records: list[dict], columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Keep the named columns as text ("" for null), as the CSV files hold them."""
    rows = []
    for record in records:
        missing = [c for c in columns if c not in record]
        if missing:
            raise ZetarisQueryError(f"Zetaris rows lack columns: {', '.join(missing)}")
        rows.append({c: "" if record[c] is None else str(record[c]) for c in columns})
    return rows


def _field(response: dict, name: str):
    if name not in response:
        raise ZetarisQueryError(f"Zetaris answer lacks {name}")
    return response[name]


def _message(error: urllib.error.HTTPError) -> str:
    try:
        text = error.read().decode("utf-8", "replace")
    except OSError:
        return error.reason or "no detail"
    try:
        return str(json.loads(text).get("msg", text))[:300]
    except (json.JSONDecodeError, AttributeError):
        return text[:300] or str(error.reason)
