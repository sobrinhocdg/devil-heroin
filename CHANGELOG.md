# Changelog

All notable changes to AfterRelease33 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v33] - 2026-04-26

### Added
- Initial release of AfterRelease33 - Dungeon Synth MIDI Generator
- Web interface for easy MIDI generation and download
- Support for up to 12 tracks with varied patterns
- Multiple musical modes: aeolian, dorian, phrygian, harmonic_minor, locrian, lydian, mixolydian, pentatonic_minor, blues
- Expanded instrument library with 40+ dark synth instruments
- Varied chord progressions and rhythmic patterns
- Windows installer batch file (RELEASE_v33.bat)
- FL Studio presets recommendations
- ZIP package for easy distribution

### Features
- Generates MIDI files focused on dungeon synth aesthetics
- Random seed for reproducible or varied results
- Web server for browser-based generation
- Command-line interface for advanced users
- Automatic dependency installation
- Cross-platform compatibility (Windows, Linux, macOS)

### Technical
- Built with Python 3, Flask, and Mido library
- MIDI files compatible with FL Studio and other DAWs
- Tempo range: 40-90 BPM
- Bars: 8-128
- Tracks: 1-12

---

## Development Notes
- Project started as a tool for generating atmospheric MIDI bases for dungeon synth music
- Focus on dark, ambient, and medieval-inspired soundscapes
- Designed for ease of use by non-technical music producers