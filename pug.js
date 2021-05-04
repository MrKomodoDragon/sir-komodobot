const pug = require('pug');

// Compile template.pug, and render a set of data
console.log(pug.renderFile('template.pug', {
  name: 'Timothy'
}));
