# Flighgear Orchestrator

A cross-platform tool that allows you to co-ordinate a multi-pc [FlightGear] session,
generally in accordance with these articles:

* [The FlightGear Flight Simulator], Alexander R. Perry, section on ['Simulating the Pilot's view']
* Flightgear Wiki: [Howto:Multi-computing FlightGear]
* Flightgear Wiki: [Slaving for Dummies]
* Flightgear Wiki: [Property Tree/Sockets]

## Dependencies

* Flightgear
* Subversion (for downloading and updating aircraft)
* Python 3.7+ with virtualenv

### Windows

Suggest to install the following:

1. [Python 3.7 x64 web installer]

2. [TortoiseSVN], choose the option to install command line tools

### Ubuntu

`sudo apt install python3.7 python3.7-venv`

### OSX

Use homebrew to install the packages above.

## Development Documentation

See [Development documentation]. 

## Credits and License
Contains icons by [Yusuke Kamiyamane].

Licensed under the [GNU GPLv3].

['Simulating the Pilot's view']: (https://www.usenix.org/legacy/publications/library/proceedings/usenix04/tech/sigs/full_papers/perry/perry_html/Simulating_Pilot_s.html)
[The FlightGear Flight Simulator]: (https://www.usenix.org/legacy/publications/library/proceedings/usenix04/tech/sigs/full_papers/perry/perry_html/fgfs.html)
[Howto:Multi-computing FlightGear]: (http://wiki.flightgear.org/Howto:Multi-computing_FlightGear)
[Slaving for Dummies]: (http://wiki.flightgear.org/Slaving_for_Dummies)
[Property Tree/Sockets]: (http://wiki.flightgear.org/Property_Tree/Sockets)
[FlightGear]: (http://home.flightgear.org/)
[Development documentation]: (./README-dev.md)
[Yusuke Kamiyamane]: (http://p.yusukekamiyamane.com/)
[GNU GPLv3]: (./LICENSE.txt)
[TortoiseSVN]: (https://tortoisesvn.net/)
[Python 3.7 x64 web installer]: (https://www.python.org/downloads/release/python-372/)