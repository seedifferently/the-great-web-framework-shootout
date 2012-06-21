require 'rubygems'
require 'renee'
require 'sqlite3'

run Renee {
  get { halt "Hello World!" }
  path('/erb_hello').get { render! 'hellos' } 
  path('/erb_sql').get {
    db = SQLite3::Database.new("hello.db")
    @data = db.execute("select id, data from hello order by id asc")
    render! :hellodb, :locals => {:data => @data}
  }
}.setup {
  views_path 'views'
}
