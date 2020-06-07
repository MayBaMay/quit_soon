"use strict";

// Load plugins
const autoprefixer = require("gulp-autoprefixer");
const browsersync = require("browser-sync").create();
const cleanCSS = require("gulp-clean-css");
const del = require("del");
const gulp = require("gulp");
const header = require("gulp-header");
const merge = require("merge-stream");
const plumber = require("gulp-plumber");
const rename = require("gulp-rename");
const sass = require("gulp-sass");
const uglify = require("gulp-uglify");

// Load package.json for banner
const pkg = require("./package.json");

// Set the banner content
const banner = [
  "/*!\n",
  " * Start Bootstrap - <%= pkg.title %> v<%= pkg.version %> (<%= pkg.homepage %>)\n",
  " * Copyright 2013-" + new Date().getFullYear(),
  " <%= pkg.author %>\n",
  " * Licensed under <%= pkg.license %> (https://github.com/BlackrockDigital/<%= pkg.name %>/blob/master/LICENSE)\n",
  " */\n",
  "\n",
].join("");

// BrowserSync
function browserSync(done) {
  browsersync.init({
    // server: {
    //   baseDir: "./"
    // },
    port: 8000,
    proxy: "http://127.0.0.1:8000/",
  });
  done();
}

// BrowserSync reload
function browserSyncReload(done) {
  browsersync.reload();
  done();
}

// Clean vendor
function clean() {
  return del(["./QuitSoonApp/static/QuitSoonApp/vendor/"]);
}

// Bring third party dependencies from node_modules into vendor directory
function modules() {
  // Bootstrap JS
  var bootstrapJS = gulp
    .src("./node_modules/bootstrap/dist/js/*")
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/vendor/bootstrap/js"));
  // Bootstrap SCSS
  var bootstrapSCSS = gulp
    .src("./node_modules/bootstrap/scss/**/*")
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/vendor/bootstrap/scss"));
  // ChartJS
  var chartJS = gulp
    .src("./node_modules/chart.js/dist/*.js")
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/vendor/chart.js"));
  // dataTables
  var dataTables = gulp
    .src([
      "./node_modules/datatables.net/js/*.js",
      "./node_modules/datatables.net-bs4/js/*.js",
      "./node_modules/datatables.net-bs4/css/*.css",
    ])
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/vendor/datatables"));
  // Font Awesome
  var fontAwesome = gulp
    .src("./node_modules/@fortawesome/**/*")
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/vendor"));
  // jQuery Easing
  var jqueryEasing = gulp
    .src("./node_modules/jquery.easing/*.js")
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/vendor/jquery-easing"));
  // jQuery
  var jquery = gulp
    .src([
      "./node_modules/jquery/dist/*",
      "!./node_modules/jquery/dist/core.js",
    ])
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/vendor/jquery"));
  return merge(
    bootstrapJS,
    bootstrapSCSS,
    chartJS,
    dataTables,
    fontAwesome,
    jquery,
    jqueryEasing
  );
}

// CSS task
function css() {
  return gulp
    .src("./QuitSoonApp/static/QuitSoonApp/scss/**/*.scss")
    .pipe(plumber())
    .pipe(
      sass({
        outputStyle: "expanded",
        includePaths: "./node_modules",
      })
    )
    .on("error", sass.logError)
    .pipe(
      autoprefixer({
        cascade: false,
      })
    )
    .pipe(
      header(banner, {
        pkg: pkg,
      })
    )
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/css"))
    .pipe(
      rename({
        suffix: ".min",
      })
    )
    .pipe(cleanCSS())
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/css"))
    .pipe(browsersync.stream());
}

// JS task
function js() {
  return gulp
    .src([
      "./QuitSoonApp/static/QuitSoonApp/js/*.js",
      "!./QuitSoonApp/static/QuitSoonApp/js/*.min.js",
    ])
    .pipe(uglify())
    .pipe(
      header(banner, {
        pkg: pkg,
      })
    )
    .pipe(
      rename({
        suffix: ".min",
      })
    )
    .pipe(gulp.dest("./QuitSoonApp/static/QuitSoonApp/js"))
    .pipe(browsersync.stream());
}

// Watch files
function watchFiles() {
  gulp.watch("./QuitSoonApp/static/QuitSoonApp/scss/**/*", css);
  gulp.watch(
    ["./QuitSoonApp/static/QuitSoonApp/js/**/*", "!./js/**/*.min.js"],
    js
  );
  gulp.watch("./QuitSoonApp/static/QuitSoonApp/**/*.html", browserSyncReload);
}

// Define complex tasks
const vendor = gulp.series(clean, modules);
const build = gulp.series(vendor, gulp.parallel(css, js));
const watch = gulp.series(build, gulp.parallel(watchFiles, browserSync));

// Export tasks
exports.css = css;
exports.js = js;
exports.clean = clean;
exports.vendor = vendor;
exports.build = build;
exports.watch = watch;
exports.default = build;
