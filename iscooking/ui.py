import click

from iscooking.setup import setupTable
from iscooking.shopping import makeShoppping

@click.command()
@click.argument('key', type=str)
@click.option('--start', type=click.DateTime(formats=["%d.%m.%Y"]),
    help="First day of cooking")
@click.option('--end', type=click.DateTime(formats=["%d.%m.%Y"]),
    help="First last day of cooking")
def setup(key, start, end):
    """
    Setup a new table for cooking
    """
    setupTable(key, start, end)

@click.command()
@click.argument('key', type=str)
@click.argument('shoppingname', type=str)
def shopping(key, shoppingname):
    """
    Generate a shopping list
    """
    makeShoppping(key, shoppingname)



@click.group()
def cli():
    """
    IS Cooking table manager
    """
    pass

cli.add_command(setup)
cli.add_command(shopping)

if __name__ == "__main__":
    cli()
