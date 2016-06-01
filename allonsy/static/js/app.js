$(document).foundation();

/* Disables Foundation hotkeys for accessibility , related to https://github.com/zurb/foundation-sites/issues/8011, otherwise messages that launch from the accordion + modal will not allow spaces in text */
Foundation.Keyboard.handleKey = function(){};