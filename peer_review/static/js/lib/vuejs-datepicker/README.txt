TODO

This is extremely kludgey.  This library (https://github.com/charliekassel/vuejs-datepicker/) is intended to be
included as a CommonJS2 module, but since M-Write Peer Review doesn't use Webpack or any other loader (yet!!!)
I had to check out the project, change the webpack prod config to use the 'var' library type, build, and then
manually include here.  THIS NEEDS TO BE REDONE CORRECTLY once we have time to move to Webpack.

1. $ git clone https://github.com/charliekassel/vuejs-datepicker.git
2. $ cd vuejs-datepicker
3. modify output object of config in build/webpack.prod.conf.js to look like this:

   output: {
     path: config.build.assetsRoot,
     filename: 'build.js',
     library: 'Datepicker',
     libraryTarget: 'var'
   }

4. $ rm -rf dist ; webpack --bail --progress --hide-modules --config build/webpack.prod.conf.js
5. copy dist/* to project and include via <script> tag
