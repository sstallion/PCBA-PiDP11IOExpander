# Copyright (c) 2021 Steven Stallion
# All rights reserved.
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

from plugs import DUT, Fixture

import openhtf as htf
from openhtf.output.callbacks import json_factory
from openhtf.util import conf, units
from openhtf_common.plugs import Aardvark, BK1785B
from openhtf_common.util import measurements, monitors, tests, validators


@htf.plug(dut=DUT)
@htf.plug(fixture=Fixture)
def setup_phase(test, dut, fixture):
    # A dedicated test phase is needed to initialize Fixture and DUT plugs.
    # This is needed to work around an issue with monitors that requires all
    # plugs are initialized before creating the monitor function.
    pass


@monitors.plug(psu=BK1785B, poll_interval_ms=500)
@htf.plug(dut=DUT)
@htf.plug(fixture=Fixture)
def main_phase(test, dut, fixture):
    for test_cycle in tests.generate_test_cycles():
        # When isolated on the text fixture, each pin is is pulled down
        # independently. If either port returns a non-zero value other than
        # the pin set, a short is present.
        test.logger.info('%s: Checking I/O for short circuits.', test_cycle)
        for primary, secondary in DUT.enumerate_ports():
            for pin, mask in DUT.enumerate_pins():
                fixture.isolate_pins()
                dut.set_direction(secondary, 0xff)
                dut.set_direction(primary, ~mask&0xff)
                dut.set_data(primary, 0x00)

                dut.clear_interrupt()
                dut.set_data(primary, mask)

                assert not fixture.has_interrupt()
                assert dut.get_data(primary) == mask
                assert dut.get_data(secondary) == 0x00

        # When connected through the bilateral switches on the test fixture,
        # both ports should return the same value with an interrupt on change.
        test.logger.info('%s: Checking I/O for open circuits.', test_cycle)
        for primary, secondary in DUT.enumerate_ports():
            for pin, mask in DUT.enumerate_pins():
                fixture.isolate_pins()
                dut.set_direction(secondary, 0xff)
                dut.set_direction(primary, ~mask&0xff)
                dut.set_data(primary, 0x00)
                fixture.connect_pins(pin)

                dut.clear_interrupt()
                dut.set_data(primary, mask)

                fixture.wait_for_interrupt()
                assert dut.get_data(primary) == mask
                assert dut.get_data(secondary) == mask


@htf.measures(htf.Measurement('current').with_dimensions(units.MILLISECOND)
              .with_units(units.AMPERE).dim_in_range(0.00, 0.10))
@htf.measures(htf.Measurement('voltage').with_dimensions(units.MILLISECOND)
              .with_units(units.VOLT).dim_in_range(4.50, 5.50))
def validate_phase(test):
    # Monitors do not have a good method for validating measured values. A
    # dedicated test phase is needed to unpack collected measurements.
    # See: https://github.com/google/openhtf/issues/766.
    psu_measurement = test.get_measurement('psu')
    measurements.copy_values(psu_measurement, test.measurements['current'],
                             BK1785B.measurement_to_current)
    measurements.copy_values(psu_measurement, test.measurements['voltage'],
                             BK1785B.measurement_to_voltage)


if __name__ == '__main__':
    test = htf.Test(
        setup_phase, main_phase, validate_phase,
        test_name='fct_test', test_description='PiDP-11 I/O Expander FCT',
        test_version='1.0.0')

    test.add_output_callbacks(json_factory.OutputToJSON(
        tests.get_output_filename('{dut_id}.{metadata[test_name]}.json')))

    # Ensure Aardvark and BK1785B plugs are initialized before prompting the
    # operator to put the test fixture in a known state:
    tests.execute_with_plugs(test, aardvark=Aardvark, psu=BK1785B)
