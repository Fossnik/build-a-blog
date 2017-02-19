import webapp2
import os
import jinja2 # Template engine specific to GAE -> Use Python to build HTML

from google.appengine.ext import db

# Concatenates the path containing this '.py' with 'templates' to establish
# the location of our templates subdirectory as a jinja2 environment object.
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
				 				autoescape = True)

class Handler(webapp2.RequestHandler):
	# "self.write()" subsumes "self.response.out.write()"
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		# Load a template file from jinja & store in "template_as_string"
		template_as_string = jinja_env.get_template(template)
		# Use "params" for variable subst. within the "template_as_string"
		return template_as_string.render(params)

	# Same as render_str, but instead of returning string, outputs it.
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

# Root page - Just a link to /blog
class MainPage(Handler):
	def get(self):
		self.write('<a href="/blog">blog</a>')

# Store a blog entry "Post" in Google DB as an object with properties.
class Post(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

# Renders the default page where up to 5 blogs can be seen.
class BlogFront(Handler):
	def render_front(self):
		# Creates a cursor for all of the posts.
		posts = db.GqlQuery("SELECT * FROM Post "
							"ORDER BY created DESC limit 5") # limit to 5
		self.render("mainblog.html", posts=posts)

	def get(self):
		self.render_front()

# Renders a page where a new post can be created.
class NewPost(Handler):
	def render_newpost(self, title="", content="", error=""):
		self.render("newpost.html", title=title, content=content, error=error)

	def get(self):
		self.render_newpost()

	def post(self):
		title = self.request.get("title") # Pulls "title" from the URL
		content = self.request.get("content")

		if title and content:
			a = Post(title = title, content = content)
			a.put() # Puts our new "Post" object in the DB
			self.redirect("/blog")
		else:
			error = "Both Title and Content are Required!"
			self.render_newpost(title, content, error)
			return

"""
# This is for the permalinks rendering single blog posts.
class ViewPostHandler(webapp2.RequestHandler):
	def get(self, id):
		key = Post.get_by_id(int(id))
		if key:
			BlogFront.render("mainblog.html", posts=key)
		else:
			self.response.write('Regretably, %s is not a valid ID' % id)
			return

"""

app = webapp2.WSGIApplication([('/', MainPage),
								('/blog/?', BlogFront),
								('/newpost', NewPost),
					#			webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
								],debug=True)
