# Flighgear Orchestrator

A cross-platform tool that allows you to co-ordinate a multi-pc [FlightGear] session,
generally in accordance with these articles:

- [The FlightGear Flight Simulator], Alexander R. Perry, section on ['Simulating the Pilot's view']
- Flightgear Wiki: [Howto:Multi-computing FlightGear]
- Flightgear Wiki: [Slaving for Dummies]
- Flightgear Wiki: [Property Tree/Sockets]
- Flightgear Wiki: [Property Tree/Native Protocol Slaving]
- [Multiple Monitors in FlightGear: Quick and Dirty]

## Installation & Running

1. Create a virtualenv: `python3 -m venv venv`
2. Activate the virtualenv:

   Windows: `.\venv\Scripts\activate.bat`

   Linux/OSX: `source ./venv/bin/activate`

3. Install with `pip install -e .`
4. Initially, and when indicated on upgrade, run `fgo setup`
5. In one console, start up agent with `fgo agent`.
6. In a second console, activate the virtualenv ands tart up director with `fgo director`.

Or run `--help` see options.

## Dependencies

- Flightgear
- Subversion (for downloading and updating aircraft)
- Python 3.7+ with virtualenv

### Windows 10

Suggest to install the following:

1. [Python 3.7 x64 web installer]

2. [TortoiseSVN], choose the option to install command line tools

### Ubuntu 20.04

`sudo apt install libxml2-dev libxslt-dev python3-dev python3-pip python3-venv python3-wheel`

### OSX

Use homebrew to install the packages above.

## Development Documentation

See [Development documentation].

## Credits and License

Contains icons by [Yusuke Kamiyamane](http://p.yusukekamiyamane.com/).

Licensed under the [GNU GPLv3].

['simulating the pilot's view']: https://www.usenix.org/legacy/publications/library/proceedings/usenix04/tech/sigs/full_papers/perry/perry_html/Simulating_Pilot_s.html
[the flightgear flight simulator]: https://www.usenix.org/legacy/publications/library/proceedings/usenix04/tech/sigs/full_papers/perry/perry_html/fgfs.html
[howto:multi-computing flightgear]: http://wiki.flightgear.org/Howto:Multi-computing_FlightGear
[slaving for dummies]: http://wiki.flightgear.org/Slaving_for_Dummies
[property tree/sockets]: http://wiki.flightgear.org/Property_Tree/Sockets
[flightgear]: http://home.flightgear.org/
[development documentation]: ./README-dev.md
[gnu gplv3]: ./LICENSE.txt
[tortoisesvn]: https://tortoisesvn.net/
[python 3.7 x64 web installer]: https://www.python.org/downloads/release/python-372/
[multiple monitors in flightgear: quick and dirty]: http://www.inkdrop.net/dave/multimon.pdf
[property tree/native protocol slaving]: http://wiki.flightgear.org/Property_Tree/Native_Protocol_Slaving
