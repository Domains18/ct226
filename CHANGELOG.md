# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive Linux installation support via `install.sh`
- Docker containerization with Dockerfile and docker-compose.yml
- Systemd service file for running as a Linux service
- Enhanced setup.py with proper packaging metadata
- GitHub Actions CI/CD workflows
- Detailed installation guide (INSTALL.md)
- Improvement recommendations document (IMPROVEMENTS.md)
- MANIFEST.in for proper package distribution
- LICENSE file (MIT)
- .env.example for environment variable configuration

### Changed
- Improved setup.py with better metadata and multiple entry points
- Enhanced package structure for better installability

### Fixed
- Entry point configuration for proper command-line access

## [1.0.0] - 2025-11-03

### Added
- Initial release
- Interactive CLI for contact management
- Telegram API integration via Telethon
- Phone number validation and formatting
- Bulk import from text files
- Progress tracking and statistics
- Session management
- Configuration via YAML
- Support for VCF, CSV, and JSON export formats

### Features
- Add contacts to Telegram in batches
- Skip existing contacts automatically
- Phone number validation using phonenumbers library
- Multi-format support for phone numbers
- Detailed logging and error handling
- Cross-platform support (Windows, Linux, macOS)

[Unreleased]: https://github.com/Domains18/ct226/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Domains18/ct226/releases/tag/v1.0.0
