import logging


def before_all(context):
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini".
    context.config.setup_logging(level=logging.DEBUG,
                                 filename="gemini.log",
                                 format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                                 datefmt='%a, %d %b %Y %H:%M:%S')

    # -- ALTERNATIVE: Setup logging with a configuration file.
    # context.config.setup_logging(configfile="behave_logging.ini")
