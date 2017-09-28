# ardu-acqua-test

Proof of concept for water quality measurements at the flussbad-berlin project.

## Basic Idea

An Arduino Mega 2650 controls a pump and some warn leds and sends the
collected sensor data over the serial line in form of a JSON array
(following a schema definition). An example output can be found
in the 'examples' folder, the JSON Schema is stored in the 'schema' folder
respectively.

## And Now?

The data can then be consumed / post-processed with:
https://github.com/zwischenloesung/ardu-report

For 'ardu-report' only two elements are mandatory, some identifier
and a value.

There is a meta schema for the schema, so any arduino project
that generates JSON arrays following a schema which validates against
the meta schema can use 'ardu-report'...

