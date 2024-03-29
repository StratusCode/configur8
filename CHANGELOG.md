# Changelog

## [Unreleased]

## [2.0.1] - 2023-03-08

### Changed
 - `configur8.cfg` String based type annotations are not currently supported.
 - `configur8.cfg` `typing.NewType` is now supported.

## [2.0] - 2023-02-09

`configur8.cfg` completely rewritten to use annotated Python classes instead
  of programmatically building via `YamlConfig`.

### Added
- `configur8.cfg.into` constructs and validates a configuration object from
  supplied annotated class and value object.
- `configur8.cfg.parse` parses a configuration object from supplied annotated
  class and raw data stream.
- `configur8.cfg.load` loads a configuration object from supplied annotated
  class and file path.

### Removed
- `configur8.cfg.YamlConfig`
