var app = require('express').createServer();

app.configure(function(){
  app.set('views', __dirname + '/views');
  app.set('view engine', 'handlebars');
  app.set('view options', { layout: 'master' });
});

// GET / → Render with no template
app.get('/', function(req, res){
    res.send('Hello World!');
});

// GET /hb_hello → Render Lorem Ipsum with Handlebars template engine
app.get('/hb_hello', function(req, res){
    res.render('hello');
});

// TODO: ADD DB TEST

app.listen(8000);
console.log('Server running on port 8000.');
