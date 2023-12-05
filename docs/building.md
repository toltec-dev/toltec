## Building the Repository from Source

The Toltec repository is automatically built for each commit on the `stable` and `testing` branches.
You may want to build the repository locally when working with a new package recipe or to make sure that nobody tampered with the automated build system. [Toltecmk](https://github.com/toltec-dev/build) could also be used instead, if you just need to compile a single standalone package.

To proceed, create a local clone of the Git repository.

```sh
git clone https://github.com/toltec-dev/toltec
```

You’ll be on the `stable` branch by default.
If you want to build the `testing` branch, switch to it manually.

### Running a Build

Before running the build, make sure you have all the required dependencies:

* Docker
* bsdtar
* Python 3.10

You’ll also need all the Python modules listed in [requirements.txt](../requirements.txt) (install them by running `pip install --user -r requirements.txt` or using a [virtual environment](https://docs.python.org/3/tutorial/venv.html)).

To start the build, run `make repo-local`.
This will be a long process, so you may want to grab a cup of coffee.
The build will involve downloading Toltec’s Docker images, which are around 1 GB each.
Once the build completes, the artifacts are available under `build/repo`.

### Running Checks

Automated code checks help identify parts of the code that do not comply with the style guide or contain potential errors.
To run them, you’ll need to install the following dependencies:

* shfmt
* Shellcheck

To check for common errors, run `make lint`.
To check for style guide errors, run `make format`.
You can also use `make format-fix` to automatically fix style guide issues (this will change the source files in your local copy!).
