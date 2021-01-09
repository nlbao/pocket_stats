import click
from data import fetch_data as _fetch_data


@click.command()
@click.option('--offset', type=int, default=0, help='First item position to be fetched')
@click.option('--limit', type=int, default=None, help='Number of items to be fetched')
@click.option('--overwrite_cache', is_flag=True, help='Will overwrite the local cache')
def fetch_data(offset: int, limit: int, overwrite_cache: bool) -> None:
    ans = _fetch_data(offset, limit, overwrite_cache)
    if len(ans) > 0:
        print('Sample record:')
        print(ans[0])


@click.group()
def cli() -> None:
    pass


cli.add_command(fetch_data)

if __name__ == '__main__':
    cli()
