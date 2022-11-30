LQR control design for vertical takeoff and landing aircraft
------------------------------------------------------------

This script demonstrates the use of the python-control package for
analysis and design of a controller for a vectored thrust aircraft
model that is used as a running example through the text Feedback
Systems by Astrom and Murray. This example makes use of MATLAB
compatible commands.

Code
....
.. literalinclude:: pvtol-lqr.py
   :language: python
   :linenos:


Notes
.....

1. The environment variable `PYCONTROL_TEST_EXAMPLES` is used for
testing to turn off plotting of the outputs.
