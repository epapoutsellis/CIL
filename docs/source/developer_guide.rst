.. Copyright 2020 United Kingdom Research and Innovation
   Copyright 2020 The University of Manchester
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   Authors:
   CIL Developers, listed at: https://github.com/TomographicImaging/CIL/blob/master/NOTICE.txt
   Kyle Pidgeon (UKRI-STFC)

Developers' Guide
*****************

CIL is an Object Orientated software. It has evolved during the years and it currently does not fully adhere to the following conventions. New additions must comply with
the following.

Conventions on new CIL objects
==============================

For each class there are **essential**, and **non-essential** parameters. The non-essential can be further be divided in **often configured** and **advanced** parameters:

* essential
* non-essential

  * often-configured
  * advanced

The definition of what are the essential, often-configured and advanced parameters depends on the actual class.

Creator
-------

To create an instance of a class, the creator of a class should require the **essential** and **often-configured** parameters as named parameters.

It should not accept positional arguments `*args` or key-worded arguments `**kwargs` so that the user can clearly understand what parameters are necessary to
create the instance.

Setter methods and properties
-----------------------------

Use of `property` is favoured instead of class members to store parameters so that the parameters can be protected.

The class should provide setter methods to change all the parameters at any time. Setter methods to set multiple parameters at the same time is also accepted.
Setter methods should be named `set_<parameter>`. The use of `set_` helps IDEs and user to find what they should change in an instance of a class.


Other methods
-------------

Methods that are not meant to be used by the user should have a `_` (underscore) at the beginning of the name.
All methods should follow the convention of small caps underscore separated words.

Logging and warning
===================
We follow pythons convention on logging (see e.g. https://docs.python.org/3/howto/logging.html). In particular:

.. list-table:: Logging and warning guidelines
   :header-rows: 1
   :widths: 40 60

   * - Task you want to perform
     - The best tool for the task
   * - Display console output for ordinary usage of a command line script or program
     - ``print()``
   * - Report events that occur during normal operation of a program
       (e.g. for status monitoring or fault investigation)
     - A logger’s ``info()`` (or ``debug()`` method for very detailed output for diagnostic purposes)
   * - Issue a warning regarding a particular runtime event
     - ``warnings.warn()``  if the issue is avoidable and the user's code
       should be modified to eliminate the warning.

       A logger’s ``warning()`` method if there is nothing the user can do about
       the situation, but the event should still be noted
   * - Report an error regarding a particular runtime event
     - Raise an exception


Documentation
=============

Docstrings
----------

The Core Imaging Library (CIL) follows the `NumpyDoc <https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard>`_
style with the `PyData Sphinx HTML theme <https://pydata-sphinx-theme.readthedocs.io/en/latest/>`_.
When contributing your code please refer to `this <https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard>`_ link
for docstring formatting and this rendered `example <https://numpydoc.readthedocs.io/en/latest/example.html#example>`_.

Example from ``cil``
^^^^^^^^^^^^^^^^^^^^

The following provides an example of the docstring format used within ``cil``, and the rendered documentation generated from it.

Source
""""""

.. literalinclude:: ../../Wrappers/Python/cil/recon/FBP.py
   :caption: `FBP.run method from cil.io.recon.FBP`
   :language: python
   :pyobject: FBP.run

Rendered
""""""""

.. automethod:: cil.recon.FBP.FBP.run


Building documentation locally
------------------------------

The easiest way to test documentation changes is to open a pull request and `download the rendered documentation from the CI <https://github.com/TomographicImaging/CIL/blob/master/.github/workflows/README.md>`_.

Alternatively, to build the docs locally, you will need a working ``cil`` installation.
For development of the documentation embedded within the source code itself (e.g. docstrings), you should build ``cil`` from source.

The following steps can be used to create an environment that is suitable for building ``cil`` and its documentation, and to start
a HTTP server to view the documentation.

#. Clone ``cil`` repo
#. Update conda with ``conda update -n base -c defaults conda``
#. Follow the instructions `here <https://github.com/TomographicImaging/CIL/tree/master#building-cil-from-source-code>`_ to create a conda environment and build ``cil`` from source
#. Go to ``docs`` folder
#. Install packages from ``docs_environment.yml``
#. `Install Ruby version 3.2 <https://www.ruby-lang.org/en/documentation/installation/#installers>`_
#. Install the web dependencies with ``make web-deps``
#. Build the documentation with ``make dirhtml web``
#. Start an HTTP server with ``make serve`` to access the docs via `localhost:8000 <http://localhost:8000>`_.

Example:
::
  git clone --recurse-submodule git@github.com:TomographicImaging/CIL
  cd CIL
  sh scripts/create_local_env_for_cil_development_tests.sh -n NUMPY_VERSION -p PYTHON_VERSION -e ENVIRONMENT_NAME
  conda activate ENVIRONMENT_NAME
  pip install .
  cd docs
  conda update -n base -c defaults conda
  conda env update -f docs_environment.yml # with the name field set to ENVIRONMENT_NAME
  make web-deps  # install dependencies (requires ruby 3.2)
  make dirhtml web serve

Notebooks gallery
-----------------

The ``mkdemos.py`` script (called by ``make dirhtml``):

- downloads notebooks from external URLs to ``source/demos/*.ipynb``
- uses the ``demos-template.rst`` file to generate the gallery in ``source/demos.rst``

The ``nbsphinx`` extension will convert the ``*.ipynb`` files to HTML.


Testing
=======

Parametrized Tests
------------------
Methods are tested using Python's `unittest <https://docs.python.org/3/library/unittest.html>`_ library. Please see the documentation `here <https://docs.python.org/3/library/unittest.html#basic-example>`_  for information and usage examples.
The `unittest-parametrize <https://github.com/adamchainz/unittest-parametrize>`_ library is used to generate parametrized test cases.

The ``@parametrize`` decorator allows you to define multiple sets of input parameters for a single test method, treating each combination as a separate test case.
This helps to test various scenarios without duplicating code.

Example: Parameterized Test for ``ProjectionOperator``

.. code:: python
   @parametrize("device, raise_error, err_type",
     [param('cpu', False, None, id="cpu_NoError"),
      param('CPU', False, None, id="CPU_NoError"),
      param('InvalidInput', True, ValueError, id="InvalidInput_ValueError")])

   def test_ProjectionOperator_2Ddata(self, device, raise_error: bool, err_type):
       if raise_error:
           with self.assertRaises(err_type):
               ProjectionOperator(self.ig, self.ag, device)
       else:
           assert isinstance(ProjectionOperator(self.ig, self.ag, device), object)

The parameters passed to the test are: The ``device`` (string), which is the device name passed to the ``ProjectionOperator``,
``raise_error`` (bool), which specifies if an error is expected during initialisation, and the expected ``err_type``.

In this example, the test instantiates a ``ProjectionOperator`` with a ``device`` name, checks if any errors should be raised, and ensures they are the expected type.
There are 3 sets of parameters:

- ``param('cpu', False, None, id="cpu_NoError")`` - Test using the device name 'cpu' (lowercase), and expects no error.
- ``param('CPU', False, None, id="CPU_NoError")`` - Test using the device name 'CPU' (uppercase), and expects no error.
- ``param('InvalidInput', True, ValueError, id="InvalidInput_ValueError")`` - Test using an invalid string, and expects the ``ValueError`` to be raised.

Each parameter set has a unique id which can also be customised for easier identification in test outputs (e.g., ``cpu_NoError``, ``InvalidInput_ValueError``)

When running the test, each parameterized case is shown as a distinct result:

.. code:: python
   test_ProjectionOperator_2Ddata[cpu_NoError] ... ok
   test_ProjectionOperator_2Ddata[CPU_NoError] ... ok
   test_ProjectionOperator_2Ddata[InvalidInput_ValueError] ... ok

   ----------------------------------------------------------------------
   Ran 3 tests in 0.001s

   OK

GitHub Actions CI
-----------------

If you open a pull request, continuous integration & deployment (CI/CD) via GitHub Actions (GHA) will run automatically. The CI will run the tests and build the documentation. For more information please see the `GHA README <https://github.com/TomographicImaging/CIL/blob/master/.github/workflows/README.md>`_.


Contributions guidelines
========================

Make sure that each contributed file contains the following text enclosed in the appropriate comment syntax for the file format. Please replace `[yyyy]` and `[name of copyright owner]` with your own identifying information. Optionally you may add author name and email.

::

  Copyright [yyyy] United Kingdom Research and Innovation
  Copyright [yyyy] The University of Manchester
  Copyright [yyyy] [name of copyright owner]
  Author(s): [Author name, Author email (optional)]
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
