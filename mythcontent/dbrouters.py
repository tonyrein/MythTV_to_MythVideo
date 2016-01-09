# Database routing classes


# for MythContent
class MythContentRouter(object):
    @staticmethod
    def model_db_name(model):
        try:
            db = model.db_name()
            if db is None or db == '':
                db = 'default'
        except AttributeError: # In case model does not define db_name
            db = 'default'
        return db
    """
    A router to control all database operations on models in the
    mythcontent application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read MythContent models go to mythcopy.
        Others to default. This is specified in the model's
        class definition in the class method db_name().
        """
        return MythContentRouter.model_db_name(model)
        
#         if model._meta.app_label == 'mythcontent':
#             return 'mythcopy'
#         return None

    def db_for_write(self, model, **hints):
        return MythContentRouter.model_db_name(model)
        """
        Attempts to write MythContent models go to mythcopy.
        """
#         if model._meta.app_label == 'mythcontent':
#             return 'mythcopy'
#         return None

#     def allow_relation(self, obj1, obj2, **hints):
#         """
#         Allow relations if a model in the MythContent app is involved.
#         """
#         if obj1._meta.app_label == 'mythcontent' or obj2._meta.app_label == 'mythcontent':
#            return True
#         return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Allow migrations for items in the default database, but not
        for items in mythcopy.
        """
        if db == 'mythcopy':
            return False
        return True
#         """
#         This is not a managed database -- do not allow migrations
#         """
#         return None
