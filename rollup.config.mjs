import { nodeResolve } from '@rollup/plugin-node-resolve';
import terser from '@rollup/plugin-terser';
import copy from 'rollup-plugin-copy';
import styles from "rollup-plugin-styler";

// toggle to enable rebrand styles
const enableRebrand = true;
const paths = {
  src: 'app/assets/',
  dist: 'app/static/',
  npm: 'node_modules/',
  govuk_frontend: 'node_modules/govuk-frontend/dist/govuk/',
};
// separate path config for govuk-frontend assets, so we can manage rebrand paths easily
const govukFrontendAssetPaths = {
  images: `${paths.govuk_frontend}assets/${enableRebrand ? 'rebrand/': ''}images/**/*`,
  fonts: `${paths.govuk_frontend}assets/fonts/**/*`,
  manifest: `${paths.govuk_frontend}assets/${enableRebrand ? 'rebrand/': ''}manifest.json`,
};

export default [
  // ESM compilation and copy static assets
  {
    input: paths.src + 'javascripts/main.mjs',
    output: {
      dir: paths.dist + 'javascripts/',
      entryFileNames: 'main.js',
      format: 'es',
      sourcemap: true
    },
    plugins: [
      nodeResolve(),
      terser(),
      // copy images, error pages and govuk-frontend static assets
      copy({
        targets: [
          { src: paths.src + 'images/**/*', dest: paths.dist + 'images/' },
          { src: govukFrontendAssetPaths.images, dest: paths.dist + 'images/' },
          { src: govukFrontendAssetPaths.fonts, dest: paths.dist + 'fonts/' },
          { src: govukFrontendAssetPaths.manifest, dest: paths.dist }
        ]
      }),
    ]
  },
  // SCSS compilation
  {
    input: paths.src + 'stylesheets/main.scss',
    output: {
      dir: paths.dist + 'stylesheets/',
      assetFileNames: "[name][extname]",
    },
    plugins: [
      // https://anidetrix.github.io/rollup-plugin-styles/interfaces/types.Options.html
      styles({
        mode: "extract",
        sass: {
          includePaths: [
            paths.govuk_frontend,
            paths.npm
          ],
          silenceDeprecations: [
            "mixed-decls",
            "global-builtin",
            "color-functions",
            "slash-div",
            "import"
          ],
        },
        minimize: true,
        url: false,
        sourceMap: true,
      }),
    ]
  }
];
