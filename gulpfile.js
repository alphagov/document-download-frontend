// GULPFILE
// - - - - - - - - - - - - - - -
// This file processes all of the assets in the "src" folder
// and outputs the finished files in the "dist" folder.

// 1. LIBRARIES
// - - - - - - - - - - - - - - -
const { src, pipe, dest, series, parallel } = require('gulp');
const oldie = require('oldie');
const postcss = require('gulp-postcss');
const rollupPluginCommonjs = require('@rollup/plugin-commonjs');
const rollupPluginNodeResolve = require('@rollup/plugin-node-resolve');
const stylish = require('jshint-stylish');

const plugins = {};
plugins.addSrc = require('gulp-add-src');
plugins.concat = require('gulp-concat');
plugins.cssUrlAdjuster = require('gulp-css-url-adjuster');
plugins.jshint = require('gulp-jshint');
plugins.prettyerror = require('gulp-prettyerror');
plugins.replace = require('gulp-replace');
plugins.rollup = require('gulp-better-rollup');
plugins.sass = require('gulp-sass')(require('sass'));
plugins.sassLint = require('gulp-sass-lint');
plugins.uglify = require('gulp-uglify');


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
  },
  js: () => {
    return src(paths.src + 'javascripts/html5shiv.min.js')
      .pipe(dest(paths.dist + 'javascripts/'));
  }
};


const javascripts = () => {
  // JS from third-party sources
  // We assume none of it will need to pass through Babel
  return src(paths.src + 'javascripts/main.mjs')
    // Use Rollup to combine all JS in JS module format into a Immediately Invoked Function
    // Expression (IIFE) to:
    // - deliver it in one bundle
    // - allow it to run in browsers without support for JS Modules
    .pipe(plugins.rollup(
      {
        plugins: [
          // determine module entry points from either 'module' or 'main' fields in package.json
          rollupPluginNodeResolve({
            mainFields: ['module', 'main']
          }),
          // gulp rollup runs on nodeJS so reads modules in commonJS format
          // this adds node_modules to the require path so it can find the GOVUK Frontend modules
          rollupPluginCommonjs({
            include: 'node_modules/**'
          })
        ]
      },
      {
        file: 'main.js',
        format: 'iife',
        name: 'GOVUK'
      }
    ))
    .pipe(plugins.uglify())
    .pipe(dest(paths.dist + 'javascripts/'))
};


const sass = () => {
  return src(paths.src + '/stylesheets/main.scss')
    .pipe(plugins.prettyerror())
    .pipe(plugins.sass.sync({
      outputStyle: 'compressed',
      includePaths: [
        paths.govuk_frontend
      ]
    }))
    .pipe(dest(paths.dist + 'stylesheets/'))
};


const ieSass = () => {
  return src(paths.src + '/stylesheets/main-ie*.scss')
    .pipe(plugins.prettyerror())
    .pipe(plugins.sass({
      outputStyle: 'compressed',
      includePaths: [
        paths.govuk_frontend
      ]
    }))
    .pipe(postcss(oldie))
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
  },
  'js': (cb) => {
    return src([
        paths.src + 'javascripts/**/*.js',
        '!' + paths.src + 'javascripts/**/html5shiv.min.js'
      ])
      .pipe(plugins.jshint())
      .pipe(plugins.jshint.reporter(stylish))
      .pipe(plugins.jshint.reporter('fail'))
  } 
};

// Default: compile everything
const defaultTask = parallel(
  series(
    parallel(
      copy.govuk_frontend.templates,
      copy.govuk_frontend.fonts,
      copy.js,
      images
    ),
    parallel(
      sass,
      ieSass
    )
  ),
  javascripts
);

exports.default = defaultTask;

exports.lint = series(lint.sass, lint.js);

// Optional: recompile on changes
exports.watch = series(defaultTask, watchForChanges);
