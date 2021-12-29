# document-download-frontend

GOV.UK Notify frontend for downloading documents uploaded via [Document Download API](https://github.com/alphagov/document-download-api).

## Setting up

### Python version

Check the version in [runtime.txt](runtime.txt).

### NPM packages

```shell
brew install node
```

[NPM](npmjs.org) is Node's package management tool. `n` is a tool for managing different versions of Node. The following installs `n` and uses the long term support (LTS) version of Node.

```shell
npm install -g n
n lts
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

## Further documentation

- [Updating dependencies](https://github.com/alphagov/notifications-manuals/wiki/Dependencies)
