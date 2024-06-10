////////////////////////////////
// Setup
////////////////////////////////

// Gulp and package
const { src, dest, parallel, series, watch } = require('gulp');
const pjson = require('./package.json');

// Plugins
const autoprefixer = require('autoprefixer');
const browserSync = require('browser-sync').create();
const concat = require('gulp-concat');
const tildeImporter = require('node-sass-tilde-importer');
const cssnano = require('cssnano');
const imagemin = require('gulp-imagemin');
const pixrem = require('pixrem');
const plumber = require('gulp-plumber');
const postcss = require('gulp-postcss');
const reload = browserSync.reload;
const rename = require('gulp-rename');
const sass = require('gulp-sass')(require('sass'));
const spawn = require('child_process').spawn;
const uglify = require('gulp-uglify-es').default;
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var rollup = require('@rollup/stream');
var babel = require('@rollup/plugin-babel');
var commonjs = require('@rollup/plugin-commonjs');
var nodeResolve = require('@rollup/plugin-node-resolve');
var cache;


// Relative paths function
function pathsConfig(appName) {
  this.app = `./${pjson.name}`;
  const vendorsRoot = 'node_modules';

  return {
    vendorsJs: [
      `${vendorsRoot}/file-saver/dist/FileSaver.js`,
      `${vendorsRoot}/jszip/dist/jszip.js`,
      `${vendorsRoot}/cropperjs/dist/cropper.js`,
    ],
    app: this.app,
    templates: `${this.app}/templates`,
    css: `./static/css`,
    sass: `./static/sass`,
    fonts: `./static/fonts`,
    images: `./static/images`,
    js: `./static/js`,
  };
}

const paths = pathsConfig();

////////////////////////////////
// Tasks
////////////////////////////////

// Styles autoprefixing and minification
function styles() {
  const processCss = [
    autoprefixer(), // adds vendor prefixes
    pixrem(), // add fallbacks for rem units
  ];

  const minifyCss = [
    cssnano({ preset: 'default' }), // minify result
  ];

  return src(`${paths.sass}/submit.scss`)
    .pipe(
      sass({
        importer: tildeImporter,
        includePaths: [paths.sass],
      }).on('error', sass.logError),
    )
    .pipe(plumber()) // Checks for errors
    .pipe(postcss(processCss))
    .pipe(dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(postcss(minifyCss)) // Minifies the result
    .pipe(dest(paths.css));
}

function adminStyles() {
  const processCss = [
    autoprefixer(), // adds vendor prefixes
    pixrem(), // add fallbacks for rem units
  ];

  const minifyCss = [
    cssnano({ preset: 'default' }), // minify result
  ];

  return src(`${paths.sass}/admin.scss`)
    .pipe(
      sass({
        importer: tildeImporter,
        includePaths: [paths.sass],
      }).on('error', sass.logError),
    )
    .pipe(plumber()) // Checks for errors
    .pipe(postcss(processCss))
    .pipe(dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(postcss(minifyCss)) // Minifies the result
    .pipe(dest(paths.css));
}

// Javascript minification

// Submit JS
function submitJS() {
  return rollup({
    input: "./static/js/submit/index.js",
    plugins: [babel({ babelHelpers: 'bundled' }), commonjs(), nodeResolve()],
    cache: cache,
    output: {
      format: "iife",
      sourcemap: true,
      name: "submit",
    }
  })
  .on("bundle", function (bundle) {cache = bundle})
  .pipe(source('submit.min.js'))
  .pipe(buffer())
  .pipe(dest('./static/js/'));
}

// Admin JS

function adminJs() {
  return rollup({
    input: "./static/js/admin/index.js",
    plugins: [babel({ babelHelpers: 'bundled' }), commonjs(), nodeResolve()],
    cache: cache,
    output: {
      format: "iife",
      sourcemap: true,
      name: "admin",
    }
  })
  .on("bundle", function (bundle) {cache = bundle})
  .pipe(source('admin.min.js'))
  .pipe(buffer())
  .pipe(dest('./static/js/'));
}

// Vendor Javascript minification
function vendorScripts() {
  return src(paths.vendorsJs, { sourcemaps: true })
    .pipe(concat('vendors.js'))
    .pipe(dest(paths.js))
    .pipe(plumber()) // Checks for errors
    .pipe(uglify()) // Minifies the js
    .pipe(rename({ suffix: '.min' }))
    .pipe(dest(paths.js, { sourcemaps: '.' }));
}

// Image compression
function imgCompression() {
  return src(`${paths.images}/*`)
    .pipe(imagemin()) // Compresses PNG, JPEG, GIF and SVG images
    .pipe(dest(paths.images));
}
// Run django server
function runServer(cb) {
  const cmd = spawn('python', ['manage.py', 'runserver'], { stdio: 'inherit' });
  cmd.on('close', function (code) {
    console.log('runServer exited with code ' + code);
    cb(code);
  });
}

// Browser sync server for live reload
function initBrowserSync() {
  browserSync.init(
    [`${paths.css}/*.css`, `${paths.js}/*.js`, `${paths.templates}/*.html`],
    {
      // https://www.browsersync.io/docs/options/#option-open
      // Disable as it doesn't work from inside a container
      open: false,
      // https://www.browsersync.io/docs/options/#option-proxy
      proxy: {
        target: 'django:8000',
        proxyReq: [
          function (proxyReq, req) {
            // Assign proxy 'host' header same as current request at Browsersync server
            proxyReq.setHeader('Host', req.headers.host);
          },
        ],
      },
    },
  );
}

// Watch
function watchPaths() {
  watch(`${paths.sass}/*.scss`, styles);
  watch(`${paths.templates}/**/*.html`).on('change', reload);
  watch([`${paths.js}/*.js`, `!${paths.js}/*.min.js`], scripts).on(
    'change',
    reload,
  );
}

// Generate all assets
const generateAssets = parallel(styles, adminStyles, vendorScripts, submitJS, adminJs, imgCompression);

// Set up dev environment
const dev = parallel(initBrowserSync, watchPaths);

exports.default = series(generateAssets, dev);
exports['generate-assets'] = generateAssets;
exports['dev'] = dev;
