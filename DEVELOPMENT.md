# Development guidelines

> [!IMPORTANT]  
> All paths are relative to the project's root directory, so make sure to `cd` after cloning the repository. If this is not done, some imports may fail.

## Running the project

```bash
python ./src/caioh_nvml_gpu_control/nvml_gpu_control.py help
```

## Local install

```bash
pip install .
```

## Running unit tests

```bash
python ./tests/test_nvml.py -b
```

## Versioning

Version number scheme: XX.YY.ZZ

* XX: represent breaking changes to the CLI interface. Since users rely on their scripts working correctly and this is the public interface, I will consider it the same as breaking API changes. 

* YY: represents new features that do not break existing ones (otherwise it would be XX).

* ZZ: representes changes that don't break anything. It could be a code refactor or new comments.

## Code style

* variable_name

* function_name

* ObjectOrClassName

## Rules for submitting code

When submmiting code to this project, pay attention to some rules:

* Other dependencies are DISALLOWED, I want to limit the dependencies as a security measure (just remember the xz incident). You are free to try to convince me, but your contribution will most likely be rejected

* Code should be testable, so please include unit tests to your code. If you think that certain parts are just too hard to make tests, include a justification