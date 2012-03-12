var path = require('path'),
    Database = require('sqlite3').Database,
    db = new Database(path.join(__dirname, 'hello.db')),
    app = require('express').createServer();

// View configuration
app.configure(function () {
  app.set('views', __dirname + '/views');
  app.set('view engine', 'handlebars');
  app.set('view options', { layout: 'master' });
});

// GET / → Render with no template
app.get('/', function (req, res) {
    res.send('Hello World!');
});

// GET /hb_hello → Render Lorem Ipsum with Handlebars template engine
app.get('/hb_hello', function (req, res) {
    res.render('hello');
});

// GET /hb_sql → Render SQLite contents (still with Handlebars)
app.get('/hb_sql', function (req, res) {
  db.all("SELECT id, data FROM hello ORDER BY id ASC", function (err, data) {
    res.render('hello_db', {"hello": data });
  });
});

// Start server (in a ideal world, we'd wait for DB to finish its
// initialization, but let's make it more readable)
app.listen(8000);
console.log('Server running on port 8000.');
