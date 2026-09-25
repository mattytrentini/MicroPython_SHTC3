"""Exercise the SHTC3 command sequence without a physical sensor."""

import errno
import sys
import types
import unittest

# CPython doesn't provide MicroPython's compile-time const helper.
if "micropython" not in sys.modules:
    micropython = types.ModuleType("micropython")
    micropython.const = lambda value: value
    sys.modules["micropython"] = micropython

from micropython_shtc3.shtc3 import LOW_POWER, NORMAL, SHTC3


class SensorBus:
    """Model commands the sleeping SHTC3 accepts and pending reads."""

    def __init__(self, device_id=0x87):
        self.sleeping = True
        self.pending = None
        self.commands = []
        self.device_id = device_id

    def writeto(self, address, data, stop=True):
        assert address == 0x70
        command = int.from_bytes(data, "big")
        if self.pending is not None:
            raise OSError(errno.ENODEV, "previous command has unread data")
        if command == 0x3517:  # wake up
            self.sleeping = False
        elif self.sleeping:
            raise OSError(errno.ENODEV, "sensor is asleep")
        elif command == 0xB098:  # sleep
            self.sleeping = True
        elif command in (0xEFC8, 0x7866, 0x609C):  # ID, normal, low power
            self.pending = command
        else:
            raise ValueError("unknown SHTC3 command: %#x" % command)
        self.commands.append(command)
        return len(data)

    def readfrom_into(self, address, buffer, stop=True):
        assert address == 0x70
        if self.pending == 0xEFC8:
            data = bytes((0x08, self.device_id, 0x5B))
        elif self.pending in (0x7866, 0x609C):
            # Captured SHTC3 response; both temperature and humidity CRCs pass.
            data = bytes.fromhex("66af5c85d415")
        else:
            raise OSError(errno.ENODEV, "no measurement or ID pending")
        assert len(buffer) == len(data)
        buffer[:] = data
        self.pending = None
        return len(data)


class SHTC3Tests(unittest.TestCase):
    def test_initialization_wakes_sensor_before_id_without_measuring(self):
        bus = SensorBus()
        sensor = SHTC3(bus)

        self.assertEqual(bus.commands, [0x3517, 0xEFC8])
        self.assertIsNone(bus.pending)
        self.assertEqual(sensor.power_mode, "NORMAL")

    def test_repeated_measurements_wake_and_sleep_sensor(self):
        bus = SensorBus()
        sensor = SHTC3(bus)

        for _ in range(2):
            temperature, humidity = sensor.measurements
            self.assertAlmostEqual(temperature, 25.19, places=1)
            self.assertAlmostEqual(humidity, 52.27, places=1)
            self.assertTrue(bus.sleeping)
            self.assertIsNone(bus.pending)
        self.assertEqual(bus.commands.count(0x7866), 2)

    def test_power_mode_switch_only_affects_next_measurement(self):
        bus = SensorBus()
        sensor = SHTC3(bus)
        sensor.power_mode = LOW_POWER
        self.assertEqual(bus.commands, [0x3517, 0xEFC8])

        sensor.measurements
        sensor.power_mode = NORMAL
        self.assertIsNone(bus.pending)
        sensor.measurements
        self.assertEqual([c for c in bus.commands if c in (0x609C, 0x7866)], [0x609C, 0x7866])

    def test_unexpected_id_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Failed to find SHTC3"):
            SHTC3(SensorBus(device_id=0x86))


if __name__ == "__main__":
    unittest.main()
