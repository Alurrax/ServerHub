import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.models import Base


# Objeto de configuración de Alembic
config = context.config


# Tomamos la conexión PostgreSQL desde la variable de entorno
DATABASE_URL = os.environ["DATABASE_URL"]

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL,
)


# Configuración de logs de Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Metadata de nuestros modelos SQLAlchemy.
# Alembic la usa para detectar cambios automáticamente.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones sin conexión activa directa a la BD."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones conectándose directamente a PostgreSQL."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
