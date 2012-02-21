var path = require('path'),
    fs = require('fs'),
    Database = require('sqlite3').Database,
    db = new Database(path.join(__dirname, 'db', 'lipsum.sqlite3')),
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
  db.all("SELECT line FROM lipsum ORDER BY rowid ASC", function (err, data) {
    res.render('hello_db', {"lines": data.map(function (row) { return row.line; }) });
  });
});

// Database initialization
db.run("DROP TABLE lipsum", function (err) {
  db.run("CREATE TABLE lipsum (line TEXT)", function (err) {
    var lipsum = 'Lorem ipsum dolor sit amet, consecteteur adipiscing elit nisi ultricies. Condimentum vel, at augue nibh sed. Diam praesent metus ut eros, sem penatibus. Pellentesque. Fusce odio posuere litora non integer habitant proin. Metus accumsan nibh facilisis nostra lobortis cum diam tellus. Malesuada nostra a volutpat pede primis congue nisl feugiat in fermentum. Orci in hymenaeos. Eni tempus mi mollis lacinia orci interdum lacus. Sollicitudin aliquet, etiam. Ac. Mi, nullam ligula, tristique penatibus nisi eros nisl pede pharetra congue, aptent nulla, rhoncus tellus morbi, ornare. Magna condimentum erat turpis. Fusce arcu ve suscipit nisi phasellus rutrum a dictumst leo, laoreet dui, ultricies platea. Porta venenatis fringilla vestibulum arcu etiam condimentum non.';
    var stmt = db.prepare("INSERT INTO lipsum VALUES (?)");
    for (var i = 0; i < 5; i++) {
        stmt.run((i+1) + ": " + lipsum);
    }
    stmt.finalize();
  });
});

// Start server (in a ideal world, we'd wait for DB to finish its initialization, but let's make it more readable)
app.listen(8000);
console.log('Server running on port 8000.');
