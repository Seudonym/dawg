import time
import typer
import logging
from pathlib import Path
from dawg.daemon import Daemon, Config

app = typer.Typer()


@app.command()
def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    config = Config(runtime_dir=Path("runtime"), memory_dir=Path("memory"))
    logger = logging.getLogger("dawg.daemon")

    daemon = Daemon(config=config)
    try:
        daemon.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()


@app.command()
def version():
    typer.echo("dawg 0.1.0")


def main():
    app()
