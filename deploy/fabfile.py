from fabric import task
import patchwork.transfers

APP_ROOT = "/app"
SOURCE_ENV_FILE = ".env"


@task
def deploy(c, envfile=SOURCE_ENV_FILE):
    c.run(f"mkdir -p {APP_ROOT}/logs")

    print("=== copy files ===")
    c.put(envfile, f"{APP_ROOT}/.env")
    c.put("./requirements.txt", f"{APP_ROOT}/requirements.txt")
    c.put("./app.py", f"{APP_ROOT}/app.py")
    c.put("./deploy/cronjobs", f"{APP_ROOT}/cronjobs")
    patchwork.transfers.rsync(
        c, "./statementdog/", f"{APP_ROOT}/statementdog", exclude="__pycache__"
    )

    print("=== operations ===")
    with c.cd(APP_ROOT):
        # c.run("pip install -r requirements.txt")
        c.run("crontab ./cronjobs")
        c.run("/etc/init.d/cron restart restart")
    print("=== done ===")
