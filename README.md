# PiDP-11 I/O Expander PCBA

This repository contains the PCBA design files for a 16-bit TTL compatible I/O
expander for the [PiDP-11][1] and [Raspberry Pi][2]. Design files are intended
to be viewed using [Altium Designer][3]. Releases may also be uploaded to the
standalone [Altium 365 Viewer][4] for free.

Project documentation is hosted on [Hackaday][5] and assembled boards are
available for purchase from [Tindie][6].

![Test Fixture](PiDP11IOExpander_Fixture.jpeg)

## Details

A test fixture was created to support functional testing of PCBs. The fixture is
based on a [Merifix MF300][7] with a custom interposer controlled by a [Total
Phase Aardvark][8] and a [B&K Precision 1785B][9] benchtop power supply.
Functional tests were developed in Python using the [OpenHTF][10] hardware
testing framework.

To execute functional tests, follow these steps:

1. Install the [Chocolatey][11] package manager for Windows.
2. Using Windows Explorer, navigate to the `Python` folder and right click on
   the `setup.cmd` command file and select `Run as administrator`. This will
   install dependencies and create a Python virtual environment for testing.
3. Double click on the `fct_station.cmd` command file in the `Python` folder to
   start the FCT test station.
4. You can interact with the test station from either the command window, or by
   pointing a browser to http://localhost:4444.
5. Enter the DUT serial number to begin testing using the keyboard or hand
   scanner (eg. Symbol LS2208).

For more details, see the latest release on [GitHub][12].

## Contributing

Pull requests are welcome! See [CONTRIBUTING.md] for more details.

## License

Source code in this repository is licensed under a Simplified BSD License. See
[LICENSE.txt] for more details.

[1]: https://obsolescence.wixsite.com/obsolescence/pidp-11
[2]: https://www.raspberrypi.org/
[3]: https://www.altium.com/altium-designer/
[4]: https://www.altium.com/viewer/
[5]: https://hackaday.io/project/181311
[6]: https://www.tindie.com/products/24781
[7]: https://www.merifix.com/docs/Merifix-MF300-Brochure.pdf
[8]: https://www.totalphase.com/products/aardvark-i2cspi/
[9]: https://www.bkprecision.com/products/power-supplies/1785B-0-18vdc-0-5a-programmable-dc-supply-w-rs232-interface.html
[10]: https://github.com/google/openhtf
[11]: https://chocolatey.org/install
[12]: https://github.com/sstallion/PCBA-PiDP11IOExpander/releases/latest

[CONTRIBUTING.md]: CONTRIBUTING.md
[LICENSE.txt]: LICENSE.txt
