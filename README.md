# IBEX Tools

This repo contains tools for manipulating IBEX data.   In general, these tools were developed to explore the representation of unreliability in the data using a 2D colormap.  These tools are based on a Python class IBEX.   Ancillary tools are contained in the colortools.py file.

## IBEX Class

The IBEX class represents an IBEX dataset.  This includes a set of *timesteps*.  Each timestep contains a set of *dependent variables*, defined as a 2D grid of scalar, floating point values, with one column for each unique longitude of the data and one row for each unique latitude.  If a particular location is not found in the original data a value of 0 will be used.

### IBEX Class Variables

- **names** a list of the timestep names.   From the names of the original CSV files.
- **varnames** a list of the variables in the data.   Each timestep must have the same set of variables
- **vardata** a list of numpy arrays containing the variable data ordered the same as **varnames**
- **resolution** the resolution of data.  All timesteps must be of the same resolution.

### IBEX Class Methods

- **Count()** Returns the number of timesteps
- **Add(name, varnames, vardata)** Add an additional timestep
- **AddFromSCSV(csv)**  Add an additional timestep read from a CSV file
- **Read(filename)** Read an instance stored in an *.ibx* file
- **Write(filename)** Save this instance to an .ibx* file
- **GetByIndex(indx)** Get [name, varnames, vardata] for the indexed timestep.   The varnames are a list of names; the vardata are a list of numpy arrays containing variable data.
- **GetByName(name)** Get [name, varnames, vardata] for the named timestep.   The varnames are a list of names; the vardata are a list of numpy arrays containing variable data.
- **Ranges()** Returns the min and max of each variable *over all timesteps*.
- **Resize(factor)**  Resize the data by *factor*.
- **Variable(name)**  Return the 3D data associated by with the variable name.   The first dimension ranges over the timesteps, the ramaining two correspond to [lat, lon].
- **Calculate(name, function)** Create a derived variable by applying  a function to the variables in the instance>
- **Sort()** Sort the timesteps lexicographically by the name.  One hopes original csv files have sensible names
- **Normalize()** Normalize the variables of the instance.  Each variable is normalized across the set of timesteps
- **Info()**  Print first a list of timestep names, then a list of variable names with the min and max of the corresponding variable

## Maps

Core to this work is the application of color maps to the data contained in the IBEX data.   Three maps are relevant: *1D colormaps* that map individual variable values to colors; *2D colormaps* which map two variables (think *signal* in the Y axis and *unreliability* in the X axis) giving color, and *opacity maps*, mapping a range of normalized values to opacities.  Tools for handling these maps (as well as other random tools) are in the colortools.py file.

### 1D Colormaps

Internally, these are [256,3] numpy arrays containing normalized RGB for each of 256 levels.  Externally, these are represented simple csv files containing normalized RGB triples for each of 256 rows, and as Paraview .xml or .json format.   See Paraview for details.  Paraview-format data may be specified sparsely in arbitrary ranges; these are re-ranged and regularized upon input.

- **load_colormap(filename)** loads a colormap from the given file, normalizes it as necessary and returns it.
- **SaveColormap(cmap, name)** Save a colormap as a Paraview json-format file.
- **SaveColormapXML(cmap, name)** Save a colormap as a Paraview xml-format file.
- **ApplyColormap1D(value_array, colormap)**  Apply the given 1D colormap to an array of values.  Dimensionality increases by 1, with the fastest index representing [r, g, b].

###  1D Opacitymaps

Internally, these are [256] numpy arrays containing normalized opacities for each of 256 levels.  Externally, these are represented simple csv files containing normalized RGB triples for each of 256 rows, and as Paraview .xml or .json format.   See Paraview for details.  Paraview-format data may be specified sparsely in arbitrary ranges; these are re-ranged and regularized upon input.

- **load_opacitymap(filename)** loads an opacitymap from the given file, normalizes it as necessary and returns it.

### 2D Colormaps

Internally, these are [1024,1024,3] arrays that map a signal (the Y axis) and associated unreliability (the X axis) to a color.  Externally, they are represented as binary data assumed to contained 1024*1024*3 float32 arrays.

- **ReadColormap2D(filename)** Read a 2D colormap from a file
- **WriteColormap2D(filename)** Write a 2D colormap to a file
- **ApplyColormap(signal, unreliability, cmap)** Apply the 2D colormap to equal-sized arrays containing normalized signal and unreliability values.

## Command-line Tools

- **Csv2Ibx csv [csv...] ibx** read a set of csv files in original format into an IBEX instance and save it as an ibx file
- **ApplyCmap2D ibx cmap sigvar relvar directory** Apply the given 2D colormap to the specified variables in the input data file, produucing one image file for each timestep
- **Ibex2Gscale ibx varname** render a grey-scale image of the named variable of each timestep of the data.
- **VarNames ibx** List the variable names contained in the ibx file
- **DatasetNames ibx** List the timestep names contained in the ibx file
- **ToCMoves ibx [-l level] [-s scale]** produce a set of data files for input to ColorMoves.  The -l parameter allows you to specify an ESA level (defaulting to all of them); the -s scale allows you to scale the output images by a factor.  ***Note - this may be out of date***

### Cacluate-based tools

Several tools are included to create derived variables using the IBEX class' Calculate method.

- **BracketExposure in.ibx low high max_unreliability out.ibx**  Creates a derived unreliability variable from the *exposure time* variable.  Values less than *low* are considered fully unreliable, and receive the maximum unreliability value.   Values greater than *high* are considered fully reliable, and receive a value of 0.  Intervening values are interpolated linearly.
- **HistoEq in.ibx varname out.ibx** applies a histogram equalization algorithm to the named variable, producing a derived variable named ***varname_he**.
- **RelativeError in.ibx signame abserrname out.ibx** Divides the absolute error variable named by *abserrname* by the signal variable named *signame*  producing a relative error variable named *sigvar_re*.
- **Normalize in.ibx varname out.ibx** Normalize the named variable *across all timesteps*, producing a derived varaiable named *varname_n*.



