// JS Module used to combine all the JS modules used in the application into a single entry point,
// a bit like `app/__init__` in the Flask app.
//
// When processed by a bundler, this is turned into a Immediately Invoked Function Expression (IIFE)
// The IIFE format allows it to run in browsers that don't support JS Modules.
//
// Exported items will be added to the window.GOVUK namespace.
// For example, `export { Frontend }` will assign `Frontend` to `window.Frontend`
import { Button, ErrorSummary, SkipLink } from 'govuk-frontend'

// Copied from GOVUK Frontend manually as the 'govuk-frontend' package doesn't export it
//
// TODO: Ideally this would be a NodeList.prototype.forEach polyfill
// This seems to fail in IE8, requires more investigation.
// See: https://github.com/imagitama/nodelist-foreach-polyfill
//
function nodeListForEach (nodes, callback) {
  if (window.NodeList.prototype.forEach) {
    return nodes.forEach(callback)
  }
  for (var i = 0; i < nodes.length; i++) {
    callback.call(window, nodes[i], i, nodes);
  }
}

// Copy of the initAll function from https://github.com/alphagov/govuk-frontend/blob/v4.7.0/package/govuk-esm/common/index.mjs
// except it only includes, and initialises, the components used by this application.
function initAll (config) {
  // Set the config to an empty object by default if no config are passed.
  config = typeof config !== 'undefined' ? config : {}

  // Allow the user to initialise GOV.UK Frontend in only certain sections of the page
  // Defaults to the entire document if nothing is set.
  var $scope = config.scope instanceof HTMLElement ? config.scope : document;

  var $buttons = $scope.querySelectorAll('[data-module="govuk-button"]')
  nodeListForEach($buttons, function ($button) {
    new Button($button, config.button).init()
  })

  // Find first error summary module to enhance.
  var $errorSummary = $scope.querySelector('[data-module="govuk-error-summary"]')
  if ($errorSummary) {
    new ErrorSummary($errorSummary, config.errorSummary).init()
  }

  // Find first skip link module to enhance.
  var $skipLink = $scope.querySelector('[data-module="govuk-skip-link"]')
  if ($skipLink) {
    new SkipLink($skipLink).init()
  }
}

var Frontend = {
  "Button": Button,
  "ErrorSummary": ErrorSummary,
  "SkipLink": SkipLink,
  "initAll": initAll
}

export {
  Frontend
}
