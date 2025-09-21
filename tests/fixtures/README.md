# Test Fixtures

This directory contains test fixtures for integration testing.

## GitHub.iatemplate

This is a copy of the official GitHub template from the iA Writer Templates repository:
https://github.com/iainc/iA-Writer-Templates

The template is used as a reference to verify that our build system produces
an exact copy of the original template.

### Updating the fixture

If you need to update the fixture with the latest version from GitHub:

```bash
# Remove the old fixture
rm -rf tests/fixtures/GitHub.iatemplate

# Clone the repository
git clone --depth 1 https://github.com/iainc/iA-Writer-Templates.git temp_clone

# Copy the GitHub template
cp -r temp_clone/GitHub.iatemplate tests/fixtures/

# Clean up
rm -rf temp_clone
```

### Automatic download

If the fixture is missing, the tests will automatically download it from GitHub
the first time they run.