// GULPFILE
// - - - - - - - - - - - - - - -
// This file processes all of the assets in the "src" folder
// and outputs the finished files in the "dist" folder.

// 1. LIBRARIES
// - - - - - - - - - - - - - - -
import gulp from 'gulp';
import loadPlugins from 'gulp-load-plugins';
import stylish from 'jshint-stylish';

const plugins = loadPlugins(),

// 2. CONFIGURATION
// - - - - - - - - - - - - - - -
    paths = {
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

gulp.task('copy:govuk_template:template', () => gulp.src(paths.template + 'views/layouts/govuk_template.html')
  .pipe(plugins.replace(/<script src="{{ asset_path }}javascripts\/govuk-template\.js\?\d+\.\d+\.\d+"><\/script>/, ''))
  .pipe(gulp.dest(paths.templates))
);

gulp.task('copy:govuk_template:css', () => gulp.src(paths.template + 'assets/stylesheets/**/*.css')
  .pipe(plugins.sass({
    outputStyle: 'compressed'
  }))
  .on('error', plugins.sass.logError)
  .pipe(plugins.cssUrlAdjuster({
    prependRelative: '/static/',
  }))
  .pipe(gulp.dest(paths.dist + 'stylesheets/'))
);

gulp.task('copy:govuk_template:images', () => gulp.src(paths.template + 'assets/stylesheets/images/**/*')
  .pipe(gulp.dest(paths.dist + 'images/'))
);

gulp.task('copy:govuk_template:fonts', () => gulp.src(paths.template + 'assets/stylesheets/fonts/**/*')
  .pipe(gulp.dest(paths.dist + 'fonts/'))
);

gulp.task('sass', () => gulp
  .src(paths.src + '/stylesheets/main*.scss')
  .pipe(plugins.prettyerror())
  .pipe(plugins.sass({
    outputStyle: 'compressed',
    includePaths: [
      paths.npm + 'govuk-elements-sass/public/sass/',
      paths.toolkit + 'stylesheets/'
    ]
  }))
  .pipe(plugins.base64({baseDir: 'app'}))
  .pipe(gulp.dest(paths.dist + 'stylesheets/'))
);


// Copy images

gulp.task('images', () => gulp
  .src([
    paths.src + 'images/**/*',
    paths.toolkit + 'images/**/*',
    paths.template + 'assets/images/**/*'
  ])
  .pipe(gulp.dest(paths.dist + 'images/'))
);

gulp.task('copy:govuk_template:error_page', () => gulp.src(paths.src + 'error_pages/**/*')
  .pipe(gulp.dest(paths.dist + 'error_pages/'))
);


// Watch for changes and re-run tasks
gulp.task('watchForChanges', function() {
  gulp.watch(paths.src + 'stylesheets/**/*', ['sass']);
  gulp.watch(paths.src + 'images/**/*', ['images']);
  gulp.watch('gulpfile.babel.js', ['default']);
});

gulp.task('lint:sass', () => gulp
  .src([
    paths.src + 'stylesheets/*.scss',
    paths.src + 'stylesheets/components/*.scss',
    paths.src + 'stylesheets/views/*.scss',
  ])
    .pipe(plugins.sassLint())
    .pipe(plugins.sassLint.format(stylish))
    .pipe(plugins.sassLint.failOnError())
);

gulp.task('lint',
  ['lint:sass']
);

// Default: compile everything
gulp.task('default',
  [
    'copy:govuk_template:template',
    'copy:govuk_template:images',
    'copy:govuk_template:fonts',
    'copy:govuk_template:css',
    'copy:govuk_template:error_page',
    'sass',
    'images'
  ]
);

// Optional: recompile on changes
gulp.task('watch',
    ['default', 'watchForChanges']
);
