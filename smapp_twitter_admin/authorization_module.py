from smapp_twitter_admin import app
import smapp_twitter_admin.models as models

# from flask.ext.login import current_user
from smapp_twitter_admin.oauth_module import current_user
from flask.ext.principal import Principal, identity_loaded, Permission, RoleNeed, UserNeed
from collections import namedtuple
from functools import partial

principals = Principal(app)


TwitterCollectionNeed = namedtuple('blog_post', ['method', 'value'])
EditTwitterCollectionNeed = partial(TwitterCollectionNeed, 'edit')


admin_permission = Permission(RoleNeed('admin'))

class EditTwitterCollectionPermission(Permission):
    def __init__(self, post_id):
        need = EditTwitterCollectionNeed(unicode(post_id))
        super(EditTwitterCollectionPermission, self).__init__(need)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):

    # Set the identity user object
    identity.user = current_user()

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

    # Assuming the User model has a list of posts the user
    # has authored, add the needs to the identity
    if hasattr(current_user, 'posts'):
        for post in current_user.posts:
            identity.provides.add(EditTwitterCollectionNeed(unicode(post.id)))

    # Give the user the permissions
    if len(models.Permission.collections_for_user(current_user())) > 0:
        identity.provides.add(RoleNeed('admin'))

    for authorized_collection in models.Permission.collections_for_user(current_user()):
        identity.provides.add(EditTwitterCollectionNeed(unicode(authorized_collection)))
