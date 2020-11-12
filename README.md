<p align="center">
<img src="https://github.com/Computational-Plant-Science/plantit/blob/master/plantit/front_end/src/assets/logo.png?raw=true" />
</p>

# PlantIT CLI

[![PyPI version](https://badge.fury.io/py/plantit-cli.svg)](https://badge.fury.io/py/plantit-cli) [![Build Status](https://travis-ci.com/Computational-Plant-Science/plantit-cli.svg?branch=master)](https://travis-ci.com/Computational-Plant-Science/plantit-cli) [![Coverage Status](https://coveralls.io/repos/github/Computational-Plant-Science/plantit-cli/badge.png?branch=master)](https://coveralls.io/github/Computational-Plant-Science/plantit-cli) 

Deploy workflows on laptops, servers, or HPC/HTC clusters.

**This project is in open alpha and is not yet stable.**

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Contents**

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Input/Output](#inputoutput)
  - [Authenticating against the Terrain API](#authenticating-against-the-terrain-api)
- [Examples](#examples)
- [Tests](#tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Requirements


- Python 3.6.9+
- [Singularity](https://sylabs.io/docs/)

## Installation

To install, clone the project with `git clone https://github.com/Computational-Plant-Science/plantit-cli.git` or use pip:

```
pip3 install plantit-cli
```

## Usage

To run `hello_world.yaml`, use `plantit hello_world.yaml`. The YAML schema should look something like this:

```yaml
identifier: a42033c3-9ba1-4d99-83ed-3fdce08c706e # run identifier (required)
image: docker://alpine                           # Docker or Singularity image (required)
workdir: /your/working/directory                 # working directory (required)
command: echo $MESSAGE                           # command to run in container (required)
params:                                          # parameters substituted when `command` is run (optional)
- key: message
  value: Hello, plant person!
```

### Input/Output

The CLI can automatically copy files from the CyVerse Data Store to the local (or network) file system before your code runs, then push output files back to the Data Store afterwards.

Runs involving inputs and outputs fall into 3 categories:

- pull a file from the Data Store and spawn a single container to process it
- pull a directory from the Data Store and spawn a single container to process it
- pull a directory from the Data Store and spawn multiple containers, one for each file

To pull a file or directory, add an `input` section (the file or directory name will be substituted for `$INPUT` when `command` is invoked).

#### 1 File, 1 Container

To pull a file from the Data Store and spawn a single container to process it, use `kind: file` and `from: <file path>`:

```yaml
input:
  kind: file
  from: /iplant/home/username/directory/file
```

#### 1 Directory, 1 Container

To pull the contents of a directory from the Data Store and spawn a single container to process it, use `kind: directory` and `from: <directory path>`:

```yaml
input:
  kind: directory
  from: /iplant/home/username/directory
```

#### 1 Directory, 1+ Container(s)

To pull a directory from the Data Store and spawn a container for each file, use `kind: file` and `from: <directory path>`:

```yaml
input:
  kind: file
  from: /iplant/home/username/directory
```

To push files matching a pattern back to the Data Store after your container executes (the local path will be substituted for `$OUTPUT` when `command` runs):

```yaml
output:
  pattern: xslx
  from: directory # relative to the working directory
  to: /iplant/home/username/collection
```

### Authenticating with the Terrain API

The CLI uses the Terrain API to access the CyVerse Data Store. Runs with inputs and outputs must provide a `--cyverse_token` argument. For instance, to run `hello_world.yaml`:

```shell script
plantit hello_world.yaml --cyverse_token 'eyJhbGciOiJSUzI1N...'
```

A CyVerse access token can be obtained from the Terrain API with a `GET` request (providing username/password for basic auth):

```shell script
GET https://de.cyverse.org/terrain/token/cas
```

## Examples

Sample definition files can be found in `examples/`.

## Tests

Before running tests, run `scripts/bootstrap.sh` (this will pull/build images for a small `docker-compose` SLURM cluster test environment). Then run:

```docker-compose -f docker-compose.test.yml exec slurmctld python3 -m pytest /opt/plantit-cli -s```

Tests invoking the Terrain API may take some time to complete; they're rigged with a delay to allow writes to propagate from Terrain to the CyVerse Data Store (some pass/fail non-determinism occurs otherwise).
