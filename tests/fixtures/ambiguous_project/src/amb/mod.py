import click
from fastapi import FastAPI

app = FastAPI()


@click.command()
def cli():
    print('hi')
