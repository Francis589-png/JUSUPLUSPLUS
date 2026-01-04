Release checklist

- [ ] Ensure all CI jobs pass (Ubuntu + Windows)
- [ ] Run full test suite locally on supported platforms
- [ ] Bump version in `pyproject.toml`
- [ ] Update `CHANGES.md` with release notes
- [ ] Tag the release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push tags and open GitHub Release (the `release` workflow will upload plugin artifact)
- [ ] Verify uploaded artifacts and smoke test the packaged plugin
- [ ] Announce release and update documentation
