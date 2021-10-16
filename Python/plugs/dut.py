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

from array import array

from openhtf import conf
from openhtf_common.plugs import Aardvark, RequiresPlug

conf.declare('dut_i2c_address',
             default_value=0x20,
             description='I2C address of DUT.')

conf.declare('dut_i2c_bitrate',
             default_value=100,
             description='I2C bit rate (in kHz) for DUT.')

conf.declare('dut_i2c_pullups',
             default_value=True,
             description='Enable I2C pullups for DUT.')


class DUT(RequiresPlug):
    """Plug that provides access to a PiDP-11 I/O Expander DUT.

    The heart of the DUT is a Microchip MCP23016 I/O expander that
    communicates over I2C and is programmed using a Total Phase Aardvark.
    """
    NUMBER_OF_PORTS = 2
    NUMBER_OF_PINS_PER_PORT = 8

    @staticmethod
    def enumerate_ports():
        """Returns an iterator of tuples containing the primary port number
        followed by the secondary (eg. opposing) port number.
        """
        return zip(range(DUT.NUMBER_OF_PORTS), reversed(range(DUT.NUMBER_OF_PORTS)))

    @staticmethod
    def enumerate_pins():
        """Returns an interator of tuples containing the pin number followed
        by its bitmask.
        """
        return enumerate(map(lambda x: 1<<x, range(DUT.NUMBER_OF_PINS_PER_PORT)))

    @conf.inject_positional_args
    def __init__(self, dut_i2c_address, dut_i2c_bitrate, dut_i2c_pullups):
        super(DUT, self).__init__(aardvark=Aardvark)
        self._i2c_address = dut_i2c_address
        self.aardvark.set_i2c_bitrate(dut_i2c_bitrate)
        self.aardvark.set_i2c_pullups(dut_i2c_pullups)

    def get_data(self, port):
        self.logger.debug('Getting data for GP%d.', port)
        return self.aardvark.i2c_read_register(self._i2c_address, 0x00+port, 1)[0]

    def set_data(self, port, mask):
        self.logger.debug('Setting data for GP%d to 0x%02x.', port, mask)
        self.aardvark.i2c_write(self._i2c_address, array('B', [0x00+port, mask]))

    def get_direction(self, port):
        self.logger.debug('Getting direction for GP%d.', port)
        return self.aardvark.i2c_read_register(self._i2c_address, 0x06+port, 1)[0]

    def set_direction(self, port, mask):
        self.logger.debug('Setting direction for GP%d to 0x%02x.', port, mask)
        self.aardvark.i2c_write(self._i2c_address, array('B', [0x06+port, mask]))

    def get_interrupt_capture(self, port):
        self.logger.debug('Getting interrupt capture for GP%d.', port)
        return self.aardvark.i2c_read_register(self._i2c_address, 0x08+port, 1)[0]

    def clear_interrupt(self):
        self.logger.debug('Clearing interrupt.')
        for port, _ in DUT.enumerate_ports():
            self.get_interrupt_capture(port)
