import click
from data import fetch_data as _fetch_data
from visualization import create_app


@click.command()
@click.option('--offset', type=int, default=0, help='First item position to be fetched')
@click.option('--limit', type=int, default=None, help='Number of items to be fetched')
@click.option('--overwrite_cache', is_flag=True, help='Will overwrite the local cache')
def fetch_data(offset: int, limit: int, overwrite_cache: bool) -> None:
    ans = _fetch_data(offset, limit, overwrite_cache)
    if len(ans) > 0:
        print('Sample record:')
        print(ans[0])


@click.command()
@click.option('--debug', is_flag=True, help='Debug mode')
@click.option('--port', type=int, default=8050, help='Port of the web server. Default = 8050.')
def webapp(debug: bool, port: int) -> None:
    app = create_app()
    app.run_server(debug=debug, port=port)


@click.group()
def cli() -> None:
    pass


cli.add_command(fetch_data)
cli.add_command(webapp)


if __name__ == '__main__':
    cli()
