var app = require('express').createServer();

app.configure(function(){
    app.set('view engine', 'handlebars');
    app.set('view options', { layout: 'master' });
});

app.set('views', __dirname + '/');
app.set('view engine', 'handlebars');

app.get('/', function(req, res){
    res.send('Hello World!');
});

app.get('/hellos', function(req, res){
    res.render('hellos');
});

// TODO: ADD DB TEST

app.listen(8000);
console.log('Server running on port 8000.');
