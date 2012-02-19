var express = require('express')
    , app = express.createServer()

app.configure(function(){
    app.set('view engine', 'handlebars')
    app.set("view options", { layout: false }) 
})
app.set('views', __dirname + '/')
app.register('.html', require('handlebars'))

app.get('/', function(req, res){
    res.render('index.html', { title: 'Hello World' })
})

app.listen(8000)
console.log('Server running.')
