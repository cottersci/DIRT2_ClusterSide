"""
    Bridge between the DIRT2 web platform and the cluster.
"""

import subprocess
import argparse
import json
import sys

from clusterside.comms import Comms

class ClusterSide:
    """
        Bridge between the DIRT2 web platform and the cluster.
    """

    # Configuration loaded form the Job config json file. Populated by main()
    config = {}

    # Server communication object
    server = None

    def __init__(self, args):
        """
            Main Program Function
        """
        parser = argparse.ArgumentParser(
            description='The Cluster Side Component of the DIRT2 Webplatform'
        )
        parser.add_argument('cmd', type=str,
                            help='URL of singularity container to run')
        parser.add_argument('--config', type=str, default="./job_config.json",
                            help="Job config file")
        parser.add_argument('--url', type=str, default="http://localhost/jobs/api/",
                            help="Sever url")
        args, unknownargs = parser.parse_known_args(args)

        with open(args.config, 'r') as fin:
            self.config = json.load(fin)

        self.server = Comms(url=args.url,
                            headers={
                                "Authorization": "Token "  + self.config['auth_token']
                            },
                            job_pk=self.config['job_pk'])

        if args.cmd == "submit":
            self.submit(unknownargs)
        elif args.cmd == "run":
            self.run()

    def submit(self, args):
        """
            Submit a job to the cluster

            Args:
                args: command line input arguments to parse
        """
        parser = argparse.ArgumentParser(description='Submit a job to the cluster')
        parser.add_argument('--script', type=str,
                            default="~/.clusterside/submit.sh",
                            help='Script template location')
        opts = parser.parse_args(args)

        script_name = "./submit_%d"%(self.config['job_pk'],)

        with open(opts.script, 'r') as fin, open(script_name, 'w') as fout:
            for line in fin:
                fout.write(line.format(**self.config))

        try:
            ret = subprocess.run(["qsub", script_name])
        except FileNotFoundError as error:
            self.server.update_status(self.server.FAILED, str(error))
            print(error)
            exit()

        if ret.returncode == 0:
            self.server.update_status(self.server.OK, "Queued")

            if ret.stdout:
                print(ret.stdout)

        if ret.stderr:
            self.server.update_status(self.server.FAILED, ret.stderr)

    def run(self):
        """
            Run the job task
        """
        self.server.update_status(self.server.OK, "Running")

        ret = subprocess.run(["singularity",
                              "run",
                              "--containall",
                              "--home `pwd`",
                              self.config['singulairty_url'],
                              *self.config['parameters']
                             ])

        if ret.returncode == 0:
            self.server.task_complete(self.config['task_pk'])
        elif ret.stderr:
            self.server.update_status(self.server.FAILED, ret.stderr)

        if ret.stderr:
            with open(self.config['job_pk'] + ".stderr", 'w') as fout:
                fout.write(ret.stderr)
        if ret.stdout:
            with open(self.config['job_pk'] + ".stdout", 'w') as fout:
                fout.write(ret.stdout)

def cli():
    '''Entry point used by setup.'''
    ClusterSide(sys.argv[1:])

if __name__ == "__main__":
    ClusterSide(sys.argv[1:])
