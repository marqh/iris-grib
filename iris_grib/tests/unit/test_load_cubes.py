# (C) British Crown Copyright 2014 - 2016, Met Office
#
# This file is part of iris-grib.
#
# iris-grib is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iris-grib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with iris-grib.  If not, see <http://www.gnu.org/licenses/>.
"""Unit tests for the `iris_grib.load_cubes` function."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import iris_grib.tests as tests

import iris
import iris.fileformats.rules

import iris_grib
import iris_grib.load_rules
from iris_grib import load_cubes
from iris.tests import mock


class TestToggle(tests.IrisGribTest):
    def _test(self, mode, generator, converter):
        # Ensure that `load_cubes` defers to
        # `iris_grib.load_cubes`, passing a correctly
        # configured `Loader` instance.
        with iris.FUTURE.context(strict_grib_load=mode):
            with mock.patch('iris.fileformats.rules.load_cubes') as rules_load:
                rules_load.return_value = mock.sentinel.RESULT
                result = load_cubes(mock.sentinel.FILES,
                                    mock.sentinel.CALLBACK,
                                    mock.sentinel.REGULARISE)
                if mode:
                    kw_args = {}
                else:
                    kw_args = {'auto_regularise': mock.sentinel.REGULARISE}
                loader = iris.fileformats.rules.Loader(
                    generator, kw_args,
                    converter, None)
                rules_load.assert_called_once_with(mock.sentinel.FILES,
                                                   mock.sentinel.CALLBACK,
                                                   loader)
                self.assertIs(result, mock.sentinel.RESULT)

    def test_sloppy_mode(self):
        # Ensure that `load_cubes` uses:
        #   iris_grib.grib_generator
        #   iris_grib.load_rules.convert
        self._test(False, iris_grib.grib_generator,
                   iris_grib.load_rules.convert)

    def test_strict_mode(self):
        # Ensure that `load_cubes` uses:
        #   iris_grib.message.GribMessage.messages_from_filename
        #   iris_grib._load_convert.convert
        self._test(
            True,
            iris_grib.message.GribMessage.messages_from_filename,
            iris_grib._load_convert.convert)


@tests.skip_data
class Test_load_cubes(tests.IrisGribTest):

    def test_reduced_raw(self):
        # Loading a GRIB message defined on a reduced grid without
        # interpolating to a regular grid.
        gribfile = tests.get_data_path(
            ("GRIB", "reduced", "reduced_gg.grib2"))
        grib_generator = load_cubes(gribfile, auto_regularise=False)
        self.assertCML(next(grib_generator))


if __name__ == "__main__":
    tests.main()