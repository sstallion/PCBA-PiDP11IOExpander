# Copyright (C) 2021 Steven Stallion <sstallion@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import time

from openhtf.util import conf
from openhtf_common.plugs import Aardvark, BK1785B, RequiresPlug

conf.declare(
    'fixture_psu_current',
    default_value=0.50,
    description='Current (in amps) to supply to fixture.')

conf.declare(
    'fixture_psu_voltage',
    default_value=5.0,
    description='Voltage (in volts) to supply to fixture.')

conf.declare(
    'fixture_settle_s',
    default_value=1.0,
    description='Time (in seconds) to wait after supplying power to fixture.')


class Fixture(RequiresPlug):
    """Plug that provides access to a PiDP-11 I/O Expander test fixture.

    The test fixture contains a simple interposer with discrete logic to
    connect or isolate I/O pins over GPIO and is programmed using a Total
    Phase Aardvark. Power is controlled using a B&K Precision BK1785B power
    supply over serial.

    Pin isolation is controlled using the 5V target power pins provided by the
    Aardvark. This signal is pulled down, effectively making it an additional
    GPIO output.
    """
    GPIO_A0  = 1<<2 # AA_GPIO_MISO (Pin 5)
    GPIO_A1  = 1<<3 # AA_GPIO_SCK  (Pin 7)
    GPIO_A2  = 1<<4 # AA_GPIO_MOSI (Pin 8)
    GPIO_INT = 1<<5 # AA_GPIO_SS   (Pin 9)

    GPIO_DIRECTION = GPIO_A0 | GPIO_A1 | GPIO_A2 #| GPIO_INT

    @conf.inject_positional_args
    def __init__(self, fixture_psu_current, fixture_psu_voltage, fixture_settle_s):
        super(Fixture, self).__init__(aardvark=Aardvark, psu=BK1785B)
        self.aardvark.set_gpio_direction(Fixture.GPIO_DIRECTION)
        self.psu.set_current(fixture_psu_current)
        self.psu.set_voltage(fixture_psu_voltage)
        self.psu.set_output(True)

        self.logger.debug('Waiting for DUT to settle.')
        time.sleep(fixture_settle_s)

    def connect_pins(self, pin):
        # Test probes were connected in reversed order. Rather than rewire the
        # test fixture, we account for it here:
        reversed_pin = pin ^ 0x7

        self.logger.debug('Connecting GP0 and GP1 pin %d.', pin)
        mask = sum(map(lambda x: reversed_pin & 1<<x[0] and x[1],
                       enumerate([Fixture.GPIO_A0, Fixture.GPIO_A1, Fixture.GPIO_A2])))
        self.aardvark.gpio_set(mask)
        self.aardvark.set_target_power(True)

    def isolate_pins(self):
        self.logger.debug('Isolating GP0 and GP1 pins.')
        self.aardvark.set_target_power(False)

    def has_interrupt(self):
        self.logger.debug('Checking for interrupt.')
        mask = self.aardvark.gpio_get()
        return mask & Fixture.GPIO_INT == 0

    def wait_for_interrupt(self):
        self.logger.debug('Waiting for interrupt.')
        mask = self.aardvark.gpio_get()
        while True:
            if mask & Fixture.GPIO_INT == 0:
                break
            mask = self.aardvark.gpio_wait()
