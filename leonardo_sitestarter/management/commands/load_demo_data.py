from __future__ import unicode_literals

from optparse import make_option
from leonardo import leonardo
from django.core.management.base import BaseCommand, NoArgsCommand
from leonardo_sitestarter.scaffold_web import load_data
from leonardo_sitestarter.utils import _load_from_stream


class Command(BaseCommand):

    help = "Load all demo data, or use --names"
    option_list = NoArgsCommand.option_list + (
        make_option("-f", "--force",
                    action="store_true", dest="force", default=False,
                    help="Flush db if is already bootstraped"),
        make_option("-n", "--names",
                    action="store", dest="names", default='',
                    help="custom names"),
        make_option("--url",
                    action="store", dest="url", default=False,
                    help="url for bootstrap source"),
        make_option('--noinput',
                    action='store_false', dest='interactive', default=True,
                    help="Do NOT prompt the user for input of any kind."),
    )

    def handle(self, *args, **options):

        names = options.get('names', '')

        if not names:

            for path in leonardo.config.demo_paths:

                data = _load_from_stream(open(path, 'r'))

                load_data(data)

        self.stdout.write(
            'Demo data was successfully loaded.')
