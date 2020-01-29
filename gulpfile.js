// GULPFILE
// - - - - - - - - - - - - - - -
// This file processes all of the assets in the "src" folder
// and outputs the finished files in the "dist" folder.

// 1. LIBRARIES
// - - - - - - - - - - - - - - -
const { src, pipe, dest, series, parallel } = require('gulp');
const stylish = require('jshint-stylish');

const plugins = {};
plugins.base64 = require('gulp-base64-inline');
plugins.cssUrlAdjuster = require('gulp-css-url-adjuster');
plugins.prettyerror = require('gulp-prettyerror');
plugins.replace = require('gulp-replace');
plugins.sass = require('gulp-sass');
plugins.sassLint = require('gulp-sass-lint');


// 2. CONFIGURATION
// - - - - - - - - - - - - - - -
const paths = {
    src: 'app/assets/',
    dist: 'app/static/',
    templates: 'app/templates/',
    npm: 'node_modules/',
    govuk_frontend: 'node_modules/govuk-frontend/govuk/'
};

// 3. TASKS
// - - - - - - - - - - - - - - -

// Move GOV.UK Frontend resources

const copy = {
  govuk_frontend: {
    fonts: () => {
      return src(paths.govuk_frontend + 'assets/fonts/**/*')
        .pipe(dest(paths.dist + 'fonts/'));
    },
    templates: (cb) => {
      src(paths.govuk_frontend + '**/*.njk')
      .pipe(
        dest(paths.templates + 'vendor/govuk_frontend')
        .on('end', () => cb())
      )
    }
  }
};

const sass = () => {
  return src(paths.src + '/stylesheets/main*.scss')
    .pipe(plugins.prettyerror())
    .pipe(plugins.sass({
      outputStyle: 'compressed',
      includePaths: [
        paths.govuk_frontend
      ]
    }))
    .pipe(plugins.base64('../..'))
    .pipe(dest(paths.dist + 'stylesheets/'))
};

// Copy images

const images = () => {
  return src([
      paths.src + 'images/**/*',
      paths.govuk_frontend + 'assets/images/**/*'
    ])
    .pipe(dest(paths.dist + 'images/'))
};

// Watch for changes and re-run tasks
const watchForChanges = () => {
  return watch(paths.src + 'stylesheets/**/*', ['sass'])
};

const lint = {
  'sass': () => {
    return src([
        paths.src + 'stylesheets/*.scss',
        paths.src + 'stylesheets/components/*.scss',
        paths.src + 'stylesheets/views/*.scss',
      ])
      .pipe(plugins.sassLint())
      .pipe(plugins.sassLint({
        'options': { 'formatter': stylish }
      }))
      .pipe(plugins.sassLint.failOnError());
  }
};

// Default: compile everything
const defaultTask = series(
  copy.govuk_frontend.templates,
  copy.govuk_frontend.fonts,
  images,
  sass
);

exports.default = defaultTask;

exports.lint = series(lint.sass);

// Optional: recompile on changes
exports.watch = series(defaultTask, watchForChanges);
