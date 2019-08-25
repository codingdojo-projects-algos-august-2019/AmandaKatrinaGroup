from config import app
from controller_functions import index, register, login, logout, dashboard, check_email,\
    show_blog, show_blogs, show_blogs_by_tag, \
    delete_blog, edit_blog, create_blog, add_comment, delete_comment

app.add_url_rule('/', view_func=index)
app.add_url_rule('/register', view_func=register, methods=['POST'])
app.add_url_rule('/login', view_func=login, methods=['POST'])
app.add_url_rule('/logout', view_func=logout, methods=['POST'])
app.add_url_rule('/email', view_func=check_email, methods=['POST'])
app.add_url_rule('/dashboard', view_func=dashboard)
app.add_url_rule('/blogs', view_func=show_blogs)
app.add_url_rule('/blogs/search/<tag>', view_func=show_blogs_by_tag)
app.add_url_rule('/blogs/create', view_func=create_blog, methods=['GET', 'POST'])
app.add_url_rule('/blogs/<id>', view_func=show_blog)
app.add_url_rule('/blogs/<id>/comment/create', view_func=add_comment, methods=['POST'])
app.add_url_rule('/comments/<id>/delete', view_func=delete_comment)
app.add_url_rule('/blogs/<id>/edit', view_func=edit_blog, methods=['GET', 'POST'])
app.add_url_rule('/blogs/<id>/delete', view_func=delete_blog)
