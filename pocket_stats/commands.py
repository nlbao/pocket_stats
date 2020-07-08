import click
from data import fetch_data as _fetch_data, count_words_in_title, get_word_counts, load_cache


@click.group()
def cli():
    pass


@click.command()
@click.option('--offset', type=int, default=0)
@click.option('--limit', type=int, default=None)
@click.option('--overwrite_cache', is_flag=True)
def fetch_data(offset: int, limit: int, overwrite_cache: bool) -> None:
    ans = _fetch_data(offset, limit, overwrite_cache)
    if len(ans) > 0:
        print('Sample record:')
        print(ans[0])


@click.command()
def title_word_count():
    data = load_cache()
    ans = count_words_in_title(data)
    for word, cnt in ans.items():
        print(word, ':', cnt)


@click.command()
def word_counts():
    data = load_cache()
    print(get_word_counts(data))


cli.add_command(fetch_data)
cli.add_command(title_word_count)
cli.add_command(word_counts)


if __name__ == '__main__':
    cli()
