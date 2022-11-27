# SHTP and SH2 HLA 

SHTP and SH2 are the Sensor Hub Transport Protocol and Sensor Hub 2 protocols from CEVA designed
to be used with sensor hub devices.

SHTP packet parser is done but the SH2 HLA only supports a small portion of the protocol. This parser
was written to test communication with the Bosch BNO085 IMU and the project only needed 3 of the many sensor reports.
The only supported reports currently are the time base, time rebase, gyroscope (calibrated), linear acceleration, and
rotation vector reports.

SH2 internally layers SH2 on top of SHTP.

## Roadmap

### SHTP

Nothing yet.

### SH2

- [ ] Display floating point result
- [ ] Add other sensor report types

## Licensing

Released under MIT license.

## Contributing

Any contributions welcome. This tool was written to facilitate testing in a capstone project in the University
of Michigan's EECS 473 Advanced Embedded Systems course and only covers the portions of SH2 that were needed.

Please open an issue for feature requests or open a pull request.
