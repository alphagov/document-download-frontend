// JS Module used to combine all the JS modules used in the application into a single entry point,
// a bit like `app/__init__` in the Flask app.
//
// When processed by a bundler, this is turned into a Immediately Invoked Function Expression (IIFE)
// The IIFE format allows it to run in browsers that don't support JS Modules.
//
// Exported items will be added to the window.GOVUK namespace.
// For example, `export { Frontend }` will assign `Frontend` to `window.Frontend`
import { nodeListForEach } from 'govuk-frontend/govuk/common'
import Button from 'govuk-frontend/govuk/components/button/button'
import SkipLink from 'govuk-frontend/govuk/components/skip-link/skip-link'

// Copy of the initAll function from https://github.com/alphagov/govuk-frontend/blob/v3.5.0/src/govuk/all.js
// except it only includes, and initialises, the components used by this application.
function initAll (options) {
  // Set the options to an empty object by default if no options are passed.
  options = typeof options !== 'undefined' ? options : {}

  // Allow the user to initialise GOV.UK Frontend in only certain sections of the page
  // Defaults to the entire document if nothing is set.
  var scope = typeof options.scope !== 'undefined' ? options.scope : document

  // Find all buttons with [role=button] on the scope to enhance.
  var buttons = scope.querySelectorAll('[data-module="govuk-button"]')
  nodeListForEach(buttons, function (button) {
    new Button(button).init()
  });

  // There will only ever be one skip-link per page
  var skipLink = scope.querySelector('[data-module="govuk-skip-link"]')

  new SkipLink(skipLink).init()
}

var Frontend = {
  "Button": Button,
  "SkipLink": SkipLink,
  "initAll": initAll
}

export {
  Frontend
}
