import logging


def before_all(context):
    # Based on https://behave.readthedocs.io/en/latest/api.html#some-useful-environment-ideas
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini".
    verbose_format = '%(asctime)s : %(levelno)s : %(funcName)s : %(message)s'
    context.config.setup_logging(level=logging.DEBUG,
                                 filemode='w',
                                 filename="./reports/bdd.log",
                                 format=verbose_format,
                                 datefmt='%a, %d %b %Y %H:%M:%S')

    # -- ALTERNATIVE: Setup logging with a configuration file.
    # context.config.setup_logging(configfile="behave_logging.ini")
