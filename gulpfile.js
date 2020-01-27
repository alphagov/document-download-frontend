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
    template: 'node_modules/govuk_template_jinja/',
    toolkit: 'node_modules/govuk_frontend_toolkit/'
};

// 3. TASKS
// - - - - - - - - - - - - - - -

// Move GOV.UK template resources

const copy = {
  govuk_template: {
    template: () => {
      return src(paths.template + 'views/layouts/govuk_template.html')
        .pipe(plugins.replace(/<script src="{{ asset_path }}javascripts\/govuk-template\.js\?\d+\.\d+\.\d+"><\/script>/, ''))
        .pipe(dest(paths.templates));
    },
    css: () => {
      return src(paths.template + 'assets/stylesheets/**/*.css')
        .pipe(plugins.sass({
          outputStyle: 'compressed'
        }))
        .on('error', plugins.sass.logError)
        .pipe(plugins.cssUrlAdjuster({
          prependRelative: '/static/',
        }))
        .pipe(dest(paths.dist + 'stylesheets/'));
    },
    images: () => {
      return src(paths.template + 'assets/stylesheets/images/**/*')
        .pipe(dest(paths.dist + 'images/'));
    },
    fonts: () => {
      return src(paths.template + 'assets/stylesheets/fonts/**/*')
        .pipe(dest(paths.dist + 'fonts/'));
    },
    error_page: () => {
      return src(paths.src + 'error_pages/**/*')
        .pipe(dest(paths.dist + 'error_pages/'))
    }
  }
};

const sass = () => {
  return src(paths.src + '/stylesheets/main*.scss')
    .pipe(plugins.prettyerror())
    .pipe(plugins.sass({
      outputStyle: 'compressed',
      includePaths: [
        paths.npm + 'govuk-elements-sass/public/sass/',
        paths.toolkit + 'stylesheets/'
      ]
    }))
    .pipe(plugins.base64('../..'))
    .pipe(dest(paths.dist + 'stylesheets/'))
};

// Copy images

const images = () => {
  return src([
      paths.src + 'images/**/*',
      paths.toolkit + 'images/**/*',
      paths.template + 'assets/images/**/*'
    ])
    .pipe(dest(paths.dist + 'images/'))
};

// Watch for changes and re-run tasks
const watchForChanges = () => {
  return watch(paths.src + 'stylesheets/**/*', ['sass'])
    .watch(paths.src + 'images/**/*', ['images']);
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
const defaultTask = parallel(
  series(
    copy.govuk_template.template,
    copy.govuk_template.images,
    copy.govuk_template.fonts,
    copy.govuk_template.css,
    copy.govuk_template.js,
    images
  ),
  series(
    copy.govuk_template.error_page,
    sass
  )
);

exports.default = defaultTask;

exports.lint = series(lint.sass, lint.js);

// Optional: recompile on changes
exports.watch = series(defaultTask, watchForChanges);
