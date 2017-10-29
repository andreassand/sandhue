import logging

FORMAT = 'SANDHUE %(asctime)-15s %(levelname)s:\t%(message)s'

logging.basicConfig(format=FORMAT)

log = logging.getLogger("sandhue logger")
log.setLevel(logging.INFO)