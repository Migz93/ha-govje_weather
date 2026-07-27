# ChatGPT Codex Instructions

ChatGPT Codex reads project instructions from [`AGENTS.md`](AGENTS.md). Read that file completely before starting any work.

`AGENTS.md` contains the shared guidance for this integration, including architecture, development workflows, validation commands, Home Assistant patterns, and breaking-change policy.

## Quick Reference

- **Domain:** `govje_weather`
- **Title:** GOVJE Weather
- **Class prefix:** `GOVJEWeather`
- **Main code:** `custom_components/govje_weather/`
- **Validate:** `script/check` (type-check + lint + spell)
- **Test:** `script/test`
- **Run HA:** `./script/develop`

## Path-Specific Instructions

Additional domain-specific guidance is available in `.github/instructions/*.instructions.md`. Review the instruction file whose `applyTo` pattern matches each file you modify.
