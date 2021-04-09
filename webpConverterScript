const imagemin = require('imagemin');
const imageminWebp = require('imagemin-webp');
const path = require('path');
var glob = require('glob');

glob('docs/assets/img/**/*.jpg', function(err, files) {
  files.forEach(element => {
    console.log(element);
    var c = imagemin([element], {
      destination: element.substring(0,element.lastIndexOf("/")+1),
      plugins: [imageminWebp({ quality: 70 })]
    });
    console.log(c);
  })
});

glob('docs/assets/img/**/*.png', function(err, files) {
  files.forEach(element => {
    console.log(element);
    var c = imagemin([element], {
      destination: element.substring(0,element.lastIndexOf("/")+1),
      plugins: [imageminWebp({ quality: 70 })]
    });
    console.log(c);
  })
});

