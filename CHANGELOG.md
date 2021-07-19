# CHANGELOG

### 0.2.1 - 15/06/2021

* New: Import metadata from [datapackage.json](https://github.com/cividi/spatial-data-package) file (w/o data layers)
* New: Interface for editing [data package contributors](https://specs.frictionlessdata.io/data-package/#contributors)
* Fixed: UTF-8 issues when exporting/importing layers
* Future: Prepared plugin for full data package import including data layers

### 0.2.0 - 09/12/2020

* Now left experimental stage
* Added code coverage report on GitHub project
* Fixed: export bugs (title, description, single symbol layer names)
* New: Added a plugin setting for data package layers to be discarded, kept as memory layers ot written as GeoJSON
* New: Shapes of legend entries can be manually changed before exporting
* New: Option to not crop exported layers to bounds
* New: Store and load data package settings to the project
* New: Added Keywords UI to set data package keywords
* New: Layer keywords and licenses are exported to Data Package
* New: Add template file paths to settings dialog
* New: Use author of the QGIS project in contributor

### 0.1.0 - 14/10/2020

* Project renamed to Spatial Data Package Export
* Project moved to github.com/cividi/spatial-data-package-export
* Add logo

### 0.0.3 - 25/09/2020

* Add support for Leaflet Styles
* Improve tests
* Use symbol opacity and store widths as float
* Fixed bug with bounding box chooser coordinate reference system

### 0.0.2 - 16/09/2020

* Remove dataclass in order to support Python 3.6

### 0.0.1 - 15/09/2020

* Processing algorithm for Styles to Attributes
* Initial DockWidget with some of the fields required for data package
* Initial support for file exports of data package snapshots
* Initial tests

###
