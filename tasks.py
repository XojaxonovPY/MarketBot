from invoke import task


# ===============================================language=========================
@task
def extract(c):
    c.run("pybabel extract --input-dirs=. -o locales/messages.pot")


@task
def init(c):
    c.run("pybabel init -i locales/messages.pot -d locales -D messages -l uz")
    c.run("pybabel init -i locales/messages.pot -d locales -D messages -l ru")
    c.run("pybabel init -i locales/messages.pot -d locales -D messages -l en")


@task
def compile(c):
    c.run("pybabel compile -d locales -D messages")


@task
def update(c):
    c.run("pybabel update -d locales -D messages -i locales/messages.pot")


# ===============================================admin=========================
@task
def admin(c):
    c.run("uvicorn web.app:app --host localhost --port 8005")


# ===============================================migratsiya=========================
@task
def mig(c):
    c.run('alembic revision --autogenerate -m "Create a baseline migrations"')


@task
def upg(c):
    c.run("alembic upgrade head")


@task
def down(c):
    c.run("alembic downgrade head")


@task
def create(c):
    c.run("alembic init migrations")
