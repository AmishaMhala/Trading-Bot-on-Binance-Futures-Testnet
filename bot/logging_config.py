import logging


def configure_logging(logfile: str = "trading_bot.log"):
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def get_logger(name: str = None):
    return logging.getLogger(name)
