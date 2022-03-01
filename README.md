# document-download-frontend

GOV.UK Notify frontend for downloading documents uploaded via [Document Download API](https://github.com/alphagov/document-download-api).

## Setting up

### Python version

Check the version in [runtime.txt](runtime.txt).

### NPM packages

```shell
brew install node
```

[NPM](npmjs.org) is Node's package management tool. `n` is a tool for managing different versions of Node.

The following installs `n` and installs the version of Node specified in `package.json` `engines` property. This will also install the NPM version packaged with that version of Node.

```shell
npm install -g n
n auto
```

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

### Updating the Node version for frontend builds

Edit the respective `node` version specified in the `engines` property in the `package.json` file.

Run `n auto` to install the new Node version.

The version specified in `engines` is also used to select the Node version used in CI builds:

 - Creating a PR with an updated version will build the PR using that version
 - Merging a version change will build and deploy the frontend assets using the new version

Ensure that an [LTS Node version](https://nodejs.org/en/about/releases/) is specified. This will also ensure the corresponding LTS NPM version is also installed.

## Further documentation

- [Updating dependencies](https://github.com/alphagov/notifications-manuals/wiki/Dependencies)
