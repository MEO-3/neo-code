import glob


def find_serial_ports() -> list[str]:
    """Return available serial ports likely connected to a ThingBot board."""
    candidates = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
    return sorted(candidates)
