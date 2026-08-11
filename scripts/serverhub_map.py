from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "serverhub-global.dot"


def python_imports(path: Path) -> set[str]:
    imports = set()

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


def module_name(path: Path) -> str:
    relative = path.relative_to(ROOT)
    parts = list(relative.with_suffix("").parts)
    return ".".join(parts)


def display_name(path: Path) -> str:
    relative = path.relative_to(ROOT)

    # Acortar rutas para que el gráfico sea legible.
    text = str(relative)

    text = text.replace("apps/api/", "")
    text = text.replace("apps/agent/", "agent/")

    return text


def node_id(value: str) -> str:
    return (
        value.replace(".", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
    )


def should_include(path: Path) -> bool:
    if ".venv" in path.parts:
        return False

    if "__pycache__" in path.parts:
        return False

    if path.name == "__init__.py":
        return False

    return True


python_files = [
    path
    for path in ROOT.rglob("*.py")
    if should_include(path)
]


modules = {
    module_name(path): path
    for path in python_files
}


edges = set()


for source_module, source_path in modules.items():
    imports = python_imports(source_path)

    for imported in imports:
        for target_module, target_path in modules.items():

            simplified_target = target_module

            # apps.api.app.main -> app.main
            if target_module.startswith("apps.api."):
                simplified_target = target_module.removeprefix(
                    "apps.api."
                )

            if (
                imported == simplified_target
                or imported.startswith(
                    simplified_target + "."
                )
                or simplified_target.startswith(
                    imported + "."
                )
            ):
                if source_module != target_module:
                    edges.add(
                        (
                            source_module,
                            target_module,
                        )
                    )


lines = [
    "digraph ServerHub {",
    "",
    '    graph [rankdir=LR, bgcolor="white"];',
    '    node [shape=box, style="rounded"];',
    '    edge [arrowsize=0.8];',
    "",
]


# =========================
# CLUSTER API
# =========================

lines += [
    '    subgraph cluster_api {',
    '        label="ServerHub API";',
]

for module, path in sorted(modules.items()):
    if module.startswith("apps.api.app"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines.append("    }")
lines.append("")


# =========================
# CLUSTER TESTS
# =========================

lines += [
    '    subgraph cluster_tests {',
    '        label="Tests";',
]

for module, path in sorted(modules.items()):
    if module.startswith("apps.api.tests"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines.append("    }")
lines.append("")


# =========================
# CLUSTER MIGRATIONS
# =========================

lines += [
    '    subgraph cluster_migrations {',
    '        label="Migraciones";',
]

for module, path in sorted(modules.items()):
    if module.startswith("apps.api.migrations"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines.append("    }")
lines.append("")


# =========================
# CLUSTER AGENT
# =========================

lines += [
    '    subgraph cluster_agent {',
    '        label="Host Agent";',
]

for module, path in sorted(modules.items()):
    if module.startswith("apps.agent"):
        lines.append(
            f'        {node_id(module)} '
            f'[label="{display_name(path)}"];'
        )

lines.append("    }")
lines.append("")


# =========================
# INFRAESTRUCTURA
# =========================

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
    '    frontend [',
    '        label="Frontend Web",',
    '        shape=box',
    '    ];',
    "",
]


# =========================
# RELACIONES PYTHON
# =========================

for source, target in sorted(edges):
    lines.append(
        f'    {node_id(source)} -> '
        f'{node_id(target)} '
        f'[label="import"];'
    )


# =========================
# RELACIONES DE INFRAESTRUCTURA
# =========================

lines += [
    "",
    "    // Infraestructura",
    "",
    "    frontend -> apps_api_app_main;",
    "",
    '    apps_api_app_main -> postgres '
    '[label="SQLAlchemy"];',
    "",
    '    apps_api_app_routers_system -> '
    'apps_agent_main '
    '[label="HTTP :9000"];',
    "",
    '    apps_agent_main -> docker '
    '[label="docker CLI"];',
    "",
    '    apps_agent_main -> systemd '
    '[label="systemctl"];',
    "",
    '    apps_agent_main -> lsblk '
    '[label="lsblk"];',
    "",
    '    compose -> apps_api_app_main '
    '[label="api"];',
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
