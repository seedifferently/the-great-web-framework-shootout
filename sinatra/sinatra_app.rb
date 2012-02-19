require 'rubygems'
require 'sinatra'
require 'sqlite3'

get '/' do
    'Hello World!'
end

get '/erb_hello' do
    erb :hellos
end

get '/erb_sql' do
    db = SQLite3::Database.new("hello.db")
    @data = db.execute("select id, data from hello order by id asc")
    erb :hellodb
end
