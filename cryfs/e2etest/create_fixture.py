import click
import asyncio
import tempfile
from cryfs.e2etest.utils.tar import TarFile
from cryfs.e2etest.fsmounter import CryfsMounter


@click.command()
@click.argument('source_dir')
@click.argument('target_tar')
def create_data_tar(source_dir: str, target_tar: str) -> None:
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(_create_data_tar(source_dir, target_tar))
    finally:
        event_loop.close()


async def _create_data_tar(source_dir: str, target_tar: str) -> None:
    await TarFile(target_tar).pack(source_dir, compress=True)


@click.command()
@click.argument('source_data_tar')
@click.argument('target_encoded_tar')
@click.option('--cryfs-executable', default="/usr/bin/cryfs")
@click.option('--password', default='mypassword')
def create_encoded_tar(source_data_tar: str, target_encoded_tar: str, cryfs_executable: str, password: str) -> None:
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(_create_encoded_tar(source_data_tar=source_data_tar, target_encoded_tar=target_encoded_tar, cryfs_executable=cryfs_executable, password=password))
    finally:
        event_loop.close()


async def _create_encoded_tar(source_data_tar: str, target_encoded_tar: str, cryfs_executable: str, password: str) -> None:
    with tempfile.TemporaryDirectory() as basedir:
        async with CryfsMounter(cryfs_executable).mount(basedir=basedir, password=password.encode('UTF-8')) as mountdir:
            await TarFile(source_data_tar).unpack(mountdir)
        await TarFile(target_encoded_tar).pack(basedir)
