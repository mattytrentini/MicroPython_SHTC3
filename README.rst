MicroPython SHTC3 Driver
=======================

A MicroPython driver for the Sensirion SHTC3 temperature and humidity sensor.
This maintained fork is based on the `original driver
<https://github.com/jposada202020/MicroPython_SHTC3>`_ by Jose D. Montoya
and Bryan Siepert. The original copyright and MIT license are preserved.

Installing with mip
====================
To install using mpremote

.. code-block:: shell

    mpremote mip install github:mattytrentini/MicroPython_SHTC3

To install directly using a WIFI capable board

.. code-block:: shell

    mip.install("github:mattytrentini/MicroPython_SHTC3")


Installing Library Examples
============================

If you want to install library examples:

.. code-block:: shell

    mpremote mip install github:mattytrentini/MicroPython_SHTC3/examples.json

To install directly using a WIFI capable board

.. code-block:: shell

    mip.install("github:mattytrentini/MicroPython_SHTC3/examples.json")


Usage Example
=============

On a board with I2C bus 0 configured for the sensor, including the Waveshare
ESP32-S3-RLCD-4.2:

.. code-block:: python

    from machine import I2C
    from micropython_shtc3.shtc3 import SHTC3

    sensor = SHTC3(I2C(0))
    temperature, relative_humidity = sensor.measurements
    print(temperature, relative_humidity)

Use the I2C bus and pins appropriate for other boards. Measurements wake the
sensor and return it to sleep. See ``examples/`` for power-mode selection and
``docs/api.rst`` for the API reference.
