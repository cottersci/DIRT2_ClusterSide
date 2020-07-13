import tempfile
from os.path import join

import pytest
from irods.session import iRODSSession

from plantit_cli.executor.inprocessexecutor import InProcessExecutor
from plantit_cli.store.irodsstore import IRODSStore
from plantit_cli.run import Run

host = "irods"
port = 1247
user = "rods"
password = "rods"
zone = "tempZone"
path = f"/{zone}"
message = "Message!"
local_dir = tempfile.gettempdir()


@pytest.fixture
def session():
    return iRODSSession(host=host,
                        port=port,
                        user=user,
                        password=password,
                        zone=zone)


@pytest.fixture
def executor():
    return InProcessExecutor()


@pytest.fixture
def pipeline_with_no_inputs():
    return Run(
        identifier='no_inputs',
        api_url='',
        workdir="/test",
        image="docker://alpine:latest",
        command='echo $MESSAGE',
        params=[
            {
                'key': 'MESSAGE',
                'value': message
            }
        ]
    )


@pytest.fixture
def pipeline_with_file_inputs():
    return Run(
        identifier='file_inputs',
        api_url='',
        workdir="/test",
        image="docker://alpine:latest",
        command='echo $MESSAGE && cat $INPUT',
        params=[
            {
                'key': 'MESSAGE',
                'value': message
            }
        ],
        input={
            'kind': 'file',
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'zone': zone,
            'irods_path': join(path, "testCollection"),
        }
    )


@pytest.fixture
def pipeline_with_directory_input():
    return Run(
        identifier='directory_inputs',
        api_url='',
        workdir="/test",
        image="docker://alpine:latest",
        command='echo $MESSAGE && ls $INPUT',
        params=[
            {
                'key': 'MESSAGE',
                'value': message
            }
        ],
        input={
            'kind': 'directory',
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'zone': zone,
            'irods_path': join(path, "testCollection"),
        }
    )


def test_run_pipeline_with_no_inputs(pipeline_with_no_inputs, executor):
    executor.execute(pipeline_with_no_inputs)


def test_run_pipeline_with_file_inputs(session, pipeline_with_file_inputs, executor):
    local_file_1 = tempfile.NamedTemporaryFile()
    local_file_2 = tempfile.NamedTemporaryFile()
    local_path_1 = local_file_1.name
    local_path_2 = local_file_2.name
    remote_coll = join(path, "testCollection")
    remote_path_1 = join(remote_coll, local_file_1.name.split('/')[-1])
    remote_path_2 = join(remote_coll, local_file_2.name.split('/')[-1])

    try:
        session.collections.create(remote_coll)
        local_file_1.write(b'Input1!')
        local_file_1.seek(0)
        local_file_2.write(b'Input2!')
        local_file_2.seek(0)
        session.data_objects.put(local_path_1, remote_path_1)
        session.data_objects.put(local_path_2, remote_path_2)
        local_file_1.close()
        local_file_2.close()

        coll = session.collections.get(remote_coll)
        for obj in coll.data_objects:
            print(obj)

        executor.execute(pipeline_with_file_inputs)
    finally:
        session.collections.remove(remote_coll, force=True)


def test_run_pipeline_with_directory_input(session, pipeline_with_directory_input, executor):
    local_file_1 = tempfile.NamedTemporaryFile()
    local_file_2 = tempfile.NamedTemporaryFile()
    local_path_1 = local_file_1.name
    local_path_2 = local_file_2.name
    remote_coll = join(path, "testCollection")
    remote_path_1 = join(remote_coll, local_file_1.name.split('/')[-1])
    remote_path_2 = join(remote_coll, local_file_2.name.split('/')[-1])

    try:
        session.collections.create(remote_coll)
        local_file_1.write(b'Input1!')
        local_file_1.seek(0)
        local_file_2.write(b'Input2!')
        local_file_2.seek(0)
        session.data_objects.put(local_path_1, remote_path_1)
        session.data_objects.put(local_path_2, remote_path_2)
        local_file_1.close()
        local_file_2.close()

        coll = session.collections.get(remote_coll)
        for obj in coll.data_objects:
            print(obj)

        executor.execute(pipeline_with_directory_input)
    finally:
        session.collections.remove(remote_coll, force=True)