import logging

def get_logger():
    logger = logging.getLogger("metric_logger")
    logger.setLevel(logging.INFO)

    # Prevent logs from going to root (FastAPI/Uvicorn)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler("metric.log")

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = get_logger()