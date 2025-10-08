class SingleObjectAdminMixin:
    def has_add_permission(self, request, obj=None):
        count = self.model().__class__.objects.count()
        return count < 1
