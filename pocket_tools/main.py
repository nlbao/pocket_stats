import click
from data import fetch_data as _fetch_data, word_count as _word_count, load_cache


@click.group()
def cli():
    pass


@click.command()
@click.option('--offset', default=0)
@click.option('--limit', default=None)
@click.option('--overwrite_cache', is_flag=True)
def fetch_data(offset: int, limit: int, overwrite_cache: bool) -> None:
    ans = _fetch_data(offset, limit, overwrite_cache)
    if len(ans) > 0:
        print('Sample record:')
        print(ans[0])


@click.command()
def word_count():
    data = load_cache()
    ans = _word_count(data)
    for word, cnt in ans.items():
        print(word, ':', cnt)


cli.add_command(fetch_data)
cli.add_command(word_count)


if __name__ == '__main__':
    cli()
