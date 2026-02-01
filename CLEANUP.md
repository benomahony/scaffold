# Cleanup Checklist

## Critical Issues - Current Status

### ✅ Completed Today
- [x] **FIXED**: uv sync error - added `[tool.hatch.build.targets.wheel]` to pyproject.toml.j2
- [x] **FIXED**: zensical version too high - changed from >=0.1.0 to >=0.0.10
- [x] **FIXED**: MCP server type error - changed uri parameter to untyped with type ignore
- [x] **FIXED**: Migrated from pre-commit to prek
  - Updated pyproject.toml template (prek>=0.1.0)
  - Updated all core.py commands to use prek
  - Updated tests to use prek run -a
  - Updated skill documentation
  - Added --all-files flag to prek run commands

### ⚠️ Still Failing
- [ ] **Tests failing with exit status 1** - prek hooks finding unfixable issues
  - All 9 integration tests fail on second `prek run -a` (check=True)
  - First run (check=False) fixes formatting but issues remain
  - Need to investigate what prek hooks are failing and why
  - Likely type errors in generated templates (MCP server, etc.)

### 🔍 Next Steps
1. Manually create a test project and run `prek run -a` to see actual errors
2. Fix template issues causing hook failures
3. Re-run tests
4. Complete remaining cleanup items

## Files to Review

- [ ] Verify `src/scaffold/templates/base/pyproject.toml.j2` generates valid TOML
- [ ] Check if pytest-cov, bump-my-version, zensical are correctly in template
- [ ] Verify MCP optional dependency syntax is correct
- [ ] Test GitHub Actions workflow template renders correctly (fixed {% raw %} tags)

## Git Status

### Modified Files (need review/commit):
- [ ] `src/scaffold/cli.py` - Removed "uv sync" from Next steps
- [ ] `src/scaffold/core.py` - Added upgrade features, pre-commit install
- [ ] `src/scaffold/template_engine.py` - Added new template files
- [ ] `src/scaffold/templates/base/pyproject.toml.j2` - Added new dependencies
- [ ] `src/scaffold/templates/python/docs_index.md.j2` - Added AI Integration section
- [ ] `tests/test_integration.py` - Added AI integration test

### New Files (need review/commit):
- [ ] `.github/workflows/ci.yml` - GitHub Actions workflow
- [ ] `.pre-commit-config.yaml` - Pre-commit hooks config
- [ ] `.skills/scaffold/SKILL.md` - Agent Skill for scaffold
- [ ] `llms.txt` - LLM-friendly docs
- [ ] `zensical.toml` - Zensical config
- [ ] `src/scaffold/mcp_server.py` - MCP server for scaffold
- [ ] `src/scaffold/templates/base/.github_workflows_ci.yml.j2` - Workflow template
- [ ] `src/scaffold/templates/base/llms.txt.j2` - llms.txt template
- [ ] `src/scaffold/templates/base/zensical.toml.j2` - zensical config template
- [ ] `src/scaffold/templates/python/SKILL.md.j2` - Agent Skill template
- [ ] `src/scaffold/templates/python/mcp_server.py.j2` - MCP server template

## Testing

- [ ] Fix all integration tests
- [ ] Add test for MCP server import
- [ ] Add test for SKILL.md YAML parsing
- [ ] Add test for GitHub Actions workflow YAML validation
- [ ] Add test for zensical.toml TOML validation
- [ ] Run pre-commit hooks on all files
- [ ] Verify coverage is maintained

## Documentation

- [ ] Update README with new features (llms.txt, MCP, Skills, docs deployment)
- [ ] Document how to use MCP server
- [ ] Document how to install Agent Skill
- [ ] Update docs/index.md with comprehensive guide
- [ ] Add examples of generated projects

## Code Quality

- [ ] Run ruff format
- [ ] Run ruff check
- [ ] Run basedpyright
- [ ] Check for unused imports/code with vulture
- [ ] Run bandit security checks
- [ ] Run deptry dependency checks
- [ ] Verify all assertions follow NASA05 (2+ per function)

## Validation

- [ ] Test `sc init` creates working project
- [ ] Test `sc check` on scaffold itself
- [ ] Test `sc upgrade` on scaffold itself
- [ ] Test recursive operations
- [ ] Verify MCP server works: `claude mcp add scaffold ...`
- [ ] Verify Agent Skill works: `claude skill add .skills/scaffold`
- [ ] Test docs build: `uv run zensical build`
- [ ] Test GitHub Actions workflow (push to branch)

## Pre-commit to Prek Migration

Files updated:
- [x] `src/scaffold/templates/base/pyproject.toml.j2` - Changed pre-commit to prek
- [x] `src/scaffold/core.py` - Updated all pre-commit commands to prek
- [x] `tests/test_integration.py` - Updated test commands to prek
- [x] `.skills/scaffold/SKILL.md` - Updated documentation

Still investigating:
- [ ] Why `prek run` returns exit status 2
- [ ] Need to check if prek needs different command structure
- [ ] May need to run `prek install-hooks` before `prek run`

## Nice to Have

- [ ] Add version bumping to scaffold itself
- [ ] Consider adding changelog generation
- [ ] Add more project templates (library-only, FastAPI, etc.)
- [ ] Add `sc adopt` command for existing projects
- [ ] Add configuration for optional features (--no-github-actions, --with-docker, etc.)

## Next Actions

1. **PRIORITY**: Fix failing tests - investigate uv sync error
2. Run full test suite and verify all pass
3. Run pre-commit hooks
4. Review all git changes
5. Create atomic commits
6. Update documentation
7. Test end-to-end workflow
