import click
from data import fetch_data as _fetch_data


@click.group()
def cli():
    pass


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)


@click.command()
@click.option('--offset', default=0)
@click.option('--limit', default=None)
@click.option('--overwrite_cache', is_flag=True)
def fetch_data(offset: int, limit: int, overwrite_cache: bool) -> None:
    ans = _fetch_data(offset, limit, overwrite_cache)
    print(ans)


cli.add_command(hello)
cli.add_command(fetch_data)


if __name__ == '__main__':
    cli()
