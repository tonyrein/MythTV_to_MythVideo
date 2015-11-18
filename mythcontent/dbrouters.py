# Database routing classes

# Use the 'mythcopy' database for MythTV content; default for all else.

# for MythContent
class MythContentRouter(object):
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read MythContent models go to mythcopy.
        """
        if model._meta.app_label == 'mythcontent':
            return 'mythcopy'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write MythContent models go to mythcopy.
        """
        if model._meta.app_label == 'mythcontent':
            return 'mythcopy'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the MythContent app is involved.
        """
        if obj1._meta.app_label == 'mythcontent' or obj2._meta.app_label == 'mythcontent':
           return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        This is not a managed database -- do not allow migrations
        """
        return None
