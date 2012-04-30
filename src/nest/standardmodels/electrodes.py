"""
Current source classes for the nest module.

Classes:
    DCSource           -- a single pulse of current of constant amplitude.
    StepCurrentSource  -- a step-wise time-varying current.
    NoisyCurrentSource -- a Gaussian whitish noise current.
    ACSource           -- a sine modulated current.


:copyright: Copyright 2006-2012 by the PyNN team, see AUTHORS.
:license: CeCILL, see LICENSE for details.

$Id: electrodes.py 991 2011-09-30 13:05:02Z apdavison $
"""

import nest
from pyNN.standardmodels import electrodes, build_translations, StandardCurrentSource
from pyNN.common import Population, PopulationView, Assembly
from pyNN.parameters import ParameterSpace, Sequence


class NestCurrentSource(StandardCurrentSource):
    """Base class for a nest source of current to be injected into a neuron."""

    def __init__(self, parameters):
        self._device   = nest.Create(self.nest_name)
        self.cell_list = []
        parameter_space = ParameterSpace(self.default_parameters,
                                         self.get_schema(),
                                         size=1)
        parameter_space.update(**parameters)
        parameter_space = self.translate(parameter_space)
        parameter_space.evaluate(simplify=True)
        self.set_native_parameters(parameter_space.as_dict())

    def inject_into(self, cells):
        __doc__ = StandardCurrentSource.inject_into.__doc__
        for id in cells:
            if id.local and not id.celltype.injectable:
                raise TypeError("Can't inject current into a spike source.")
        if isinstance(cells, (Population, PopulationView, Assembly)):
            self.cell_list = [cell for cell in cells]
        else:
            self.cell_list = cells
        nest.DivergentConnect(self._device, self.cell_list)

    def set_native_parameters(self, parameters):
        for key, value in parameters.items():
            if key == "amplitude_values":
                assert isinstance(value, Sequence)
                nest.SetStatus([self._device], {key : value.value, 'amplitude_times' : parameters["amplitude_times"].value})
            elif not key == "amplitude_times":
                nest.SetStatus([self._device], {key : float(value)})

    def get_native_parameters(self):
        return nest.GetStatus([self._device])[0]


class DCSource(NestCurrentSource, electrodes.DCSource):
    __doc__ = electrodes.DCSource.__doc__

    translations = build_translations(
        ('amplitude',  'amplitude', 1000.),
        ('start',      'start'),
        ('stop',       'stop')
    )
    nest_name = 'dc_generator'


class ACSource(NestCurrentSource, electrodes.ACSource):
    __doc__ = electrodes.ACSource.__doc__

    translations = build_translations(
        ('amplitude',  'amplitude', 1000.),
        ('start',      'start'),
        ('stop',       'stop'),
        ('frequency',  'frequency'),
        ('offset',     'offset',    1000.),
        ('phase',      'phase')
    )
    nest_name = 'ac_generator'


class StepCurrentSource(NestCurrentSource, electrodes.StepCurrentSource):
    __doc__ = electrodes.StepCurrentSource.__doc__

    translations = build_translations(
        ('amplitudes',  'amplitude_values', 1000.),
        ('times',       'amplitude_times')
    )
    nest_name = 'step_current_generator'


class NoisyCurrentSource(NestCurrentSource, electrodes.NoisyCurrentSource):
    __doc__ = electrodes.NoisyCurrentSource.__doc__

    translations = build_translations(
        ('mean',  'mean', 1000.),
        ('start', 'start'),
        ('stop',  'stop'),
        ('stdev', 'std', 1000.),
        ('dt',    'dt')
    )
    nest_name = 'noise_generator'