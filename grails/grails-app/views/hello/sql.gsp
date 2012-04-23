<!doctype html>
<html>
	<head>
		<title>Hello World</title>
	</head>
	<body>
		<table>
			<g:each in="${hellos}" var="${hello}">
				<tr>
					<td>${hello.id}</td>
					<td>${hello.data}</td>
				</tr>
			</g:each>
		</table>
	</body>
</html>
