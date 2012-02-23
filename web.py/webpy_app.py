import web
import model

urls = (
    '/', 'Index',
    '/hellos', 'Hellos',
    '/hellodb', 'Hellodb',
)

render = web.template.render('templates', base='base')

class Index:

	def GET(self):
		return 'Hello World!'

class Hellos:

	def GET(self):
		return render.hellos()

class Hellodb:

	def GET(self):
		rows = model.get_rows()
		return render.hellodb(rows)

app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()