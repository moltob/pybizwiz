# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project 
adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 4.4.6

- Interpreter update to Python 3.7.
- Update of all used packages.

## 4.4.5
### Fixed

- Salutation now showing customer name's title (Dr., ...).

## 4.4.4
### Added

- Python package updates, including to Django 2.0.3.

## 4.4.3
### Added

- Python package updates, including to Django 2.0.1.

## 4.4.2
### Added

- Display of customer notes during invoice creation and editing.

## 4.4.1
### Added

- Migration to [django-money](https://github.com/django-money/django-money), currency-aware
  representation of money values.
- Added currency to all forms and views.
- Switched default print template to match paper with full letterhead.

## 4.4.0
### Added

- Internal package updates, in particluar updated to Django 2.0.
- Another PDF template for export to paper with full letterhead preprinted.

## 4.3.1
### Added

- Display of changelog.

### Fixed

- Annual income now exact sum of all invoices.
- Drilldown to articles sold in given year now shows article names from invoice, not the originally 
  selected article (from master data).

## 4.3.0
### Added

- Excel export of invoice lists.
- Annual sales report.
- Article tops and flops.

### Changed

- Updated to Python 3.6.2.
- Updated package dependencies.

## 4.2.3
### Changed

- Icons.
- Welcome screen.

## 4.2.1
### Added

- Version information created during release automatically.

### Changed

- Python package updates.
- _Latest_ tag for docker container.

## 4.2.0
### Added

- Rebate rule system
