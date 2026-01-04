Release checklist

- [ ] Ensure all CI jobs pass (Ubuntu + Windows)
- [ ] Run full test suite locally on supported platforms
- [ ] Bump version in `pyproject.toml`
- [ ] Update `CHANGES.md` with release notes
- [ ] Tag the release: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push tags and open GitHub Release
- [ ] Verify uploaded artifacts (Unreal plugin archived; no plugin artifact will be published)
- [ ] Announce release and update documentation
