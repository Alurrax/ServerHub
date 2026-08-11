from pathlib import Path
import ast
import re


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "serverhub-global.dot"


# =========================================================
# UTILIDADES
# =========================================================

def should_include(path: Path) -> bool:
    ignored_parts = {
        ".venv",
        "node_modules",
        "__pycache__",
        "dist",
    }

    if any(part in ignored_parts for part in path.parts):
        return False

    if path.name == "__init__.py":
        return False

    return True


def node_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", value)


def display_name(path: Path) -> str:
    relative = path.relative_to(ROOT)
    text = str(relative)

    if text.startswith("apps/api/"):
        return text.removeprefix("apps/api/")

    if text.startswith("apps/agent/"):
        return "agent/" + text.removeprefix("apps/agent/")

    if text.startswith("apps/web/src/"):
        return text.removeprefix("apps/web/src/")

    return text


# =========================================================
# PYTHON
# =========================================================

def python_module_name(path: Path) -> str:
    relative = path.relative_to(ROOT)
    return ".".join(relative.with_suffix("").parts)


def python_imports(path: Path) -> set[str]:
    imports: set[str] = set()

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

    return imports


python_files = [
    path
    for path in ROOT.rglob("*.py")
    if should_include(path)
]

python_modules = {
    python_module_name(path): path
    for path in python_files
}

python_edges: set[tuple[str, str]] = set()


for source_module, source_path in python_modules.items():
    imports = python_imports(source_path)

    for imported in imports:
        for target_module in python_modules:
            simplified_target = target_module

            if target_module.startswith("apps.api."):
                simplified_target = target_module.removeprefix(
                    "apps.api."
                )

            if (
                imported == simplified_target
                or imported.startswith(simplified_target + ".")
                or simplified_target.startswith(imported + ".")
            ):
                if source_module != target_module:
                    python_edges.add(
                        (
                            source_module,
                            target_module,
                        )
                    )


# =========================================================
# TYPESCRIPT / REACT
# =========================================================

web_root = ROOT / "apps" / "web" / "src"

typescript_files = [
    path
    for extension in ("*.ts", "*.tsx")
    for path in web_root.rglob(extension)
    if should_include(path)
]


def typescript_imports(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    patterns = [
        r'import\s+.*?\s+from\s+["\'](.+?)["\']',
        r'import\s+["\'](.+?)["\']',
        r'import\s*\(\s*["\'](.+?)["\']\s*\)',
    ]

    imports: list[str] = []

    for pattern in patterns:
        imports.extend(
            re.findall(
                pattern,
                source,
                flags=re.MULTILINE,
            )
        )

    return imports


def resolve_typescript_import(
    source_path: Path,
    imported: str,
) -> Path | None:

    # Librerías externas:
    # react, react-dom, etc.
    if not imported.startswith("."):
        return None

    base = (source_path.parent / imported).resolve()

    candidates = [
        base,
        base.with_suffix(".ts"),
        base.with_suffix(".tsx"),
        base / "index.ts",
        base / "index.tsx",
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


typescript_edges: set[tuple[Path, Path]] = set()


for source_path in typescript_files:
    for imported in typescript_imports(source_path):
        target_path = resolve_typescript_import(
            source_path,
            imported,
        )

        if target_path is not None:
            typescript_edges.add(
                (
                    source_path,
                    target_path,
                )
            )


# =========================================================
# GRAPHVIZ
# =========================================================

lines = [
    "digraph ServerHub {",
    "",
    '    graph [',
    '        rankdir=LR,',
    '        bgcolor="white",',
    '        pad="0.4",',
    '        nodesep="0.55",',
    '        ranksep="0.9"',
    '    ];',
    "",
    '    node [',
    '        shape=box,',
    '        style="rounded",',
    '        fontname="Arial"',
    '    ];',
    "",
    '    edge [',
    '        arrowsize=0.8,',
    '        fontname="Arial",',
    '        fontsize=9',
    '    ];',
    "",
]


# =========================================================
# FRONTEND
# =========================================================

lines += [
    '    subgraph cluster_frontend {',
    '        label="Frontend Web — React / TypeScript";',
    "",
]

for path in sorted(typescript_files):
    relative = str(path.relative_to(ROOT))

    lines.append(
        f'        {node_id(relative)} '
        f'[label="{display_name(path)}"];'
    )

lines += [
    "    }",
    "",
]


# =========================================================
# API
# =========================================================

lines += [
    '    subgraph cluster_api {',
    '        label="ServerHub API — FastAPI";',
    "",
]

for module, path in sorted(python_modules.items()):
    if module.startswith("apps.api.app"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines += [
    "    }",
    "",
]


# =========================================================
# TESTS
# =========================================================

lines += [
    '    subgraph cluster_tests {',
    '        label="Tests";',
    "",
]

for module, path in sorted(python_modules.items()):
    if module.startswith("apps.api.tests"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines += [
    "    }",
    "",
]


# =========================================================
# MIGRACIONES
# =========================================================

lines += [
    '    subgraph cluster_migrations {',
    '        label="Migraciones — Alembic";',
    "",
]

for module, path in sorted(python_modules.items()):
    if module.startswith("apps.api.migrations"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines += [
    "    }",
    "",
]


# =========================================================
# HOST AGENT
# =========================================================

lines += [
    '    subgraph cluster_agent {',
    '        label="Host Agent";',
    "",
]

for module, path in sorted(python_modules.items()):
    if module.startswith("apps.agent"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines += [
    "    }",
    "",
]


# =========================================================
# INFRAESTRUCTURA
# =========================================================

lines += [
    '    postgres [',
    '        label="PostgreSQL\\nserverhub-db",',
    '        shape=cylinder',
    '    ];',
    "",
    '    docker [',
    '        label="Docker Engine",',
    '        shape=component',
    '    ];',
    "",
    '    systemd [',
    '        label="systemd",',
    '        shape=component',
    '    ];',
    "",
    '    lsblk [',
    '        label="lsblk / discos",',
    '        shape=component',
    '    ];',
    "",
    '    compose [',
    '        label="compose.yml",',
    '        shape=folder',
    '    ];',
    "",
]


# =========================================================
# RELACIONES PYTHON
# =========================================================

for source, target in sorted(python_edges):
    lines.append(
        f'    {node_id(source)} -> '
        f'{node_id(target)} '
        f'[label="import"];'
    )


# =========================================================
# RELACIONES TYPESCRIPT / REACT
# =========================================================

for source_path, target_path in sorted(
    typescript_edges,
    key=lambda item: (
        str(item[0]),
        str(item[1]),
    ),
):
    source_relative = str(source_path.relative_to(ROOT))
    target_relative = str(target_path.relative_to(ROOT))

    lines.append(
        f'    {node_id(source_relative)} -> '
        f'{node_id(target_relative)} '
        f'[label="import"];'
    )


# =========================================================
# RELACIONES DE INFRAESTRUCTURA
# =========================================================

frontend_api_node = node_id(
    "apps/web/src/services/api.ts"
)

api_main_node = node_id(
    "apps.api.app.main"
)

system_router_node = node_id(
    "apps.api.app.routers.system"
)

agent_main_node = node_id(
    "apps.agent.main"
)


lines += [
    "",
    "    // Comunicación entre frontend y API",
    "",
    f'    {frontend_api_node} -> '
    f'{api_main_node} '
    f'[label="HTTP :8000"];',
    "",
    "    // API y persistencia",
    "",
    f'    {api_main_node} -> postgres '
    f'[label="SQLAlchemy"];',
    "",
    "    // API y Host Agent",
    "",
    f'    {system_router_node} -> '
    f'{agent_main_node} '
    f'[label="HTTP :9000"];',
    "",
    "    // Host Agent y Ubuntu",
    "",
    f'    {agent_main_node} -> docker '
    f'[label="docker CLI"];',
    "",
    f'    {agent_main_node} -> systemd '
    f'[label="systemctl"];',
    "",
    f'    {agent_main_node} -> lsblk '
    f'[label="lsblk"];',
    "",
    "    // Docker Compose",
    "",
    f'    compose -> {api_main_node} '
    f'[label="api"];',
    "",
    '    compose -> postgres '
    '[label="db"];',
    "",
    "}",
]


OUTPUT.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(f"Mapa generado: {OUTPUT}")
print(
    f"Python: {len(python_files)} archivos, "
    f"{len(python_edges)} relaciones"
)
print(
    f"TypeScript/React: {len(typescript_files)} archivos, "
    f"{len(typescript_edges)} relaciones"
)
