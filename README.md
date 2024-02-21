# document-download-frontend

GOV.UK Notify frontend for downloading documents uploaded via [Document Download API](https://github.com/alphagov/document-download-api).

## Setting up

### Python version

Check the version in [runtime.txt](runtime.txt).

### NodeJS version

If you don't have NodeJS on your system, install it with homebrew.

```shell
brew install node
```

`nvm` is a tool for managing different versions of NodeJS. Follow [the guidance on nvm's github repository](https://github.com/nvm-sh/nvm#installing-and-updating) to install it.

Once installed, run the following to switch to the version of NodeJS for this project. If you don't
have that version, it should tell you how to install it.

```shell
nvm use
```

### Pre-commit

We use [pre-commit](https://pre-commit.com/) to ensure that committed code meets basic standards for formatting, and will make basic fixes for you to save time and aggravation.

Install pre-commit system-wide with, eg `brew install pre-commit`. Then, install the hooks in this repository with `pre-commit install --install-hooks`.

## To run the application

```shell
# install dependencies, etc.
make bootstrap

make run-flask
```

## To test the application

```shell
# install dependencies, etc.
make bootstrap

make test
```

## Common tasks

### Automatically rebuilding the frontend assets

If you want the front end assets to re-compile on changes, leave this running
in a separate terminal from the app

```shell
npm run watch
```

You will need to restart the app after any changes to front end assets, so that they are served with
the correct `Content-Length` header for their contents. If you are using
[notifications-local](https://github.com/alphagov/notifications-local), you will need to run:

```bash
docker compose restart document-download-frontend
```

### Updating the Node version for frontend builds

Edit the respective `node` version specified in the `.nvmrc` file.

Run `nvm install` to install the new Node version.

The version specified in the `.nvmrc` file is also used to select the Node version used in CI builds:

 - Creating a PR with an updated version will build the PR using that version
 - Merging a version change will build and deploy the frontend assets using the new version

Ensure that an [LTS Node version](https://nodejs.org/en/about/releases/) is specified. This will also ensure the corresponding LTS NPM version is also installed.

### Updating GOV.UK Frontend

#### Keeping GOV.UK Frontend versions in sync

We have GOV.UK Frontend as a dependency in two places:

* In Python, our requirements.in specifies a version of [govuk-frontend-jinja](https://github.com/LandRegistry/govuk-frontend-jinja) for our jinja templates
* In Node, our package.json specifies a version of [govuk-frontend](https://github.com/alphagov/govuk-frontend) for our fonts, images and sass files

We need to ensure that the version of govuk-frontend that the Python library relies on always
matches the version of govuk-frontend in our package.json exactly.

If you're bumping either library, make sure the version of the Python library supports the same version
of govuk-frontend defined in our package.json, as referred to in the
[govuk-frontend-jinja compatibility table](https://github.com/LandRegistry/govuk-frontend-jinja#compatibility).

#### Keeping the HTML footer up to date

We override the [govuk-frontend footer](./app/templates/components/footer/macro.html).
If you bump the version of govuk-frontend-jinja, you should ensure that the footer HTML stays up to date with the
version of govuk-frontend-jinja. See the comment in that file for more details.

## Further documentation

- [Updating dependencies](https://github.com/alphagov/notifications-manuals/wiki/Dependencies)
