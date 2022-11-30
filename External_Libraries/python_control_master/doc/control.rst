.. _function-ref:

******************
Function reference
******************

.. Include header information from the main control module
.. automodule:: control
   :no-members:
   :no-inherited-members:
   :no-special-members:

System creation
===============
.. autosummary::
   :toctree: generated/

    ss
    tf
    frd
    rss
    drss

System interconnections
=======================
.. autosummary::
   :toctree: generated/

    append
    connect
    feedback
    negate
    parallel
    series

See also the :ref:`iosys-module` module, which can be used to create and
interconnect nonlinear input/output systems.

Frequency domain plotting
=========================

.. autosummary::
   :toctree: generated/

    bode_plot
    describing_function_plot
    nyquist_plot
    gangof4_plot
    nichols_plot
    nichols_grid

Note: For plotting commands that create multiple axes on the same plot, the
individual axes can be retrieved using the axes label (retrieved using the
`get_label` method for the matplotliib axes object).  The following labels
are currently defined:

* Bode plots: `control-bode-magnitude`, `control-bode-phase`
* Gang of 4 plots: `control-gangof4-s`, `control-gangof4-cs`,
  `control-gangof4-ps`, `control-gangof4-t`

Time domain simulation
======================

.. autosummary::
   :toctree: generated/

    forced_response
    impulse_response
    initial_response
    input_output_response
    step_response
    phase_plot

Control system analysis
=======================
.. autosummary::
   :toctree: generated/

    dcgain
    describing_function
    evalfr
    freqresp
    get_input_ff_index
    get_output_fb_index
    ispassive
    margin
    stability_margins
    phase_crossover_frequencies
    poles
    zeros
    pzmap
    root_locus
    sisotool



Matrix computations
===================
.. autosummary::
   :toctree: generated/

    care
    dare
    lyap
    dlyap
    ctrb
    obsv
    gram

Control system synthesis
========================
.. autosummary::
   :toctree: generated/

    acker
    create_statefbk_iosystem
    dlqr
    h2syn
    hinfsyn
    lqr
    mixsyn
    place
    rootlocus_pid_designer

Model simplification tools
==========================
.. autosummary::
   :toctree: generated/

    minreal
    balred
    hsvd
    modred
    era
    markov

Nonlinear system support
========================
.. autosummary::
   :toctree: generated/

    describing_function
    find_eqpt
    interconnect
    linearize
    input_output_response
    ss2io
    summing_junction
    tf2io
    flatsys.point_to_point

Stochastic system support
=========================
.. autosummary::
   :toctree: generated/

    correlation
    create_estimator_iosystem
    dlqe
    lqe
    white_noise

.. _utility-and-conversions:

Utility functions and conversions
=================================
.. autosummary::
   :toctree: generated/

    augw
    bdschur
    canonical_form
    damp
    db2mag
    isctime
    isdtime
    issiso
    issys
    mag2db
    modal_form
    observable_form
    pade
    reachable_form
    reset_defaults
    sample_system
    ss2tf
    ssdata
    tf2ss
    tfdata
    timebase
    timebaseEqual
    unwrap
    use_fbs_defaults
    use_matlab_defaults
    use_numpy_matrix
